import discord
from discord.ext import commands
from discord import app_commands

from db.repositories.matches_repository import MatchesRepository
from utils.storage import load_players


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.matches_repo = MatchesRepository(bot.db)

    # -----------------------
    # 🏓 PING
    # -----------------------
    @app_commands.command(
        name="ping",
        description="Проверка работы бота"
    )
    async def ping(self, interaction: discord.Interaction):

        latency = round(self.bot.latency * 1000)

        await interaction.response.send_message(
            f"🏓 Pong! Задержка: **{latency}ms**"
        )

    # -----------------------
    # 📘 HELPLOL
    # -----------------------
    @app_commands.command(
        name="helplol",
        description="Справка по командам"
    )
    async def helplol(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🎮 CCG Bot Help",
            description="Команды бота по категориям",
            color=discord.Color.purple()
        )

        embed.add_field(
            name="Основное",
            value=(
                "`/5stars` - рандом ролей с баном одной роли\n"
                "`/lolstats` - статистика матчей игрока, без count покажет весь максимум из БД\n"
                "`/matchdetails` - подробности конкретного матча\n"
                "`/search` - поиск по чемпиону или совместным играм\n"
                "`/records` - рекорды игроков из списка\n"
                "`/playerslol` - список отслеживаемых игроков\n"
                "`/whoingame` - кто из списка сейчас в игре\n"
                "`/dbstats` - сводка по локальной базе"
            ),
            inline=False
        )

        embed.add_field(
            name="Управление",
            value=(
                "`/addplayer` - добавить игрока в список\n"
                "`/removeplayer` - удалить игрока из списка\n"
                "`/setchannel` - установить канал уведомлений\n"
                "`/allowuser` - выдать доступ к управлению списком\n"
                "`/disallowuser` - забрать доступ к управлению списком"
            ),
            inline=False
        )

        embed.add_field(
            name="Служебное",
            value="`/ping` - проверка, что бот отвечает",
            inline=False
        )

        embed.set_footer(text="Riot API | CCG Bot")

        await interaction.response.send_message(embed=embed)

    @staticmethod
    def format_duration(total_seconds: int) -> str:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours} ч {minutes} мин"

    @app_commands.command(
        name="dbstats",
        description="Показать сводку по локальной базе данных"
    )
    async def dbstats(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            players_row = await self.bot.db.fetchone(
                "SELECT COUNT(*) AS count FROM players"
            )
            matches_row = await self.bot.db.fetchone(
                "SELECT COUNT(*) AS count, COALESCE(SUM(game_duration), 0) AS total_duration FROM matches"
            )
            tracked_stats_row = await self.bot.db.fetchone(
                "SELECT COUNT(*) AS count, COUNT(DISTINCT puuid) AS unique_players FROM player_match_stats"
            )

            total_players_in_db = int(players_row["count"] if players_row else 0)
            total_matches = int(matches_row["count"] if matches_row else 0)
            total_duration = int(matches_row["total_duration"] if matches_row else 0)
            tracked_stats_count = int(tracked_stats_row["count"] if tracked_stats_row else 0)
            tracked_players_in_stats = int(tracked_stats_row["unique_players"] if tracked_stats_row else 0)
            tracked_players_list = len(load_players())

            total_question_pings = 0
            for match_data in await self.matches_repo.get_all_matches_json():
                participants = match_data.get("info", {}).get("participants", [])
                total_question_pings += sum(
                    int(player.get("enemyMissingPings", 0) or 0)
                    for player in participants
                )

            avg_match_duration = int(total_duration / total_matches) if total_matches else 0

            embed = discord.Embed(
                title="🗃️ Статистика списочка",
                color=discord.Color.teal()
            )

            embed.add_field(
                name="Игроки в базе",
                value=f"**{total_players_in_db}**",
                inline=True
            )
            embed.add_field(
                name="Матчи в базе",
                value=f"**{total_matches}**",
                inline=True
            )
            embed.add_field(
                name="Игроки в списке",
                value=f"**{tracked_players_list}**",
                inline=True
            )
            embed.add_field(
                name="Записей stats",
                value=f"**{tracked_stats_count}**",
                inline=True
            )
            embed.add_field(
                name="Игроков в stats",
                value=f"**{tracked_players_in_stats}**",
                inline=True
            )
            embed.add_field(
                name="Средняя длительность",
                value=f"**{self.format_duration(avg_match_duration)}**",
                inline=True
            )
            embed.add_field(
                name="Суммарное время игр",
                value=f"**{self.format_duration(total_duration)}**",
                inline=True
            )
            embed.add_field(
                name="Всего ?-пингов",
                value=f"**{total_question_pings}**",
                inline=True
            )

            embed.set_footer(text="CCG Bot")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"❌ Ошибка в /dbstats: {e!r}")

            if interaction.response.is_done():
                await interaction.followup.send(
                    f"⚠️ Произошла ошибка: {e}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"⚠️ Произошла ошибка: {e}",
                    ephemeral=True
                )


async def setup(bot):
    await bot.add_cog(Misc(bot))
