import discord
from discord.ext import commands
from discord import app_commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            title="🎮 LoL Bot Help",
            description="Список команд бота",
            color=discord.Color.purple()
        )

        embed.add_field(
            name="/lolstats",
            value="Статистика игрока (ник#тег)",
            inline=False
        )

        embed.add_field(
            name="/matchdetails",
            value="Детали матча",
            inline=False
        )

        embed.add_field(
            name="/playerslol",
            value="Список отслеживаемых игроков",
            inline=False
        )

        embed.add_field(
            name="/whoingame",
            value="Кто сейчас в игре",
            inline=False
        )

        embed.add_field(
            name="/5stars",
            value="Рандом ролей с выбором нелюбимой",
            inline=False
        )

        embed.add_field(
            name="/setchannel",
            value="Канал уведомлений",
            inline=False
        )

        embed.set_footer(text="Riot Games API Bot")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Misc(bot))