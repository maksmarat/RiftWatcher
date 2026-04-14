from __future__ import annotations

import os
import aiohttp
from pathlib import Path


PLAYERS_PATH = Path("data/players.txt")
ALLOWED_USERS_PATH = Path("data/allowed_users.txt")

async def load_champions():

    url = "https://ddragon.leagueoflegends.com/cdn/16.1.1/data/en_US/champion.json"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    return {
        int(champ["key"]): champ["name"]
        for champ in data["data"].values()
    }

def _load_lines(path: Path) -> list[str]:
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def _save_lines(path: Path, values: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    unique_values = list(dict.fromkeys(values))
    temp_path = path.with_suffix(".tmp")

    with open(temp_path, "w", encoding="utf-8") as f:
        for value in unique_values:
            f.write(f"{value}\n")

    os.replace(temp_path, path)


# ---------- tracked players ----------
def load_players() -> list[str]:
    return _load_lines(PLAYERS_PATH)


def save_players(players: list[str]) -> None:
    _save_lines(PLAYERS_PATH, players)


def add_player(puuid: str) -> bool:
    players = load_players()
    if puuid in players:
        return False

    players.append(puuid)
    save_players(players)
    return True


def remove_player(puuid: str) -> bool:
    players = load_players()
    if puuid not in players:
        return False

    players.remove(puuid)
    save_players(players)
    return True


# ---------- discord allowed users ----------
def load_allowed_users() -> list[int]:
    raw = _load_lines(ALLOWED_USERS_PATH)
    result = []

    for value in raw:
        try:
            result.append(int(value))
        except ValueError:
            pass

    return result


def save_allowed_users(user_ids: list[int]) -> None:
    _save_lines(ALLOWED_USERS_PATH, [str(user_id) for user_id in user_ids])


def add_allowed_user(user_id: int) -> bool:
    users = load_allowed_users()
    if user_id in users:
        return False

    users.append(user_id)
    save_allowed_users(users)
    return True


def remove_allowed_user(user_id: int) -> bool:
    users = load_allowed_users()
    if user_id not in users:
        return False

    users.remove(user_id)
    save_allowed_users(users)
    return True


def is_user_allowed(user_id: int) -> bool:
    return user_id in load_allowed_users()