from .interface import IVMRepository


class CommandHandler:
    def __init__(self, repository: IVMRepository):
        self._repo = repository

    async def handle_login(self, vm_id: int, password: str) -> str:
        authenticated = await self._repo.authenticate_vm(vm_id, password)
        return "Login successful" if authenticated else "Login failed"

    async def handle_logout(self, vm_id: int) -> None:
        return await self._repo.update_vm(vm_id=vm_id, authorized=False)

    async def handle_add_vm(self, ram: int, cpu: int, password: str) -> str:
        vm_id = await self._repo.create_vm(ram, cpu, password)
        return f"VM added with ID {vm_id}"

    async def handle_list_vms(self) -> str:
        vms = await self._repo.get_all_vms()
        return "\n".join([f"VM {vm['id']}: RAM={vm['ram']}, CPU={vm['cpu']}" for vm in vms])

    async def handle_list_authorized_vms(self) -> str:
        vms = await self._repo.get_all_authorized_vms()
        return "\n".join([f"VM {vm['id']}: RAM={vm['ram']}, CPU={vm['cpu']}" for vm in vms])

    async def handle_list_all_connected_vms(self) -> str:
        vms = await self._repo.get_all_connected_vms()
        return "\n".join([f"VM {vm['id']}: RAM={vm['ram']}, CPU={vm['cpu']}" for vm in vms])

    async def handle_update_vm(self, vm_id: int, ram: int, cpu: int) -> str:
        await self._repo.update_vm(vm_id, ram=ram, cpu=cpu)
        return "VM updated"

    async def handle_list_disks(self) -> str:
        disks = await self._repo.get_all_disks()
        return "\n".join([f"Disk {disk['id']}: Size={disk['size']}, VM ID={disk['vm_id']}" for disk in disks])

