# CCG Bot

A Discord bot for tracking League of Legends matches through the Riot API. The project collects statistics for tracked players, stores matches in SQLite, provides detailed team analytics, and automatically sends notifications about new games to Discord.

## About the Project

- slash commands built with `discord.py`
- integration with the `Riot Games API`
- local storage for matches and statistics in `SQLite`
- a background watcher that checks for new matches
- a separate mini-game feature for the Discord server

## Core Features

- View a player's stats for their last 100 matches with `/lolstats`
- Get a detailed breakdown of a specific match with `/matchdetails`
- Check which tracked players are currently in game with `/whoingame`
- Automatically track new matches and send embed notifications to Discord
- Store the list of tracked players and a whitelist of users allowed to run management commands
- Calculate records from saved matches with `/records`
- Play the `/5stars` mini-game for random role assignment while taking each player's unwanted role into account
- Use built-in utility commands to check the bot's status and display help

## Commands

| Command                                        | Description                                                                     |
| ---------------------------------------------- | ------------------------------------------------------------------------------- |
| `/lolstats nickname match_count result_filter` | Shows a player's recent match stats with win/loss filtering                     |
| `/matchdetails nickname match_number`          | Shows a detailed breakdown of a selected match from the player's history        |
| `/whoingame`                                   | Checks which tracked players are currently in an active game                    |
| `/playerslol`                                  | Displays the list of tracked players                                            |
| `/addplayer nickname`                          | Adds a player to tracking                                                       |
| `/removeplayer nickname`                       | Removes a player from tracking                                                  |
| `/allowuser user`                              | Adds a user to the whitelist for management commands                            |
| `/disallowuser user`                           | Removes a user from the whitelist                                               |
| `/setchannel`                                  | Sets the current channel as the match notification channel                      |
| `/records`                                     | Shows the best records for tracked players based on saved matches               |
| `/5stars`                                      | Starts a mini-game for 5 players with random role assignment                    |
| `/ping`                                        | Checks whether the bot is available                                             |
| `/helplol`                                     | Displays command help                                                           |

## Architecture

The project is split into several logical layers:

- `bot.py` initializes the Discord bot, Riot API client, database, and extensions
- `cogs/` contains the user-facing slash commands
- `services/` contains background processes that run independently of manual commands
- `riot/riot_api.py` encapsulates the Riot API integration
- `db/` is responsible for the schema, SQLite connection, and repository layer
- `utils/` contains file-based storage, helpers, and declarative record definitions
- `data/` stores configs, player lists, the whitelist, and the local database

### What Is Stored in the Database

- `players` - tracked players and their Riot IDs
- `matches` - saved matches and raw JSON responses from the Riot API
- `player_match_stats` - aggregated statistics for tracked players across matches

## Repository Structure

```text
CCG bot/
|- bot.py
|- config.py
|- settings.py
|- debug_db.py
|- cogs/
|  |- admin.py
|  |- game.py
|  |- lol.py
|  |- misc.py
|  |- players.py
|  \- records.py
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

## Technologies

- Python 3.11+
- `discord.py`
- `aiohttp`
- `aiosqlite`
- `python-dotenv`
- Riot Games API
- SQLite

## Running Locally

### 1. Install Dependencies

```bash
pip install discord.py aiohttp aiosqlite python-dotenv requests flask
```

### 2. Create `.env`

```env
DISCORD_TOKEN=your_discord_bot_token
RIOT_API_KEY=your_riot_api_key
```

### 3. Start the Bot

```bash
python bot.py
```

On first launch, the bot will:

- connect to Discord
- create or initialize the SQLite database from `db/schema.sql`
- load the list of champions
- register slash commands and start the background watcher

## Important Data Files

- `data/players.txt` - list of tracked players by `puuid`
- `data/allowed_users.txt` - whitelist of Discord users allowed to run management commands
- `data/config.json` - config file containing `notify_channel_id`
- `data/riftwatcher.db` - local database for matches and statistics

## What This Project Demonstrates

From a resume or portfolio perspective, this project demonstrates:

- working with an external REST API
- building an asynchronous Python application
- designing a repository layer and SQLite schema
- handling background tasks and periodic polling
- storing and reusing raw data
- developing user-facing Discord functionality

## Possible Improvements

- move dependencies into a root `requirements.txt`
- add tests for the repository layer and business logic
- set up Docker packaging and deployment
- add caching and more careful Riot API rate limit handling
- add CI for linting and verification
