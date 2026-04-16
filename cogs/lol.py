from __future__ import annotations

from datetime import datetime
from math import ceil
from typing import Literal

import discord
from discord.ext import commands
from discord import app_commands

from utils.helpers import parse_riot_id
from db.repositories.players_repository import PlayersRepository
from db.repositories.matches_repository import MatchesRepository

import asyncio

MATCHES_PER_PAGE = 10


class StatsPaginatorView(discord.ui.View):
    def __init__(
        self,
        author_id: int,
        nickname: str,
        matches: list,
        filter_label: str,
        timeout: float = 180
    ):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.nickname = nickname
        self.matches = matches
        self.filter_label = filter_label
        self.page = 0
        self.total_pages = max(1, ceil(len(matches) / MATCHES_PER_PAGE))

        self._update_buttons()

    def _update_buttons(self) -> None:
        self.prev_button.disabled = self.page <= 0
        self.next_button.disabled = self.page >= self.total_pages - 1

    def _build_summary(self) -> str:
        total_matches = len(self.matches)
        if total_matches == 0:
            return "Нет матчей для отображения."

        wins = sum(1 for m in self.matches if m["win"])
        losses = total_matches - wins
        winrate = (wins / total_matches) * 100 if total_matches else 0

        total_kills = sum(m["kills"] for m in self.matches)
        total_deaths = sum(m["deaths"] for m in self.matches)
        total_assists = sum(m["assists"] for m in self.matches)
        total_dpm = sum(float(m["damage_per_minute"] or 0) for m in self.matches)
        total_cs = sum(int(m["cs"] or 0) for m in self.matches)

        avg_kills = total_kills / total_matches
        avg_deaths = total_deaths / total_matches
        avg_assists = total_assists / total_matches
        avg_dpm = total_dpm / total_matches
        avg_cs = total_cs / total_matches

        if total_deaths == 0:
            overall_kda = total_kills + total_assists
        else:
            overall_kda = (total_kills + total_assists) / total_deaths

        return (
            f"**Фильтр:** {self.filter_label}\n"
            f"**Матчей:** {total_matches} | **Победы:** {wins} | **Поражения:** {losses} | "
            f"**WR:** {winrate:.1f}%\n"
            f"**Средний K/D/A:** {avg_kills:.1f}/{avg_deaths:.1f}/{avg_assists:.1f} | "
            f"**Общий KDA:** {overall_kda:.2f}\n"
            f"**Средний DPM:** {avg_dpm:.0f} | **Средний CS:** {avg_cs:.1f}"
        )

    def _build_embed(self) -> discord.Embed:
        total_matches = len(self.matches)
        start = self.page * MATCHES_PER_PAGE
        end = start + MATCHES_PER_PAGE
        current_matches = self.matches[start:end]

        page_start_num = start + 1
        page_end_num = start + len(current_matches)

        embed = discord.Embed(
            title=f"📊 Статистика {self.nickname}",
            description=(
                f"{self._build_summary()}\n\n"
                f"**Показаны матчи {page_start_num}–{page_end_num} из {total_matches}**"
            ),
            color=discord.Color.blue()
        )

        for global_index, match in enumerate(current_matches, start=page_start_num):
            win_emoji = "✅" if match["win"] else "❌"

            game_start = match["game_start"]
            if game_start is None:
                match_time_text = "Неизвестное время"
            else:
                try:
                    # Riot timestamp в БД хранится в миллисекундах
                    match_time_text = datetime.fromtimestamp(
                        int(game_start) / 1000
                    ).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    match_time_text = str(game_start)

            kills = int(match["kills"] or 0)
            deaths = int(match["deaths"] or 0)
            assists = int(match["assists"] or 0)
            dpm = float(match["damage_per_minute"] or 0)
            cs = int(match["cs"] or 0)
            gold = int(match["gold_earned"] or 0)

            if deaths == 0:
                match_kda = kills + assists
            else:
                match_kda = (kills + assists) / deaths

            embed.add_field(
                name=f"Match {global_index} · {match_time_text}",
                value=(
                    f"{win_emoji} **{match['champion_name']}**\n"
                    f"K/D/A: **{kills}/{deaths}/{assists}** | **KDA:** {match_kda:.2f}\n"
                    f"DPM: **{dpm:.0f}** | CS: **{cs}** | Gold: **{gold}**"
                ),
                inline=False
            )

        embed.set_footer(
            text=f"Страница {self.page + 1}/{self.total_pages} • Riot API           CCG Bot"
        )
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ Эти кнопки доступны только тому, кто вызвал команду.",
                ephemeral=True
            )
            return False
        return True

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self._build_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self._build_embed(), view=self)


