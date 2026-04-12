import discord
from discord.ext import commands
import asyncio
import os

from settings import DISCORD_TOKEN
from riot.riot_api import RiotAPI

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} запущен!')
    print(f'👥 Серверов: {len(bot.guilds)}')

    try:
        synced = await bot.tree.sync()
        print(f"🔁 Slash-команд: {len(synced)}")
    except Exception as e:
        print(f"❌ Sync ошибка: {e}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        await message.channel.send("What's up? Use /help to see available commands!")

    await bot.process_commands(message)


async def main():
    async with bot:
        bot.riot_api = RiotAPI(os.getenv("RIOT_API_KEY"))

        await bot.riot_api.init()
        # загрузка модулей
        await bot.load_extension("cogs.lol")
        await bot.load_extension("cogs.players")
        await bot.load_extension("cogs.game")
        await bot.load_extension("cogs.admin")
        await bot.load_extension("cogs.misc")
        await bot.load_extension("services.match_watcher")

        await bot.start(DISCORD_TOKEN)


asyncio.run(main())