import discord
from discord.ext import commands
from discord import app_commands

from config import load_config, save_config


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------
    # 📌 SETCHANNEL
    # -----------------------
    @app_commands.command(
        name="setchannel",
        description="Установить канал для уведомлений"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setchannel(self, interaction: discord.Interaction):

        config = load_config()
        config["notify_channel_id"] = interaction.channel_id
        save_config(config)

        await interaction.response.send_message(
            f"✅ Канал {interaction.channel.mention} установлен для уведомлений"
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))