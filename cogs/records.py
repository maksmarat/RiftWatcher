from __future__ import annotations

from dataclasses import dataclass

import discord
from discord.ext import commands
from discord import app_commands

from db.repositories.matches_repository import MatchesRepository
from utils.storage import load_players
from utils.record_definitions import (
    RECORD_DEFINITIONS,
    RecordDefinition,
    default_formatter,
)


@dataclass
class RecordResult:
    definition: RecordDefinition
    value: float | int
    participant: dict
    match_id: str


class Records(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.matches_repo = MatchesRepository(bot.db)

    def build_player_name(self, participant: dict) -> str:
        return f"{participant.get('riotIdGameName', 'Unknown')}#{participant.get('riotIdTagline', 'Unknown')}"

    def format_record_entry(self, result: RecordResult) -> str:
        participant = result.participant
        match_id = result.match_id
        champion = participant.get("championName", "Unknown")
        player_name = self.build_player_name(participant)

        formatter = result.definition.formatter or default_formatter
        value_text = formatter(result.value)

        return f"**{player_name}** — {value_text} ({champion}, `{match_id}`)"

    def collect_best_records(
        self,
        matches: list[dict],
        tracked_set: set[str],
    ) -> dict[str, RecordResult]:
        best_records: dict[str, RecordResult] = {}

        for match_data in matches:
            metadata = match_data.get("metadata", {})
            info = match_data.get("info", {})
            match_id = metadata.get("matchId", "Unknown")
            participants = info.get("participants", [])

            for participant in participants:
                if participant.get("puuid") not in tracked_set:
                    continue

                for definition in RECORD_DEFINITIONS:
                    value = definition.extractor(participant)

                    current_best = best_records.get(definition.key)
                    if current_best is None or value > current_best.value:
                        best_records[definition.key] = RecordResult(
                            definition=definition,
                            value=value,
                            participant=participant,
                            match_id=match_id,
                        )

        return best_records

    @app_commands.command(
        name="records",
        description="Показать рекорды игроков"
    )
    async def records(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            tracked_set = set(load_players())
            if not tracked_set:
                await interaction.followup.send("⚠️ Список players.txt пуст.")
                return

            matches = await self.matches_repo.get_all_matches_json()
            if not matches:
                await interaction.followup.send("⚠️ В базе пока нет сохранённых матчей.")
                return

            best_records = self.collect_best_records(matches, tracked_set)

            embed = discord.Embed(
                title="🏆 Рекорды игроков из списка",
                color=discord.Color.gold()
            )

            for definition in RECORD_DEFINITIONS:
                result = best_records.get(definition.key)

                if result is None:
                    embed.add_field(
                        name=definition.label,
                        value="Нет данных",
                        inline=False
                    )
                    continue

                embed.add_field(
                    name=definition.label,
                    value=self.format_record_entry(result),
                    inline=False
                )

            embed.set_footer(text="CCG Bot")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"❌ Ошибка в /records: {e!r}")

            if interaction.response.is_done():
                await interaction.followup.send(
                    f"⚠️ Ошибка: {e}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"⚠️ Ошибка: {e}",
                    ephemeral=True
                )


async def setup(bot):
    await bot.add_cog(Records(bot))