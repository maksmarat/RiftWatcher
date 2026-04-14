from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands

from utils.helpers import parse_riot_id
from utils.storage import (
    load_players,
    add_player,
    remove_player,
    is_user_allowed,
    add_allowed_user,
    remove_allowed_user,
    load_allowed_users,
)
from db.repositories.players_repository import PlayersRepository


class Players(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players_repo = PlayersRepository(bot.db)

    def ensure_allowed(self, interaction: discord.Interaction) -> bool:
        return is_user_allowed(interaction.user.id)

    @app_commands.command(
        name="playerslol",
        description="Список отслеживаемых игроков"
    )
    async def playerslol(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            puuids = load_players()

            if not puuids:
                await interaction.followup.send("⚠️ В players.txt нет игроков.")
                return

            result = []

            for puuid in puuids:
                player_row = await self.players_repo.get_player_by_puuid(puuid)

                if player_row and player_row["game_name"] and player_row["tag_line"]:
                    result.append(f"{player_row['game_name']}#{player_row['tag_line']}")
                    continue

                summoner = await self.bot.riot_api.get_summoner_data(puuid)
                if summoner:
                    nickname = f"{summoner['gameName']}#{summoner['tagLine']}"
                    result.append(nickname)

                    await self.players_repo.upsert_player(
                        puuid=puuid,
                        game_name=summoner["gameName"],
                        tag_line=summoner["tagLine"]
                    )
                else:
                    result.append(f"Unknown ({puuid[:8]})")

            embed = discord.Embed(
                title="📋 Отслеживаемые игроки",
                description="\n".join(result[:100]),
                color=discord.Color.blue()
            )

            if len(result) > 100:
                embed.set_footer(text=f"Показаны первые 100 из {len(result)} игроков")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"❌ Ошибка в /playerslol: {e!r}")
            await interaction.followup.send(
                f"⚠️ Ошибка: {e}",
                ephemeral=True
            )

    @app_commands.command(
        name="addplayer",
        description="Добавить игрока в список)"
    )
    async def addplayer(self, interaction: discord.Interaction, nickname: str):
        if not self.ensure_allowed(interaction):
            await interaction.response.send_message(
                "❌ Я вам запрещаю делать это.",
                ephemeral=True
            )
            return

        game_name, tag_line = parse_riot_id(nickname)

        if not game_name or not tag_line:
            await interaction.response.send_message(
                "❌ Неверный формат ника. Используй: nickname#tag",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            puuid = await self.bot.riot_api.get_puuid(game_name, tag_line)
            if not puuid:
                await interaction.followup.send(
                    f"❌ Игрок **{nickname}** не найден.",
                    ephemeral=True
                )
                return

            added = add_player(puuid)

            await self.players_repo.upsert_player(
                puuid=puuid,
                game_name=game_name,
                tag_line=tag_line
            )

            if not added:
                await interaction.followup.send(
                    f"⚠️ Игрок **{nickname}** уже есть в книжечке.",
                    ephemeral=True
                )
                return

            await interaction.followup.send(
                f"✅ Преступаю к отслеживанию **{nickname}**",
                ephemeral=True
            )

        except Exception as e:
            print(f"❌ Ошибка в /addplayer: {e!r}")
            await interaction.followup.send(
                f"⚠️ Ошибка: {e}",
                ephemeral=True
            )

    @app_commands.command(
        name="removeplayer",
        description="Удалить игрока из списка("
    )
    async def removeplayer(self, interaction: discord.Interaction, nickname: str):
        if not self.ensure_allowed(interaction):
            await interaction.response.send_message(
                "❌ У тебя нет доступа к этой команде.",
                ephemeral=True
            )
            return

        game_name, tag_line = parse_riot_id(nickname)

        if not game_name or not tag_line:
            await interaction.response.send_message(
                "❌ Неверный формат ника. Используй: nickname#tag",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            puuid = await self.bot.riot_api.get_puuid(game_name, tag_line)
            if not puuid:
                await interaction.followup.send(
                    f"❌ Игрок **{nickname}** не найден.",
                    ephemeral=True
                )
                return

            removed = remove_player(puuid)

            if not removed:
                await interaction.followup.send(
                    f"⚠️ Игрок **{nickname}** отсутствует в книжечке.",
                    ephemeral=True
                )
                return

            await interaction.followup.send(
                f"🗑️ Игрок **{nickname}** очищен.",
                ephemeral=True
            )

        except Exception as e:
            print(f"❌ Ошибка в /removeplayer: {e!r}")
            await interaction.followup.send(
                f"⚠️ Ошибка: {e}",
                ephemeral=True
            )

    @app_commands.command(
        name="allowuser",
        description="Разрешить пользователю использовать add/remove player"
    )
    async def allowuser(self, interaction: discord.Interaction, user: discord.Member):
        if not self.ensure_allowed(interaction):
            await interaction.response.send_message(
                "❌ Я вам запрещаю делать это.",
                ephemeral=True
            )
            return

        added = add_allowed_user(user.id)

        if not added:
            await interaction.response.send_message(
                f"⚠️ {user.mention} уже есть в whitelist.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"✅ {user.mention} добавлен в whitelist.",
            ephemeral=True
        )

    @app_commands.command(
        name="disallowuser",
        description="Запретить пользователю использовать add/remove player"
    )
    async def disallowuser(self, interaction: discord.Interaction, user: discord.Member):
        if not self.ensure_allowed(interaction):
            await interaction.response.send_message(
                "❌ Я вам запрещаю делать это.",
                ephemeral=True
            )
            return

        if user.id == interaction.user.id and len(load_allowed_users()) <= 1:
            await interaction.response.send_message(
                "❌ Нельзя удалить последнего пользователя из whitelist.",
                ephemeral=True
            )
            return

        removed = remove_allowed_user(user.id)

        if not removed:
            await interaction.response.send_message(
                f"⚠️ {user.mention} не находится в whitelist.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"🗑️ {user.mention} удалён из whitelist.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Players(bot))