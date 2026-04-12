from discord.ext import commands
from discord import app_commands
import discord

from utils.helpers import parse_riot_id
from utils.embeds import build_match_embed


class LoL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lolstats")
    async def lolstats(self, interaction: discord.Interaction, nickname: str):
        game, tag = parse_riot_id(nickname)

        if not game:
            await interaction.response.send_message("❌ Формат: ник#тег")
            return

        await interaction.response.defer()

        stats = await self.bot.riot_api.get_player_stats(game, tag, 5)

        await interaction.followup.send(str(stats))


async def setup(bot):
    await bot.add_cog(LoL(bot))