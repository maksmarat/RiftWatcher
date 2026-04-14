import asyncio
import os
import discord
from discord.ext import commands

from settings import DISCORD_TOKEN
from riot.riot_api import RiotAPI
from db.database import Database
from utils.storage import load_champions

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Синхронизировано команд: {len(synced)}")
    except Exception as e:
        print(f"❌ Ошибка sync: {e}")


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    print("APP COMMAND ERROR:", repr(error))
    try:
        if interaction.response.is_done():
            await interaction.followup.send(f"⚠️ Ошибка: {error}", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ Ошибка: {error}", ephemeral=True)
    except Exception as e:
        print("Ошибка в error handler:", repr(e))


async def main():
    async with bot:
        bot.riot_api = RiotAPI(os.getenv("RIOT_API_KEY"))
        await bot.riot_api.init()

        bot.db = Database()
        await bot.db.connect()
        await bot.db.init_schema()

        bot.champions = await load_champions()
        
        await bot.load_extension("cogs.lol")
        await bot.load_extension("cogs.players")
        await bot.load_extension("cogs.game")
        await bot.load_extension("cogs.admin")
        await bot.load_extension("cogs.misc")
        await bot.load_extension("services.match_watcher")

        try:
            await bot.start(DISCORD_TOKEN)
        finally:
            await bot.riot_api.close()
            await bot.db.close()


if __name__ == "__main__":
    asyncio.run(main())