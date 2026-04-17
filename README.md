# CCG Bot

CCG Bot is a Discord bot for tracking League of Legends matches for a curated group of players. It syncs match history through the Riot API, stores raw match payloads and derived stats in SQLite, and exposes slash commands for match analysis, shared-game search, live status checks, records, and automated post-match notifications.

## Overview

The project is built around three ideas:

- keep a local, queryable history of tracked players
- enrich Riot match data with practical Discord-facing analytics
- automate routine server tasks such as match notifications and player management

The bot uses slash commands built on `discord.py`, a lightweight SQLite persistence layer, and a background watcher that keeps recent matches in sync.

## Features

### Match Analytics

- `/lolstats` syncs recent matches for a player and shows a paginated history view
- queue filters are available for solo queue, flex, arena, normal games, and ARAM
- result filters are available for wins, losses, or all matches
- current solo queue and flex rank information is shown alongside match history when available
- `/matchdetails` expands a selected match into full blue/red team breakdowns with KDA, DPM, CS, gold, queue name, and duration
- ranked queue match details also include current participant rank text for the relevant queue
- `/records` calculates best stored performances across tracked players
- `/dbstats` summarizes the local dataset, including players, matches, stored stat rows, total playtime, average game length, and total question-mark pings

### Search and Comparison

- `/search` supports champion search across a player's stored matches or shared-match search for one player plus up to four additional Riot IDs
- champion search includes autocomplete from the loaded Riot champion dataset
- search results are paginated and highlight matched players directly inside the team view
- shared-match searches also return a compact summary of the group's combined win rate

### Tracking and Notifications

- tracked players are polled automatically every minute in the background
- the watcher performs an initial sync to avoid replaying old matches as fresh notifications
- new matches are stored once even if multiple tracked players were in the same game
- notifications are grouped per match and sent only once to the configured Discord channel
- ranked queue notifications include queue labels and current rank text for participants
- ranked entry lookups are cached briefly to reduce repeated Riot API calls during command usage and background sync

### Server Utilities

- `/playerslol` lists the currently tracked players
- `/addplayer` and `/removeplayer` manage the tracked player list
- `/allowuser` and `/disallowuser` manage the local whitelist for player-list administration
- `/setchannel` stores the Discord channel used for automatic match notifications
- `/whoingame` checks which tracked players are currently in an active game
- `/ping` and `/helplol` provide health and command discovery utilities
- `/5stars` runs a role-draw mini-game for five players with one disliked role per user

## Commands

All Riot player arguments use the `gameName#tagLine` format.

| Command | Description |
| --- | --- |
| `/lolstats nickname [count] [queue] [result]` | Sync recent matches for a player and show paginated match history with optional queue and result filters. |
| `/matchdetails nickname match_number` | Show a detailed breakdown of a match using the numbering from `/lolstats`. |
| `/search nickname [character_name] [nickname_2] [nickname_3] [nickname_4] [nickname_5]` | Search a player's stored matches either by champion or by shared games with other players. |
| `/whoingame` | Check which tracked players are currently in an active match. |
| `/records` | Show the best saved records across tracked players. |
| `/dbstats` | Show summary statistics for the local SQLite dataset. |
| `/playerslol` | Show the current tracked player list. |
| `/addplayer nickname` | Add a player to tracking. |
| `/removeplayer nickname` | Remove a player from tracking. |
| `/allowuser user` | Allow a Discord user to manage tracked players. |
| `/disallowuser user` | Remove player-management access from a Discord user. |
| `/setchannel` | Set the current channel as the notification channel. |
| `/5stars` | Start the role-draw mini-game for five players. |
| `/ping` | Check whether the bot is responsive. |
| `/helplol` | Show the built-in command help embed. |

## Command Notes

- Omitting `count` in `/lolstats` uses all matches currently stored in the local database for that player.
- `/search` accepts either `character_name` or additional player nicknames, not both in the same request.
- `/matchdetails` uses the same match numbering order as `/lolstats`, where `1` is the newest match.

## Architecture

The codebase is organized into a small set of focused layers:

- `bot.py` initializes the Discord client, Riot API client, database connection, champion metadata, and extensions
- `cogs/` contains the user-facing slash command groups
- `services/match_watcher.py` handles background polling, synchronization, and notification delivery
- `riot/riot_api.py` wraps Riot account, match, spectator, and ranked-entry requests
- `db/` contains the schema, SQLite wrapper, and repository layer
- `utils/` contains flat-file storage helpers and shared formatting/filtering utilities
- `data/` stores the local SQLite database and file-based configuration

### Storage Model

| Table | Purpose |
| --- | --- |
| `players` | Stores known Riot identities by `puuid`. |
| `matches` | Stores saved matches, queue metadata, timing, and raw Riot JSON payloads. |
| `player_match_stats` | Stores derived per-player metrics for tracked participants. |

### File-Based Data

- `data/players.txt` stores tracked `puuid` values
- `data/allowed_users.txt` stores the Discord whitelist for player-management commands
- `data/config.json` stores runtime configuration such as `notify_channel_id`
- `data/riftwatcher.db` stores the SQLite database used by the bot

## Repository Structure

```text
CCG bot/
|- bot.py
|- config.py
|- settings.py
|- debug_db.py
|- README.md
|- README_ru.md
|- cogs/
|  |- admin.py
|  |- game.py
|  |- lol.py
|  |- misc.py
|  |- players.py
|  |- records.py
|  \- search.py
|- services/
|  \- match_watcher.py
|- riot/
|  \- riot_api.py
|- db/
|  |- database.py
|  |- schema.sql
|  \- repositories/
|     |- matches_repository.py
|     \- players_repository.py
|- utils/
|  |- helpers.py
|  |- record_definitions.py
|  \- storage.py
\- data/
   |- allowed_users.txt
   |- config.json
   |- players.txt
   \- riftwatcher.db
```

## Tech Stack

- Python 3.11+
- `discord.py`
- `aiohttp`
- `aiosqlite`
- `python-dotenv`
- SQLite
- Riot Games API

## Getting Started

### 1. Install Dependencies

```bash
pip install discord.py aiohttp aiosqlite python-dotenv
```

### 2. Create `.env`

```env
DISCORD_TOKEN=your_discord_bot_token
RIOT_API_KEY=your_riot_api_key
```

### 3. Run the Bot

```bash
python bot.py
```

On startup, the bot will:

- connect to Discord
- initialize the SQLite schema from `db/schema.sql`
- download champion metadata from Data Dragon
- load all command cogs and the background watcher

## What the Project Covers

From an engineering and portfolio perspective, the project demonstrates:

- asynchronous Python application design
- Discord slash command development with `discord.py`
- Riot API integration for account, match, spectator, and ranked data
- local persistence with SQLite and a repository-style data access layer
- background polling and notification fan-out
- derived analytics computed from raw third-party API payloads
