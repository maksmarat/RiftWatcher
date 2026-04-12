from discord.ext import commands
from discord import app_commands
import discord

from utils.storage import load_players


class Players(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="playerslol")
    async def playerslol(self, interaction: discord.Interaction):
        await interaction.response.defer()

        players = load_players()

        await interaction.followup.send("\n".join(players) or "Нет игроков")


async def setup(bot):
    await bot.add_cog(Players(bot))