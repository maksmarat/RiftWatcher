from __future__ import annotations

import aiosqlite
from pathlib import Path


DB_PATH = Path("data/riftwatcher.db")
SCHEMA_PATH = Path("db/schema.sql")


class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self.connection.execute("PRAGMA foreign_keys = ON;")
        await self.connection.commit()

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    async def init_schema(self) -> None:
        if self.connection is None:
            raise RuntimeError("Database is not connected")

        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        await self.connection.executescript(schema_sql)
        await self.connection.commit()

    async def execute(self, query: str, params: tuple = ()) -> aiosqlite.Cursor:
        if self.connection is None:
            raise RuntimeError("Database is not connected")

        cursor = await self.connection.execute(query, params)
        await self.connection.commit()
        return cursor

    async def executemany(self, query: str, params_list: list[tuple]) -> None:
        if self.connection is None:
            raise RuntimeError("Database is not connected")

        await self.connection.executemany(query, params_list)
        await self.connection.commit()

    async def fetchone(self, query: str, params: tuple = ()) -> aiosqlite.Row | None:
        if self.connection is None:
            raise RuntimeError("Database is not connected")

        cursor = await self.connection.execute(query, params)
        row = await cursor.fetchone()
        await cursor.close()
        return row

    async def fetchall(self, query: str, params: tuple = ()) -> list[aiosqlite.Row]:
        if self.connection is None:
            raise RuntimeError("Database is not connected")

        cursor = await self.connection.execute(query, params)
        rows = await cursor.fetchall()
        await cursor.close()
        return rows