class LoL(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players_repo = PlayersRepository(bot.db)
        self.matches_repo = MatchesRepository(bot.db)
    #lolstats
    @app_commands.command(
        name="lolstats",
        description="Показать статистику последних матчей игрока"
    )
    @app_commands.describe(
        nickname="Ник в формате gameName#tagLine",
        match_count="Количество матчей от 1 до 100",
        result_filter="Фильтр матчей: все / победы / поражения"
    )
    @app_commands.choices(
        result_filter=[
            app_commands.Choice(name="Все", value="all"),
            app_commands.Choice(name="Только победы", value="wins"),
            app_commands.Choice(name="Только поражения", value="losses"),
        ]
    )
    async def lolstats(
        self,
        interaction: discord.Interaction,
        nickname: str,
        match_count: app_commands.Range[int, 1, 100] = 5,
        result_filter: app_commands.Choice[str] | None = None,
    ):
        game_name, tag_line = parse_riot_id(nickname)

        if not game_name or not tag_line:
            await interaction.response.send_message(
                "❌ Неверный формат ника. Используй: nickname#tag",
                ephemeral=True
            )
            return

        filter_value = result_filter.value if result_filter else "all"
        filter_label_map = {
            "all": "Все",
            "wins": "Только победы",
            "losses": "Только поражения",
        }
        filter_label = filter_label_map.get(filter_value, "Все")

        await interaction.response.defer()

        try:
            # 1. Получаем puuid
            puuid = await self.bot.riot_api.get_puuid(game_name, tag_line)
            if not puuid:
                await interaction.followup.send(f"❌ Игрок {nickname} не найден.")
                return

            # 2. Обновляем игрока в БД
            await self.players_repo.upsert_player(
                puuid=puuid,
                game_name=game_name,
                tag_line=tag_line,
            )

            # 3. Обязательно сверяем последние match_id через Riot API
            recent_match_ids = await self.bot.riot_api.get_recent_matches(
                puuid,
                count=match_count
            )

            if not recent_match_ids:
                await interaction.followup.send(
                    f"⚠️ Для {nickname} не найдено матчей."
                )
                return

            # 4. Догружаем недостающие матчи в БД
            synced_count = 0
            for match_id in recent_match_ids:
                exists = await self.matches_repo.match_exists(match_id)
                if exists:
                    match_data = await self.matches_repo.get_match_json(match_id)
                    if match_data:
                        await self.matches_repo.insert_player_match_stats_for_puuid(match_data, puuid)
                    continue

                match_data = await self.bot.riot_api.get_match_details(match_id)
                if not match_data:
                    continue

                await self.matches_repo.save_full_match(match_data)
                await self.matches_repo.insert_player_match_stats_for_puuid(match_data, puuid)
                synced_count += 1

            # 5. Получаем матчи игрока из БД
            db_matches = await self.matches_repo.get_recent_matches_for_player(
                puuid=puuid,
                limit=match_count
            )

            if not db_matches:
                await interaction.followup.send(
                    "⚠️ Матчи не удалось загрузить из бд."
                )
                return

            # 6. Фильтрация
            filtered_matches = []
            for match in db_matches:
                is_win = bool(match["win"])
                if filter_value == "wins" and not is_win:
                    continue
                if filter_value == "losses" and is_win:
                    continue
                filtered_matches.append(match)

            if not filtered_matches:
                await interaction.followup.send(
                    f"⚠️ По фильтру **{filter_label}** для {nickname} ничего не найдено."
                )
                return

            # 7. Пагинация кнопками
            view = StatsPaginatorView(
                author_id=interaction.user.id,
                nickname=f"{game_name}#{tag_line}",
                matches=filtered_matches,
                filter_label=filter_label,
            )

            embed = view._build_embed()

            sync_note = ""
            if synced_count > 0:
                sync_note = f"\n🔄 Новых матчей синхронизировано: **{synced_count}**"

            await interaction.followup.send(
                content=(
                    f"Запрошено матчей: **{match_count}**"
                    f"{sync_note}"
                ),
                embed=embed,
                view=view
            )

        except Exception as e:
            print(f"❌ Ошибка в /lolstats: {e!r}")

            try:
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
            except Exception as send_error:
                print(f"❌ Ошибка отправки ошибки: {send_error!r}")

    #matchdetails
    @app_commands.command(
        name="matchdetails",
        description="Показать подробности матча по его номеру из /lolstats"
    )
    @app_commands.describe(
        nickname="Ник в формате gameName#tagLine",
        match_number="Номер матча из списка /lolstats (1 = самый новый)"
    )
    async def matchdetails(
        self,
        interaction: discord.Interaction,
        nickname: str,
        match_number: app_commands.Range[int, 1, 100]
    ):
        game_name, tag_line = parse_riot_id(nickname)

        if not game_name or not tag_line:
            await interaction.response.send_message(
                "❌ Неверный формат ника. Используй: nickname#tag",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        try:
            # 1. Получаем puuid игрока
            puuid = await self.bot.riot_api.get_puuid(game_name, tag_line)
            if not puuid:
                await interaction.followup.send(
                    f"❌ Игрок {nickname} не найден."
                )
                return

            # 2. Обновляем игрока в БД
            await self.players_repo.upsert_player(
                puuid=puuid,
                game_name=game_name,
                tag_line=tag_line,
            )

            # 3. Получаем список последних матчей из Riot API
            recent_match_ids = await self.bot.riot_api.get_recent_matches(
                puuid,
                count=match_number
            )

            if not recent_match_ids:
                await interaction.followup.send(
                    f"⚠️ Для {nickname} не найдено матчей."
                )
                return

            if len(recent_match_ids) < match_number:
                await interaction.followup.send(
                    f"⚠️ У игрока найдено только {len(recent_match_ids)} матчей."
                )
                return

            # 4. Берём нужный match_id по номеру
            match_id = recent_match_ids[match_number - 1]

            # 5. Если матча нет в БД — догружаем
            exists = await self.matches_repo.match_exists(match_id)
            if not exists:
                match_data = await self.bot.riot_api.get_match_details(match_id)
                if not match_data:
                    await interaction.followup.send(
                        f"❌ Не удалось загрузить матч #{match_number}."
                    )
                    return

                await self.matches_repo.save_full_match(match_data)

            # 6. Загружаем raw_json матча из БД
            match_data = await self.matches_repo.get_match_json(match_id)
            if not match_data:
                await interaction.followup.send(
                    f"⚠️ Матч #{match_number} не удалось загрузить из бд."
                )
                return

            info = match_data.get("info", {})
            participants = info.get("participants", [])

            # 7. Ищем целевого игрока
            target_player = next(
                (p for p in participants if p.get("puuid") == puuid),
                None
            )

            if not target_player:
                await interaction.followup.send(
                    f"⚠️ Игрок {nickname} не найден в матче #{match_number}."
                )
                return

            blue_team = [p for p in participants if p.get("teamId") == 100]
            red_team = [p for p in participants if p.get("teamId") == 200]

            game_start = info.get("gameStartTimestamp")
            if game_start:
                try:
                    match_time_text = datetime.fromtimestamp(
                        game_start / 1000
                    ).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    match_time_text = "Неизвестно"
            else:
                match_time_text = "Неизвестно"

            game_duration = info.get("gameDuration", 0)
            minutes = game_duration // 60
            seconds = game_duration % 60
            duration_text = f"{minutes}:{seconds:02d}"

            embed = discord.Embed(
                title=f"🎮 Match Details — {nickname}",
                description=(
                    f"**Match Number:** `{match_number}`\n"
                    f"**Match ID:** `{match_id}`\n"
                    f"**Start Time:** {match_time_text}\n"
                    f"**Duration:** {duration_text}"
                ),
                color=discord.Color.green()
            )

            embed.add_field(
                name=f"{'✅' if blue_team and blue_team[0].get('win') else '❌'} Blue Team",
                value=self.format_team(blue_team, puuid),
                inline=True
            )

            embed.add_field(
                name=f"{'✅' if red_team and red_team[0].get('win') else '❌'} Red Team",
                value=self.format_team(red_team, puuid),
                inline=True
            )

            target_kills = target_player.get("kills", 0)
            target_deaths = target_player.get("deaths", 0)
            target_assists = target_player.get("assists", 0)
            target_dpm = target_player.get("challenges", {}).get("damagePerMinute", 0)
            target_cs = target_player.get("totalMinionsKilled", 0) + target_player.get("neutralMinionsKilled", 0)
            target_gold = target_player.get("goldEarned", 0)
            champion = target_player.get("championName", "Unknown")

            if target_deaths == 0:
                kda = target_kills + target_assists
            else:
                kda = (target_kills + target_assists) / target_deaths

            embed.set_footer(text=f"{nickname} {target_kills}/{target_deaths}/{target_assists} KDA: {kda:.2f}       |       Riot API        CCG Bot")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"❌ Ошибка в /matchdetails: {e!r}")

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
    
    #whoingame
    @app_commands.command(
        name="whoingame",
        description="Показать, кто из списка сейчас в игре"
    )
    async def whoingame(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            from utils.storage import load_players

            puuids = load_players()

            if not puuids:
                await interaction.followup.send("⚠️ Список игроков пуст (players.txt)")
                return

            ingame_players = []

            for puuid in puuids:
                try:
                    # Проверяем, в игре ли игрок
                    in_game, game_data = await self.bot.riot_api.is_player_in_game_by_puuid(puuid)

                    if not in_game:
                        continue

                    # Получаем инфу об игроке
                    summoner = await self.bot.riot_api.get_summoner_data(puuid)

                    if summoner:
                        nickname = f"{summoner['gameName']}#{summoner['tagLine']}"
                    else:
                        nickname = "Unknown"

                    # Ищем чемпиона
                    champion_name = "Unknown"

                    for participant in game_data.get("participants", []):
                        if participant.get("puuid") == puuid:
                            champion_id = participant.get("championId")

                            champion_name = self.bot.champions.get(
                                champion_id,
                                f"Unknown ({champion_id})"
                            )

                    # Время игры
                    game_length = game_data.get("gameLength", 0)
                    minutes = game_length // 60
                    seconds = game_length % 60
                    game_time = f"{minutes}:{seconds:02d}"

                    ingame_players.append({
                        "name": nickname,
                        "champion": champion_name,
                        "game_time": game_time
                    })

                    await asyncio.sleep(0.1)  # защита от rate limit

                except Exception as e:
                    print(f"Ошибка whoingame для {puuid}: {e}")

            embed = discord.Embed(
                title="🎮 Кто сейчас в игре",
                color=discord.Color.green()
            )

            if ingame_players:
                for player in ingame_players:
                    embed.add_field(
                        name="🟢 В игре",
                        value=(
                            f"🎮 {player['name']}\n"
                            f"Чемпион: **{player['champion']}**\n"
                            f"Время: **{player['game_time']}**"
                        ),
                        inline=False
                    )
            else:
                embed.add_field(
                    name="🟢 В игре",
                    value="Никого нет",
                    inline=False
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"❌ Ошибка в /whoingame: {e!r}")
            await interaction.followup.send(
                f"⚠️ Произошла ошибка: {e}",
                ephemeral=True
            )

    def format_team(self, team: list[dict], target_puuid: str) -> str:
        if not team:
            return "Нет данных"

        lines = []
        for player in team:
            riot_name = f"{player.get('riotIdGameName', 'Unknown')}#{player.get('riotIdTagline', 'Unknown')}"
            champion = player.get("championName", "Unknown")
            kills = player.get("kills", 0)
            deaths = player.get("deaths", 0)
            assists = player.get("assists", 0)
            cs = player.get("totalMinionsKilled", 0) + player.get("neutralMinionsKilled", 0)
            gold = player.get("goldEarned", 0)
            dpm = player.get("challenges", {}).get("damagePerMinute", 0)

            marker = "🎯 " if player.get("puuid") == target_puuid else ""

            lines.append(
                f"{marker}**{riot_name[:20]}**\n"
                f"{champion} | {kills}/{deaths}/{assists}\n"
                f"{dpm:.0f} DPM | CS {cs} | Gold {gold}\n"
            )

        text = "\n".join(lines)

        if len(text) > 1024:
            text = text[:1021] + "..."

        return text

async def setup(bot: commands.Bot):
    await bot.add_cog(LoL(bot))
