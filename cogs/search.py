from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from db.repositories.matches_repository import MatchesRepository
from db.repositories.players_repository import PlayersRepository
from utils.helpers import format_match_age, get_queue_display_name, parse_riot_id


@dataclass(slots=True)
class PlayerIdentity:
    puuid: str
    riot_id: str
    game_name: str
    tag_line: str


@dataclass(slots=True)
class PlayerMatch:
    match_number: int
    match_id: str
    match_data: dict[str, Any]


@dataclass(slots=True)
class SearchResult:
    match_number: int
    match_id: str
    match_data: dict[str, Any]
    summary_lines: list[str]
    highlight_puuids: set[str]


class SearchPaginatorView(discord.ui.View):
    def __init__(
        self,
        author_id: int,
        base_player: PlayerIdentity,
        results: list[SearchResult],
        timeout: float = 180,
    ):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.base_player = base_player
        self.results = results
        self.page = 0
        self.total_pages = max(1, len(results))

        self._update_buttons()

    def _update_buttons(self) -> None:
        self.prev_button.disabled = self.page <= 0
        self.next_button.disabled = self.page >= self.total_pages - 1

    @staticmethod
    def build_player_name(participant: dict[str, Any]) -> str:
        game_name = participant.get("riotIdGameName") or participant.get("summonerName") or "Unknown"
        tag_line = participant.get("riotIdTagline")
        return f"{game_name}#{tag_line}" if tag_line else game_name

    @staticmethod
    def format_duration(duration_seconds: int | None) -> str:
        duration = int(duration_seconds or 0)
        minutes = duration // 60
        seconds = duration % 60
        return f"{minutes}:{seconds:02d}"

    def format_team(
        self,
        team: list[dict[str, Any]],
        target_puuid: str,
        highlight_puuids: set[str],
    ) -> str:
        if not team:
            return "Нет данных"

        lines: list[str] = []

        for player in team:
            player_puuid = player.get("puuid")
            if player_puuid == target_puuid:
                marker = "🎯 "
            elif player_puuid in highlight_puuids:
                marker = "🔎 "
            else:
                marker = ""

            riot_name = self.build_player_name(player)
            champion = player.get("championName", "Unknown")
            kills = int(player.get("kills", 0) or 0)
            deaths = int(player.get("deaths", 0) or 0)
            assists = int(player.get("assists", 0) or 0)
            cs = int(player.get("totalMinionsKilled", 0) or 0) + int(player.get("neutralMinionsKilled", 0) or 0)
            gold = int(player.get("goldEarned", 0) or 0)
            dpm = float(player.get("challenges", {}).get("damagePerMinute", 0) or 0)

            lines.append(
                f"{marker}**{riot_name[:24]}**\n"
                f"{champion} | {kills}/{deaths}/{assists}\n"
                f"{dpm:.0f} DPM | CS {cs} | Gold {gold}\n"
            )

        text = "\n".join(lines)
        if len(text) > 1024:
            text = text[:1021] + "..."

        return text

    def _build_embed(self) -> discord.Embed:
        result = self.results[self.page]
        info = result.match_data.get("info", {})
        participants = info.get("participants", [])

        blue_team = [player for player in participants if player.get("teamId") == 100]
        red_team = [player for player in participants if player.get("teamId") == 200]
        target_player = next(
            (player for player in participants if player.get("puuid") == self.base_player.puuid),
            None,
        )

        description_lines = [
            f"**Матч №:** `{result.match_number}`",
            f"**ID:** `{result.match_id}`",
            f"**Тип:** {get_queue_display_name(info.get('queueId'))}",
            f"**Сыгран** {format_match_age(info.get('gameStartTimestamp'))}",
            f"**Длительность:** {self.format_duration(info.get('gameDuration'))}",
            "",
            *result.summary_lines,
        ]

        embed = discord.Embed(
            title=f"🔎 Search Results — {self.base_player.riot_id}",
            description="\n".join(description_lines),
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name=f"{'✅' if blue_team and blue_team[0].get('win') else '❌'} Blue Team",
            value=self.format_team(blue_team, self.base_player.puuid, result.highlight_puuids),
            inline=True,
        )
        embed.add_field(
            name=f"{'✅' if red_team and red_team[0].get('win') else '❌'} Red Team",
            value=self.format_team(red_team, self.base_player.puuid, result.highlight_puuids),
            inline=True,
        )

        if target_player is not None:
            target_kills = int(target_player.get("kills", 0) or 0)
            target_deaths = int(target_player.get("deaths", 0) or 0)
            target_assists = int(target_player.get("assists", 0) or 0)
            target_champion = target_player.get("championName", "Unknown")
            if target_deaths == 0:
                kda = target_kills + target_assists
            else:
                kda = (target_kills + target_assists) / target_deaths

            footer_text = (
                f"Страница {self.page + 1}/{self.total_pages} • "
                f"{self.base_player.riot_id} • {target_champion} "
                f"{target_kills}/{target_deaths}/{target_assists} KDA {kda:.2f}"
            )
        else:
            footer_text = f"Страница {self.page + 1}/{self.total_pages} • CCG Bot"

        embed.set_footer(text=footer_text)
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ Эти кнопки доступны только тому, кто вызвал команду.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self._build_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self._build_embed(), view=self)


