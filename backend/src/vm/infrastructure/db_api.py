from typing import Any, AsyncIterable

import asyncpg

from .config import Config


class DbApi:
    def __init__(self, connection: asyncpg.Connection) -> None:
        self._conn = connection

    async def execute(self, query: str, *args: Any) -> None:
        await self._conn.execute(query, *args)

    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        return await self._conn.fetch(query, *args)

    async def fetchone(self, query: str, *args: Any) -> asyncpg.Record:
        return await self._conn.fetchrow(query, *args)


class CreateTable:
    def __init__(self, db_api: "DbApi") -> None:
        self._db = db_api

    async def _create_vm_table(self) -> None:
        columns = [
            "id SERIAL PRIMARY KEY",
            "ram INTEGER NOT NULL",
            "cpu INTEGER NOT NULL",
            "password TEXT NOT NULL",
            "authorized BOOLEAN DEFAULT FALSE",
            "connected BOOLEAN DEFAULT FALSE"
        ]
        await self._create_table(title="virtual_machines", columns=columns)

    async def _create_disk_table(self) -> None:
        columns = [
            "id SERIAL PRIMARY KEY",
            "vm_id INTEGER REFERENCES virtual_machines(id) ON DELETE CASCADE",
            "size INTEGER NOT NULL"
        ]
        await self._create_table(title="disks", columns=columns)

    async def _create_table(self, title: str, columns: list[str]) -> None:
        query = f"CREATE TABLE IF NOT EXISTS {title} ({', '.join(columns)})"
        await self._db.execute(query)

    async def create_tables(self) -> None:
        await self._create_vm_table()
        await self._create_disk_table()


class DatabaseProvider:

    def __init__(self, cfg: "Config") -> None:
        self.config = cfg
        self._pool = None

    async def construct_pool(self) -> AsyncIterable[asyncpg.Pool]:
        self._pool = await asyncpg.create_pool(
            user=self.config.db.user,
            password=self.config.db.password,
            host=self.config.db.host,
            port=self.config.db.port,
            database=self.config.db.database
        )
        yield self._pool
        await self._pool.close()

    async def provide_connection(self) -> AsyncIterable[asyncpg.Connection]:
        if self._pool is None:
            raise Exception("Pool is not initialized. Call construct_pool first.")

        async with self._pool.acquire() as conn:
            async with conn.transaction():
                yield conn
