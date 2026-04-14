from __future__ import annotations

from db.database import Database


class PlayersRepository:
    def __init__(self, db: Database):
        self.db = db

    async def upsert_player(self, puuid: str, game_name: str | None, tag_line: str | None) -> None:
        await self.db.execute(
            """
            INSERT INTO players (puuid, game_name, tag_line, is_active)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(puuid) DO UPDATE SET
                game_name = excluded.game_name,
                tag_line = excluded.tag_line,
                is_active = 1
            """,
            (puuid, game_name, tag_line),
        )

    async def get_player_by_puuid(self, puuid: str):
        return await self.db.fetchone(
            "SELECT * FROM players WHERE puuid = ?",
            (puuid,),
        )

    async def get_all_active_players(self):
        return await self.db.fetchall(
            "SELECT * FROM players WHERE is_active = 1 ORDER BY game_name, tag_line"
        )

    async def deactivate_player(self, puuid: str) -> None:
        await self.db.execute(
            "UPDATE players SET is_active = 0 WHERE puuid = ?",
            (puuid,),
        )