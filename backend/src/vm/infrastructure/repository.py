from typing import Any

import asyncpg
import bcrypt

from .db_api import DbApi
from ..application import IVMRepository


class VMRepository(IVMRepository):
    def __init__(self, db_api: DbApi) -> None:
        self._db = db_api

    async def create_vm(self, ram: int, cpu: int, password: str) -> int:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        vm_id = await self._db.fetchone(
            "INSERT INTO virtual_machines (ram, cpu, password) VALUES ($1, $2, $3) RETURNING id",
            ram, cpu, hashed_password.decode()
        )
        return vm_id['id']

    async def get_all_vms(self) -> list[asyncpg.Record]:
        return await self._db.fetch("SELECT id, ram, cpu FROM virtual_machines")

    async def update_vm(self, vm_id: int, **kwargs: Any) -> None:
        set_clause = ", ".join(f"{key} = ${i + 1}" for i, key in enumerate(kwargs.keys()))
        values = list(kwargs.values())
        values.append(vm_id)

        query = f"UPDATE virtual_machines SET {set_clause} WHERE id = ${len(values)}"
        await self._db.execute(query, *values)

    async def authenticate_vm(self, vm_id: int, password: str) -> bool:
        vm = await self._db.fetchone(
            "SELECT password FROM virtual_machines WHERE id = $1",
            vm_id
        )
        if vm and bcrypt.checkpw(password.encode(), vm['password'].encode()):
            await self.update_vm(vm_id, authorized=True)
            return True
        return False

    async def get_all_connected_vms(self) -> list[asyncpg.Record]:
        return await self._db.fetch("SELECT id, ram, cpu FROM virtual_machines WHERE connected = TRUE")

    async def get_all_authorized_vms(self) -> list[asyncpg.Record]:
        return await self._db.fetch("SELECT id, ram, cpu FROM virtual_machines WHERE authorized = TRUE")

    async def get_all_disks(self) -> list[asyncpg.Record]:
        return await self._db.fetch("SELECT id, size, vm_id FROM disks")
