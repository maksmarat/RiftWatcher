from __future__ import annotations

import json
from typing import Any

from db.database import Database
from utils.storage import load_players


class MatchesRepository:
    def __init__(self, db: Database):
        self.db = db

    async def match_exists(self, match_id: str) -> bool:
        row = await self.db.fetchone(
            "SELECT 1 FROM matches WHERE match_id = ?",
            (match_id,),
        )
        return row is not None

    async def insert_match(self, match_data: dict[str, Any]) -> None:
        info = match_data["info"]

        await self.db.execute(
            """
            INSERT OR IGNORE INTO matches (
                match_id,
                game_start,
                game_duration,
                queue_id,
                map_id,
                raw_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                match_data["metadata"]["matchId"],
                info.get("gameStartTimestamp"),
                info.get("gameDuration"),
                info.get("queueId"),
                info.get("mapId"),
                json.dumps(match_data, ensure_ascii=False),
            ),
        )

    async def get_match_json(self, match_id: str):
        row = await self.db.fetchone(
            "SELECT raw_json FROM matches WHERE match_id = ?",
            (match_id,),
        )

        if not row or not row["raw_json"]:
            return None

        return json.loads(row["raw_json"])
    
    async def upsert_tracked_participants(self, match_data: dict[str, Any]) -> None:
        tracked_puuids = set(load_players())
        participants = match_data.get("info", {}).get("participants", [])

        params = []

        for p in participants:
            puuid = p.get("puuid")
            if puuid not in tracked_puuids:
                continue

            params.append(
                (
                    puuid,
                    p.get("riotIdGameName"),
                    p.get("riotIdTagline"),
                )
            )

        if not params:
            return

        await self.db.executemany(
            """
            INSERT INTO players (puuid, game_name, tag_line, is_active)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(puuid) DO UPDATE SET
                game_name = excluded.game_name,
                tag_line = excluded.tag_line,
                is_active = 1
            """,
            params,
        )

    async def get_all_matches_json(self) -> list[dict]:
        rows = await self.db.fetchall(
            """
            SELECT raw_json
            FROM matches
            WHERE raw_json IS NOT NULL
            ORDER BY game_start DESC
            """
        )

        result = []
        for row in rows:
            raw_json = row["raw_json"]
            if not raw_json:
                continue

            try:
                result.append(json.loads(raw_json))
            except Exception:
                pass

        return result

    async def insert_player_match_stats_for_puuid(
        self,
        match_data: dict[str, Any],
        puuid: str,
    ) -> None:
        match_id = match_data["metadata"]["matchId"]
        participants = match_data.get("info", {}).get("participants", [])

        target_player = next(
            (participant for participant in participants if participant.get("puuid") == puuid),
            None,
        )
        if target_player is None:
            return

        cs = target_player.get("totalMinionsKilled", 0) + target_player.get("neutralMinionsKilled", 0)
        riot_id = (
            f"{target_player.get('riotIdGameName', 'Unknown')}"
            f"#{target_player.get('riotIdTagline', 'Unknown')}"
        )

        await self.db.execute(
            """
            INSERT OR IGNORE INTO player_match_stats (
                match_id,
                puuid,
                riot_id,
                champion_name,
                kills,
                deaths,
                assists,
                win,
                team_id,
                damage_per_minute,
                cs,
                gold_earned
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match_id,
                puuid,
                riot_id,
                target_player.get("championName"),
                target_player.get("kills", 0),
                target_player.get("deaths", 0),
                target_player.get("assists", 0),
                1 if target_player.get("win") else 0,
                target_player.get("teamId"),
                target_player.get("challenges", {}).get("damagePerMinute", 0),
                cs,
                target_player.get("goldEarned", 0),
            ),
        )

    async def insert_tracked_player_match_stats(self, match_data: dict[str, Any]) -> None:
        tracked_puuids = set(load_players())
        match_id = match_data["metadata"]["matchId"]
        participants = match_data.get("info", {}).get("participants", [])

        params_list: list[tuple] = []

        for p in participants:
            puuid = p.get("puuid")
            if puuid not in tracked_puuids:
                continue

            riot_id = f"{p.get('riotIdGameName', 'Unknown')}#{p.get('riotIdTagline', 'Unknown')}"
            cs = p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0)

            params_list.append(
                (
                    match_id,
                    puuid,
                    riot_id,
                    p.get("championName"),
                    p.get("kills", 0),
                    p.get("deaths", 0),
                    p.get("assists", 0),
                    1 if p.get("win") else 0,
                    p.get("teamId"),
                    p.get("challenges", {}).get("damagePerMinute", 0),
                    cs,
                    p.get("goldEarned", 0),
                )
            )

        if not params_list:
            return

        await self.db.executemany(
            """
            INSERT OR IGNORE INTO player_match_stats (
                match_id,
                puuid,
                riot_id,
                champion_name,
                kills,
                deaths,
                assists,
                win,
                team_id,
                damage_per_minute,
                cs,
                gold_earned
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            params_list,
        )

    async def save_full_match(self, match_data: dict[str, Any]) -> None:
        await self.insert_match(match_data)
        await self.upsert_tracked_participants(match_data)
        await self.insert_tracked_player_match_stats(match_data)

    async def get_recent_matches_for_player(self, puuid: str, limit: int | None = 5):
        query = """
            SELECT
                pms.match_id,
                pms.riot_id,
                pms.champion_name,
                pms.kills,
                pms.deaths,
                pms.assists,
                pms.win,
                pms.team_id,
                pms.damage_per_minute,
                pms.cs,
                pms.gold_earned,
                m.game_start,
                m.game_duration,
                m.queue_id,
                m.map_id
            FROM player_match_stats pms
            JOIN matches m ON m.match_id = pms.match_id
            WHERE pms.puuid = ?
            ORDER BY m.game_start DESC
        """
        params: list[Any] = [puuid]

        if limit is not None:
            query += "\n            LIMIT ?"
            params.append(limit)

        return await self.db.fetchall(query, tuple(params))

    async def get_match_stats_for_tracked_players(self, match_id: str):
        return await self.db.fetchall(
            """
            SELECT
                pms.match_id,
                pms.puuid,
                pms.riot_id,
                pms.champion_name,
                pms.kills,
                pms.deaths,
                pms.assists,
                pms.win,
                pms.team_id,
                pms.damage_per_minute,
                pms.cs,
                pms.gold_earned
            FROM player_match_stats pms
            WHERE pms.match_id = ?
            ORDER BY pms.team_id, pms.riot_id
            """,
            (match_id,),
        )