class Search(commands.Cog):
    MAX_SYNC_MATCHES = 100

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players_repo = PlayersRepository(bot.db)
        self.matches_repo = MatchesRepository(bot.db)

    @staticmethod
    def normalize_text(value: str) -> str:
        return "".join(char for char in value.casefold() if char.isalnum())

    def get_champion_names(self) -> list[str]:
        champions = getattr(self.bot, "champions", {}) or {}
        return sorted(set(champions.values()))

    def resolve_champion_name(self, raw_name: str) -> str | None:
        champions = self.get_champion_names()
        if not champions:
            return None

        normalized_query = self.normalize_text(raw_name)
        if not normalized_query:
            return None

        exact_match = next(
            (name for name in champions if self.normalize_text(name) == normalized_query),
            None,
        )
        if exact_match is not None:
            return exact_match

        partial_matches = [
            name for name in champions
            if normalized_query in self.normalize_text(name)
        ]
        if len(partial_matches) == 1:
            return partial_matches[0]

        return None

    async def resolve_player_identity(self, nickname: str) -> PlayerIdentity | None:
        game_name, tag_line = parse_riot_id(nickname)
        if not game_name or not tag_line:
            return None

        puuid = await self.bot.riot_api.get_puuid(game_name, tag_line)
        if not puuid:
            return None

        await self.players_repo.upsert_player(
            puuid=puuid,
            game_name=game_name,
            tag_line=tag_line,
        )
        return PlayerIdentity(
            puuid=puuid,
            riot_id=f"{game_name}#{tag_line}",
            game_name=game_name,
            tag_line=tag_line,
        )

    async def sync_recent_matches(self, puuid: str, count: int | None = None) -> tuple[list[str], int]:
        match_count = count or self.MAX_SYNC_MATCHES
        recent_match_ids = await self.bot.riot_api.get_recent_matches(puuid, count=match_count)
        if not recent_match_ids:
            return [], 0

        synced_count = 0

        for match_id in recent_match_ids:
            exists = await self.matches_repo.match_exists(match_id)
            if exists:
                match_data = await self.matches_repo.get_match_json(match_id)
                if match_data:
                    await self.matches_repo.insert_player_match_stats_for_puuid(match_data, puuid)
                    continue

            match_data = await self.bot.riot_api.get_match_details(match_id)
            if not match_data:
                continue

            await self.matches_repo.save_full_match(match_data)
            await self.matches_repo.insert_player_match_stats_for_puuid(match_data, puuid)
            synced_count += 1

        return recent_match_ids, synced_count

    async def get_matches_for_player(self, puuid: str) -> list[PlayerMatch]:
        all_matches = await self.matches_repo.get_all_matches_json()
        player_matches: list[PlayerMatch] = []
        match_number = 0

        for match_data in all_matches:
            participants = match_data.get("info", {}).get("participants", [])
            if not any(player.get("puuid") == puuid for player in participants):
                continue

            metadata = match_data.get("metadata", {})
            match_number += 1
            player_matches.append(
                PlayerMatch(
                    match_number=match_number,
                    match_id=metadata.get("matchId", "Unknown"),
                    match_data=match_data,
                )
            )

        return player_matches

    def build_champion_results(
        self,
        base_player: PlayerIdentity,
        player_matches: list[PlayerMatch],
        champion_name: str,
    ) -> list[SearchResult]:
        normalized_champion = self.normalize_text(champion_name)
        results: list[SearchResult] = []

        for match in player_matches:
            participants = match.match_data.get("info", {}).get("participants", [])
            target_player = next(
                (player for player in participants if player.get("puuid") == base_player.puuid),
                None,
            )
            if target_player is None:
                continue

            matching_participants = [
                player for player in participants
                if self.normalize_text(player.get("championName", "")) == normalized_champion
            ]
            if not matching_participants:
                continue

            player_used_champion = (
                self.normalize_text(target_player.get("championName", "")) == normalized_champion
            )

            champion_players = ", ".join(
                self.build_player_name(player) for player in matching_participants
            )
            highlight_puuids = {
                player.get("puuid")
                for player in matching_participants
                if player.get("puuid") and player.get("puuid") != base_player.puuid
            }

            results.append(
                SearchResult(
                    match_number=match.match_number,
                    match_id=match.match_id,
                    match_data=match.match_data,
                    summary_lines=[
                        f"**Поиск по чемпиону:** `{champion_name}`",
                        f"**{base_player.riot_id} играл на нём:** {'Да' if player_used_champion else 'Нет'}",
                        f"**Кто играл на {champion_name}:** {champion_players}",
                    ],
                    highlight_puuids=highlight_puuids,
                )
            )

        return results

    def build_shared_match_results(
        self,
        base_player: PlayerIdentity,
        teammates: list[PlayerIdentity],
        player_matches: list[PlayerMatch],
    ) -> list[SearchResult]:
        teammate_puuids = {player.puuid for player in teammates}
        results: list[SearchResult] = []

        for match in player_matches:
            participants = match.match_data.get("info", {}).get("participants", [])
            participants_by_puuid = {
                player.get("puuid"): player
                for player in participants
                if player.get("puuid")
            }

            base_participant = participants_by_puuid.get(base_player.puuid)
            if base_participant is None:
                continue

            if not teammate_puuids.issubset(participants_by_puuid):
                continue

            base_team_id = base_participant.get("teamId")
            if any(participants_by_puuid[player.puuid].get("teamId") != base_team_id for player in teammates):
                continue

            results.append(
                SearchResult(
                    match_number=match.match_number,
                    match_id=match.match_id,
                    match_data=match.match_data,
                    summary_lines=[
                        f"**С игроками:** {', '.join(player.riot_id for player in teammates)}",
                    ],
                    highlight_puuids=teammate_puuids,
                )
            )

        return results

    @staticmethod
    def build_player_name(participant: dict[str, Any]) -> str:
        return SearchPaginatorView.build_player_name(participant)

    def build_sync_summary(
        self,
        recent_match_count: int,
        synced_count: int,
        player_match_count: int,
        result_count: int,
    ) -> str:
        
        return (
            f"Матчей игрока найдено: **{player_match_count}**\n"
            f"Совпадений по поиску: **{result_count}**"
        )

    def build_shared_players_summary(
        self,
        base_player: PlayerIdentity,
        teammates: list[PlayerIdentity],
        results: list[SearchResult],
    ) -> str:
        tracked_players = [base_player, *teammates]
        stats = {
            player.puuid: {
                "riot_id": player.riot_id,
                "games": 0,
                "wins": 0,
                "kda_sum": 0.0,
            }
            for player in tracked_players
        }

        total_games = len(results)
        team_wins = 0

        for result in results:
            participants = result.match_data.get("info", {}).get("participants", [])
            participants_by_puuid = {
                player.get("puuid"): player
                for player in participants
                if player.get("puuid")
            }

            base_participant = participants_by_puuid.get(base_player.puuid)
            if base_participant and base_participant.get("win"):
                team_wins += 1

            for player in tracked_players:
                participant = participants_by_puuid.get(player.puuid)
                if participant is None:
                    continue

                kills = int(participant.get("kills", 0) or 0)
                deaths = int(participant.get("deaths", 0) or 0)
                assists = int(participant.get("assists", 0) or 0)
                kda = kills + assists if deaths == 0 else (kills + assists) / deaths

                stats[player.puuid]["games"] += 1
                stats[player.puuid]["wins"] += 1 if participant.get("win") else 0
                stats[player.puuid]["kda_sum"] += kda

        lines = [
            f"WR общих игр: **{(team_wins / total_games) * 100:.1f}%** ({team_wins}/{total_games})",
        ]

        culprit_name = base_player.riot_id
        culprit_kda = float("inf")

        for player in tracked_players:
            player_stats = stats[player.puuid]
            games = player_stats["games"]
            avg_kda = player_stats["kda_sum"] / games if games else 0.0

            if avg_kda < culprit_kda:
                culprit_kda = avg_kda
                culprit_name = player.riot_id

        lines.append(f"Виновный в поражениях - **{culprit_name}**")
        return "\n".join(lines)

    @app_commands.command(
        name="search",
        description="Поиск матчей игрока по чемпиону или по совместным играм с другими игроками",
    )
    @app_commands.describe(
        nickname="Основной игрок в формате gameName#tagLine",
        character_name="Имя чемпиона, например Darius",
        nickname_2="Второй игрок для поиска совместных матчей",
        nickname_3="Третий игрок для поиска совместных матчей",
        nickname_4="Четвёртый игрок для поиска совместных матчей",
        nickname_5="Пятый игрок для поиска совместных матчей",
    )
    async def search(
        self,
        interaction: discord.Interaction,
        nickname: str,
        character_name: str | None = None,
        nickname_2: str | None = None,
        nickname_3: str | None = None,
        nickname_4: str | None = None,
        nickname_5: str | None = None,
    ):
        extra_nicknames = [
            value.strip() for value in (nickname_2, nickname_3, nickname_4, nickname_5)
            if value and value.strip()
        ]

        if character_name and extra_nicknames:
            await interaction.response.send_message(
                "❌ Используй `/search` либо с `character_name`, либо с дополнительными никами игроков.",
                ephemeral=True,
            )
            return

        if not character_name and not extra_nicknames:
            await interaction.response.send_message(
                "❌ Укажи либо `character_name`, либо хотя бы одного дополнительного игрока.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        try:
            base_player = await self.resolve_player_identity(nickname)
            if base_player is None:
                await interaction.followup.send(
                    f"❌ Игрок {nickname} не найден или ник указан не в формате `name#tag`.",
                )
                return

            recent_match_ids, synced_count = await self.sync_recent_matches(base_player.puuid)
            if not recent_match_ids:
                await interaction.followup.send(
                    f"⚠️ Для {base_player.riot_id} не найдено матчей.",
                )
                return

            player_matches = await self.get_matches_for_player(base_player.puuid)
            if not player_matches:
                await interaction.followup.send(
                    "⚠️ Матчи игрока не удалось загрузить из БД.",
                )
                return

            if character_name:
                champion_name = self.resolve_champion_name(character_name)
                if champion_name is None:
                    await interaction.followup.send(
                        f"❌ Чемпион `{character_name}` не найден. Начни вводить имя и выбери вариант из списка.",
                    )
                    return

                results = self.build_champion_results(
                    base_player=base_player,
                    player_matches=player_matches,
                    champion_name=champion_name,
                )

                if not results:
                    await interaction.followup.send(
                        self.build_sync_summary(
                            recent_match_count=len(recent_match_ids),
                            synced_count=synced_count,
                            player_match_count=len(player_matches),
                            result_count=0,
                        )
                        + f"\nСовпадений по чемпиону **{champion_name}** не найдено.",
                    )
                    return
            else:
                teammate_identities: list[PlayerIdentity] = []
                seen_puuids = {base_player.puuid}

                for teammate_nickname in extra_nicknames:
                    teammate = await self.resolve_player_identity(teammate_nickname)
                    if teammate is None:
                        await interaction.followup.send(
                            f"❌ Игрок {teammate_nickname} не найден или ник указан не в формате `name#tag`.",
                        )
                        return

                    if teammate.puuid in seen_puuids:
                        await interaction.followup.send(
                            "❌ Один и тот же игрок указан несколько раз.",
                        )
                        return

                    seen_puuids.add(teammate.puuid)
                    teammate_identities.append(teammate)

                results = self.build_shared_match_results(
                    base_player=base_player,
                    teammates=teammate_identities,
                    player_matches=player_matches,
                )

                if not results:
                    teammate_list = ", ".join(player.riot_id for player in teammate_identities)
                    await interaction.followup.send(
                        self.build_sync_summary(
                            recent_match_count=len(recent_match_ids),
                            synced_count=synced_count,
                            player_match_count=len(player_matches),
                            result_count=0,
                        )
                        + f"\nСовместных матчей с **{teammate_list}** не найдено.",
                    )
                    return

            view = SearchPaginatorView(
                author_id=interaction.user.id,
                base_player=base_player,
                results=results,
            )

            await interaction.followup.send(
                content=(
                    self.build_shared_players_summary(
                        base_player=base_player,
                        teammates=teammate_identities,
                        results=results,
                    )
                    if extra_nicknames else
                    self.build_sync_summary(
                        recent_match_count=len(recent_match_ids),
                        synced_count=synced_count,
                        player_match_count=len(player_matches),
                        result_count=len(results),
                    )
                ),
                embed=view._build_embed(),
                view=view,
            )

        except Exception as e:
            print(f"❌ Ошибка в /search: {e!r}")

            if interaction.response.is_done():
                await interaction.followup.send(
                    f"⚠️ Произошла ошибка: {e}",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f"⚠️ Произошла ошибка: {e}",
                    ephemeral=True,
                )

    @search.autocomplete("character_name")
    async def character_name_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        champions = self.get_champion_names()
        if not champions:
            return []

        if not current:
            return [
                app_commands.Choice(name=champion, value=champion)
                for champion in champions[:25]
            ]

        normalized_current = self.normalize_text(current)

        startswith_matches = [
            champion for champion in champions
            if self.normalize_text(champion).startswith(normalized_current)
        ]
        contains_matches = [
            champion for champion in champions
            if normalized_current in self.normalize_text(champion)
            and champion not in startswith_matches
        ]

        return [
            app_commands.Choice(name=champion, value=champion)
            for champion in (startswith_matches + contains_matches)[:25]
        ]


async def setup(bot: commands.Bot):
    await bot.add_cog(Search(bot))
