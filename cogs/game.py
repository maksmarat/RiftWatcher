from discord.ext import commands
from discord import app_commands
import discord
import asyncio
import random
from typing import Dict

ROLE_EMOJIS = {
    "👨‍❤️‍👨": "топ",
    "🌲": "лес",
    "🤡": "мид",
    "💩": "адк",
    "🛡️": "сап"
}

ALL_ROLES = list(ROLE_EMOJIS.values())
SUPPORT_ROLE = "сап"


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessions: Dict[int, dict] = {}

    # -------------------------------
    # 🎮 ОСНОВНАЯ КОМАНДА
    # -------------------------------
    @app_commands.command(name="5stars", description="Рандом ролей с баном одной роли")
    async def five_stars(self, interaction: discord.Interaction):

        channel_id = interaction.channel_id

        if channel_id in self.sessions:
            await interaction.response.send_message(
                "❌ В этом канале уже идет игра!", ephemeral=True
            )
            return

        session = self.create_session(channel_id)
        self.sessions[channel_id] = session

        embed = discord.Embed(
            title="🌟 5 Stars",
            description=(
                "Выбери роль, которую НЕ хочешь:\n\n"
                "👨‍❤️‍👨 Топ\n🌲 Лес\n🤡 Мид\n💩 Адк\n🛡️ Сап\n\n"
                "⚠️ Нужно 5 игроков"
            ),
            color=discord.Color.gold()
        )

        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()

        session["message_id"] = msg.id

        # добавляем реакции
        for emoji in ROLE_EMOJIS:
            await msg.add_reaction(emoji)

        # запускаем таймер
        session["task"] = asyncio.create_task(self.timeout(session, interaction))

        await self.collect_players(session, interaction)

    # -------------------------------
    # 🧠 СОЗДАНИЕ СЕССИИ
    # -------------------------------
    def create_session(self, channel_id):
        return {
            "channel_id": channel_id,
            "message_id": None,
            "players": {},  # user_id: disliked_role
            "temp_messages": [],
            "task": None
        }

    # -------------------------------
    # ⏳ ТАЙМАУТ
    # -------------------------------
    async def timeout(self, session, interaction):
        await asyncio.sleep(500)

        if session["channel_id"] not in self.sessions:
            return

        if len(session["players"]) < 5:
            await self.safe_edit_message(
                interaction,
                session["message_id"],
                "⏰ Время вышло! Недостаточно игроков."
            )

            await self.cleanup(session, interaction)
            self.sessions.pop(session["channel_id"], None)

    # -------------------------------
    # 🎯 СБОР ИГРОКОВ
    # -------------------------------
    async def collect_players(self, session, interaction):
        def check(reaction, user):
            return (
                reaction.message.id == session["message_id"]
                and user != self.bot.user
                and str(reaction.emoji) in ROLE_EMOJIS
                and user.id not in session["players"]
            )

        while len(session["players"]) < 5:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    timeout=500,
                    check=check
                )

                role = ROLE_EMOJIS[str(reaction.emoji)]

                if role == SUPPORT_ROLE and SUPPORT_ROLE in session["players"].values():
                    try:
                        await reaction.remove(user)
                    except:
                        pass

                    temp_msg = await interaction.followup.send(
                        f"❌ {user.mention} роль **{role}** уже занята как нелюбимая. Выбери другую роль."
                    )
                    session["temp_messages"].append(temp_msg.id)
                    continue

                session["players"][user.id] = role

                # убираем реакцию
                try:
                    await reaction.remove(user)
                except:
                    pass

                temp_msg = await interaction.followup.send(
                    f"✅ {user.mention} выбрал: **{role}** ({len(session['players'])}/5)"
                )
                session["temp_messages"].append(temp_msg.id)

            except asyncio.TimeoutError:
                return

        # успех
        session["task"].cancel()
        await self.finish_game(session, interaction)

    # -------------------------------
    # 🎲 ЗАВЕРШЕНИЕ ИГРЫ
    # -------------------------------
    async def finish_game(self, session, interaction):
        await self.cleanup(session, interaction)

        assignments = self.generate_roles(session["players"])

        embed = discord.Embed(
            title="🎲 Результаты",
            color=discord.Color.green()
        )

        for user_id, role in assignments.items():
            user = interaction.guild.get_member(user_id)
            if user:
                embed.description = (embed.description or "") + \
                    f"\n{user.mention} → **{role.upper()}**"

        await interaction.followup.send(embed=embed)

        self.sessions.pop(session["channel_id"], None)

    # -------------------------------
    # 🧹 ОЧИСТКА
    # -------------------------------
    async def cleanup(self, session, interaction):
        channel = interaction.channel

        # удалить главное сообщение
        try:
            msg = await channel.fetch_message(session["message_id"])
            await msg.delete()
        except:
            pass

        # удалить временные
        for msg_id in session["temp_messages"]:
            try:
                temp = await channel.fetch_message(msg_id)
                await temp.delete()
            except:
                pass

    # -------------------------------
    # 🎲 ГЕНЕРАЦИЯ РОЛЕЙ (УЛУЧШЕНО)
    # -------------------------------
    def generate_roles(self, players):
        players_list = list(players.keys())

        for _ in range(100):
            roles = ALL_ROLES.copy()
            random.shuffle(roles)

            result = {}
            success = True

            for user_id in players_list:
                disliked = players[user_id]

                valid_roles = [r for r in roles if r != disliked]

                if not valid_roles:
                    success = False
                    break

                chosen = random.choice(valid_roles)
                roles.remove(chosen)
                result[user_id] = chosen

            if success:
                return result

        # fallback
        random.shuffle(players_list)
        random.shuffle(roles := ALL_ROLES.copy())

        return dict(zip(players_list, roles))

    # -------------------------------
    # 🛠 SAFE EDIT
    # -------------------------------
    async def safe_edit_message(self, interaction, message_id, text):
        try:
            msg = await interaction.channel.fetch_message(message_id)
            await msg.edit(content=text, embed=None)
        except:
            pass


async def setup(bot):
    await bot.add_cog(Game(bot))
