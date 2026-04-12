from discord.ext import commands, tasks
from utils.storage import load_players
from config import load_config


class MatchWatcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}
        self.first = False
        self.loop.start()

    @tasks.loop(minutes=3)
    async def loop(self):
        players = load_players()
        print(f"👥 Игроков: {len(players)}")

    @loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(MatchWatcher(bot))