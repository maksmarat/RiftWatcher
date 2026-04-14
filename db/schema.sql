PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    puuid TEXT NOT NULL UNIQUE,
    game_name TEXT,
    tag_line TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS matches (
    match_id TEXT PRIMARY KEY,
    game_start TIMESTAMP,
    game_duration INTEGER,
    queue_id INTEGER,
    map_id INTEGER,
    raw_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS player_match_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id TEXT NOT NULL,
    puuid TEXT NOT NULL,
    riot_id TEXT,
    champion_name TEXT,
    kills INTEGER NOT NULL DEFAULT 0,
    deaths INTEGER NOT NULL DEFAULT 0,
    assists INTEGER NOT NULL DEFAULT 0,
    win INTEGER NOT NULL DEFAULT 0,
    team_id INTEGER,
    damage_per_minute REAL NOT NULL DEFAULT 0,
    cs INTEGER NOT NULL DEFAULT 0,
    gold_earned INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(match_id, puuid),
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (puuid) REFERENCES players(puuid) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_players_puuid
ON players (puuid);

CREATE INDEX IF NOT EXISTS idx_matches_game_start
ON matches (game_start DESC);

CREATE INDEX IF NOT EXISTS idx_player_match_stats_puuid
ON player_match_stats (puuid);

CREATE INDEX IF NOT EXISTS idx_player_match_stats_match_id
ON player_match_stats (match_id);

CREATE INDEX IF NOT EXISTS idx_player_match_stats_puuid_match_id
ON player_match_stats (puuid, match_id);