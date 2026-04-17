from __future__ import annotations

import asyncio
import os
from datetime import datetime

import discord
from discord.ext import commands, tasks

import random

from config import load_config
from db.repositories.matches_repository import MatchesRepository
from utils.helpers import (
    format_rank_entry,
    get_queue_display_name,
    get_ranked_entry_for_queue,
    get_ranked_queue_label,
    get_ranked_queue_type,
)
from utils.storage import load_players

WIN_PHRASES = [
    "✅ Сильны... как насчет наконец-то потрогать траву?",
    "✅ Выиграли сильверов, повод для гордости?",
    "✅ Все молодцы, top,mid,jungle,adc,sup diff",
    "✅ Гоооооооооооооол",
    "✅ Некст некст некст",
    "✅ В некст проиграете, не радуйтесь, это всего лишь игра)",
]

LOSS_PHRASES = [
    "❌ У всех бывают поражения)",
    "❌ В некст выиграете, не отчаивайтесь, это всего лишь игра)",
    "❌ Заслуженное поражение",
    "❌ Причина проигрыша? Плохой интернет? Плохой пинг? Плохой компьютер? Плохая мышка? Плохой монитор? Плохая клавиатура? Плохой стул? Плохая комната? Плохая одежда? Плохая еда? Плохой сон? Плохое настроение? Плохая погода? Плохая луна? Плохая звезда?",
    "❌ НЕКСТ НЕКСТ НЕКСТ",
]

WATCHER_PLAYER_DELAY_SECONDS = 1.0

class MatchWatcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.matches_repo = MatchesRepository(bot.db)

        # puuid -> last known match_id
        self.last_match_cache: dict[str, str] = {}

        # чтобы при первом запуске не спамить старыми матчами
        self.first_sync_completed = False

        self.loop.start()

    @tasks.loop(minutes=1)
    async def loop(self):
        try:
            if not os.path.exists("data/players.txt"):
                print("⚠️ Файл data/players.txt не найден")
                return

            tracked_puuids = load_players()
            if not tracked_puuids:
                print("⚠️ players.txt пустой")
                return

            tracked_set = set(tracked_puuids)

            # ---------- Первый запуск ----------
            if not self.first_sync_completed:
                for index, puuid in enumerate(tracked_puuids, start=1):
                    try:
                        recent_match_ids = await self.bot.riot_api.get_recent_matches(puuid, count=1)
                        if not recent_match_ids:
                            continue

                        match_id = recent_match_ids[0]
                        self.last_match_cache[puuid] = match_id

                        exists = await self.matches_repo.match_exists(match_id)
                        if not exists:
                            match_data = await self.bot.riot_api.get_match_details(match_id)
                            if match_data:
                                await self.matches_repo.save_full_match(match_data)
                                print(f"✅ [INIT] Сохранён матч {match_id} для tracked player {puuid}")

                    except Exception as e:
                        print(f"❌ Ошибка initial sync для {puuid}: {e!r}")
                    finally:
                        if index < len(tracked_puuids):
                            await asyncio.sleep(WATCHER_PLAYER_DELAY_SECONDS)

                self.first_sync_completed = True
                print("✅ Initial sync завершён")
                return

            # ---------- Обычный цикл ----------
            # match_id -> set(puuid), чтобы один и тот же матч отправить 1 раз
            new_matches_grouped: dict[str, set[str]] = {}

            for index, puuid in enumerate(tracked_puuids, start=1):
                try:
                    recent_match_ids = await self.bot.riot_api.get_recent_matches(puuid, count=1)
                    if not recent_match_ids:
                        continue

                    latest_match_id = recent_match_ids[0]
                    cached_match_id = self.last_match_cache.get(puuid)

                    # игрок добавлен после запуска
                    if cached_match_id is None:
                        self.last_match_cache[puuid] = latest_match_id

                        exists = await self.matches_repo.match_exists(latest_match_id)
                        if not exists:
                            match_data = await self.bot.riot_api.get_match_details(latest_match_id)
                            if match_data:
                                await self.matches_repo.save_full_match(match_data)
                                print(f"✅ [NEW TRACKED PLAYER] Сохранён матч {latest_match_id} для {puuid}")

                        continue

                    # матч не изменился
                    if latest_match_id == cached_match_id:
                        continue

                    # появился новый матч
                    new_matches_grouped.setdefault(latest_match_id, set()).add(puuid)

                    exists = await self.matches_repo.match_exists(latest_match_id)
                    if not exists:
                        match_data = await self.bot.riot_api.get_match_details(latest_match_id)
                        if match_data:
                            await self.matches_repo.save_full_match(match_data)
                            print(f"🎮 Новый матч {latest_match_id} для tracked player {puuid} сохранён в БД")

                    # обновляем кэш
                    self.last_match_cache[puuid] = latest_match_id

                except Exception as e:
                    print(f"❌ Ошибка проверки игрока {puuid}: {e!r}")
                finally:
                    if index < len(tracked_puuids):
                        await asyncio.sleep(WATCHER_PLAYER_DELAY_SECONDS)

            # ---------- Отправка уведомлений ----------
            if new_matches_grouped:
                for match_id, triggering_puuids in new_matches_grouped.items():
                    try:
                        await self.notify_new_match(match_id, tracked_set, triggering_puuids)
                    except Exception as e:
                        print(f"❌ Ошибка отправки уведомления по матчу {match_id}: {e!r}")
            else:
                print("🟢 Новых матчей нет")

        except Exception as e:
            print(f"❌ Ошибка в MatchWatcher.loop: {e!r}")

    async def notify_new_match(
        self,
        match_id: str,
        tracked_set: set[str],
        triggering_puuids: set[str],
    ) -> None:
        config = load_config()
        channel_id = config.get("notify_channel_id")

        if not channel_id:
            print("⚠️ notify_channel_id не установлен")
            return

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception as e:
                print(f"❌ Не удалось получить канал {channel_id}: {e!r}")
                return

        match_data = await self.matches_repo.get_match_json(match_id)

        # fallback: если в БД вдруг нет raw_json, грузим напрямую
        if not match_data:
            match_data = await self.bot.riot_api.get_match_details(match_id)
            if not match_data:
                print(f"⚠️ Не удалось загрузить матч {match_id} для уведомления")
                return

        info = match_data.get("info", {})
        participants = info.get("participants", [])
        ranked_queue_type = get_ranked_queue_type(info.get("queueId"))
        rank_entry_map: dict[str, dict | None] = {}

        if ranked_queue_type:
            puuids = [
                player.get("puuid")
                for player in participants
                if player.get("puuid")
            ]
            ranked_entries_by_puuid = await self.bot.riot_api.get_ranked_entries_for_puuids(puuids)

            for puuid, ranked_entries in ranked_entries_by_puuid.items():
                rank_entry_map[puuid] = get_ranked_entry_for_queue(
                    ranked_entries,
                    ranked_queue_type,
                )

        embed = self.build_match_notification_embed(
            match_data,
            tracked_set,
            triggering_puuids,
            ranked_queue_type=ranked_queue_type,
            rank_entry_map=rank_entry_map,
        )
        await channel.send(embed=embed)

    def build_match_notification_embed(
        self,
        match_data: dict,
        tracked_set: set[str],
        triggering_puuids: set[str],
        ranked_queue_type: str | None = None,
        rank_entry_map: dict[str, dict | None] | None = None,
    ) -> discord.Embed:
        info = match_data.get("info", {})
        metadata = match_data.get("metadata", {})
        participants = info.get("participants", [])

        match_id = metadata.get("matchId", "Unknown")
        game_start = info.get("gameStartTimestamp")
        game_duration = info.get("gameDuration", 0)

        if game_start:
            try:
                match_time_text = datetime.fromtimestamp(game_start / 1000).strftime("%Y-%m-%d | %H:%M")
            except Exception:
                match_time_text = "Неизвестно"
        else:
            match_time_text = "Неизвестно"

        minutes = game_duration // 60
        seconds = game_duration % 60
        duration_text = f"{minutes}:{seconds:02d}"
        queue_name = get_queue_display_name(info.get("queueId"))
        ranked_queue_label = get_ranked_queue_label(ranked_queue_type)

        blue_team = [p for p in participants if p.get("teamId") == 100]
        red_team = [p for p in participants if p.get("teamId") == 200]

        tracked_players_in_match = [
            p for p in participants
            if p.get("puuid") in tracked_set
        ]

        if tracked_players_in_match:
            is_win = tracked_players_in_match[0].get("win", False)
            result_text = random.choice(WIN_PHRASES if is_win else LOSS_PHRASES)

            tracked_names = []
            for p in tracked_players_in_match:
                riot_name = f"{p.get('riotIdGameName', 'Unknown')}#{p.get('riotIdTagline', 'Unknown')}"
                champion = p.get("championName", "Unknown")
                tracked_names.append(f"• **{riot_name}** — {champion}")

            tracked_players_text = "\n".join(tracked_names)
        else:
            result_text = "🎮 Завершился новый матч"
            tracked_players_text = "Нет игроков из списка"

        description_lines = [
            tracked_players_text,
            "",
            f"**Match ID:** `{match_id}`",
            f"**Тип:** {queue_name}",
        ]
        if ranked_queue_label:
            description_lines.append(f"**Ранги:** {ranked_queue_label}")
        description_lines.extend([
            f"**Start Time:** {match_time_text}",
            f"**Duration:** {duration_text}",
        ])

        embed = discord.Embed(
            title=result_text,
            description="\n".join(description_lines),
            color=discord.Color.green() if tracked_players_in_match and tracked_players_in_match[0].get("win", False)
            else discord.Color.red() if tracked_players_in_match
            else discord.Color.blurple()
        )

        embed.add_field(
            name=f"{'✅' if blue_team and blue_team[0].get('win') else '❌'} Blue Team",
            value=self.format_team(
                blue_team,
                tracked_set,
                ranked_queue_type=ranked_queue_type,
                rank_entry_map=rank_entry_map,
            ),
            inline=True
        )

        embed.add_field(
            name=f"{'✅' if red_team and red_team[0].get('win') else '❌'} Red Team",
            value=self.format_team(
                red_team,
                tracked_set,
                ranked_queue_type=ranked_queue_type,
                rank_entry_map=rank_entry_map,
            ),
            inline=True
        )

        return embed

    def format_team(
        self,
        team: list[dict],
        tracked_set: set[str],
        ranked_queue_type: str | None = None,
        rank_entry_map: dict[str, dict | None] | None = None,
    ) -> str:
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

            marker = "🎯 " if player.get("puuid") in tracked_set else ""
            rank_text = None
            if ranked_queue_type:
                rank_entry = None if rank_entry_map is None else rank_entry_map.get(player.get("puuid"))
                rank_text = format_rank_entry(rank_entry, unranked_text="Unranked")

            stats_line = f"{champion} | {kills}/{deaths}/{assists}"
            if rank_text:
                stats_line += f" | {rank_text}"

            lines.append(
                f"{marker}**{riot_name[:20]}**\n"
                f"{stats_line}\n"
                f"{dpm:.0f} DPM | CS {cs} | Gold {gold}\n"
            )

        text = "\n".join(lines)

        # лимит Discord field = 1024
        if len(text) > 1024:
            text = text[:1021] + "..."

        return text

    @loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
        print("🚀 MatchWatcher запущен")

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ MatchWatcher готов")

    def cog_unload(self):
        self.loop.cancel()


async def setup(bot):
    await bot.add_cog(MatchWatcher(bot))
