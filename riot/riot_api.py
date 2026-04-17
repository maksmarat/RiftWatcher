import asyncio
from datetime import datetime
from time import monotonic

import aiohttp


class RiotAPI:
    RANKED_CACHE_TTL_SECONDS = 300

    def __init__(
        self,
        api_key: str,
        region: str = "europe",
        platform_region: str = "ru",
    ):
        self.api_key = api_key
        self.region = region
        self.platform_region = platform_region

        self.base_url = f"https://{region}.api.riotgames.com"
        self.platform_base_url = f"https://{platform_region}.api.riotgames.com"
        self.headers = {"X-Riot-Token": self.api_key}

        self.session: aiohttp.ClientSession | None = None
        self.ranked_entries_cache: dict[str, tuple[float, list[dict]]] = {}

    # --------------------------
    # 🔧 SESSION INIT
    # --------------------------
    async def init(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    # --------------------------
    # 🔧 GENERIC REQUEST
    # --------------------------
    async def request(self, url, params=None):
        await self.init()
        async with self.session.get(url, params=params) as resp:
            if resp.status == 200:
                return await resp.json()

            print(f"Riot API error {resp.status}: {await resp.text()}")
            return None

    # --------------------------
    # 👤 PUUID
    # --------------------------
    async def get_puuid(self, game_name, tag_line):
        url = (
            f"{self.base_url}/riot/account/v1/accounts/"
            f"by-riot-id/{game_name}/{tag_line}"
        )

        data = await self.request(url)
        return data["puuid"] if data else None

    async def get_summoner_data(self, puuid):
        url = f"{self.base_url}/riot/account/v1/accounts/by-puuid/{puuid}"
        return await self.request(url)
    # --------------------------
    # 🎮 MATCH IDS
    # --------------------------
    async def get_recent_matches(self, puuid, count=5):
        url = f"{self.base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids"

        data = await self.request(url, params={"count": count})
        return data or []

    # --------------------------
    # 👀 MATCH DETAILS
    # --------------------------
    async def get_match_details(self, match_id):
        url = f"{self.base_url}/lol/match/v5/matches/{match_id}"
        return await self.request(url)

    async def get_ranked_entries(self, puuid: str, force_refresh: bool = False):
        cache_entry = self.ranked_entries_cache.get(puuid)
        now = monotonic()

        if (
            not force_refresh
            and cache_entry is not None
            and now - cache_entry[0] < self.RANKED_CACHE_TTL_SECONDS
        ):
            return cache_entry[1]

        url = f"{self.platform_base_url}/lol/league/v4/entries/by-puuid/{puuid}"
        data = await self.request(url)

        if data is None:
            return []

        self.ranked_entries_cache[puuid] = (now, data)
        return data

    async def get_ranked_entries_for_puuids(self, puuids: list[str]) -> dict[str, list[dict]]:
        unique_puuids: list[str] = []
        seen: set[str] = set()

        for puuid in puuids:
            if not puuid or puuid in seen:
                continue
            seen.add(puuid)
            unique_puuids.append(puuid)

        ranked_entries_list = await asyncio.gather(
            *(self.get_ranked_entries(puuid) for puuid in unique_puuids),
            return_exceptions=True,
        )

        result: dict[str, list[dict]] = {}
        for puuid, ranked_entries in zip(unique_puuids, ranked_entries_list):
            if isinstance(ranked_entries, Exception):
                print(f"Riot API ranked entries error for {puuid}: {ranked_entries!r}")
                result[puuid] = []
            else:
                result[puuid] = ranked_entries or []

        return result

    # --------------------------
    # 📊 FORMAT MATCH
    # --------------------------
    async def get_formatted_match_stats(self, match_id, target_puuid=None):
        match_data = await self.get_match_details(match_id)

        if not match_data:
            return None, None

        participants = match_data["info"]["participants"]
        puuids = match_data["metadata"]["participants"]

        match_time = datetime.fromtimestamp(
            match_data["info"]["gameStartTimestamp"] / 1000
        )

        result = []

        for i, p in enumerate(participants):
            result.append(self.build_player_row(
                p,
                is_target=(target_puuid == puuids[i])
            ))

        return result, match_time

    # --------------------------
    # 🧾 PLAYER ROW
    # --------------------------
    def build_player_row(self, p, is_target=False):
        return {
            "nickname": f"{p['riotIdGameName']}#{p['riotIdTagline']}",
            "champion": p["championName"],
            "kills": p["kills"],
            "deaths": p["deaths"],
            "assists": p["assists"],
            "dpm": p.get("challenges", {}).get("damagePerMinute", 0),
            "cs": p["totalMinionsKilled"] + p["neutralMinionsKilled"],
            "gold": p["goldEarned"],
            "win": p["win"],
            "team": p["teamId"],
            "is_target": is_target
        }

    # --------------------------
    # 📊 MAIN STATS FUNCTION
    # --------------------------
    async def get_player_stats(self, game_name, tag_line, match_count):
        puuid = await self.get_puuid(game_name, tag_line)

        if not puuid:
            return f"Игрок {game_name}#{tag_line} не найден"

        matches = await self.get_recent_matches(puuid, match_count)

        if not matches:
            return f"Нет матчей для {game_name}#{tag_line}"

        all_stats = []

        for match_id in matches:
            stats, match_time = await self.get_formatted_match_stats(
                match_id,
                puuid
            )

            all_stats.append({
                "match_id": match_id,
                "stats": stats,
                "match_time": match_time
            })

        return all_stats

    # --------------------------
    # 🧠 SPECTATOR
    # --------------------------
    async def is_player_in_game_by_puuid(self, puuid):
        url = f"https://ru.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"

        data = await self.request(url)

        if data:
            return True, data
        return False, None

    # --------------------------
    # 🧹 CLEANUP (ВАЖНО)
    # --------------------------
    async def close(self):
        if self.session:
            await self.session.close()
