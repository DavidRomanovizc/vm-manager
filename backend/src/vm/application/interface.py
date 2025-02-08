import abc
from typing import Any


class IVMRepository(abc.ABC):
    @abc.abstractmethod
    async def create_vm(self, ram: int, cpu: int, password: str) -> int:
        """Создает новую виртуальную машину и возвращает её ID"""
        pass

    @abc.abstractmethod
    async def get_all_vms(self) -> list:
        """Возвращает список всех виртуальных машин"""
        pass

    @abc.abstractmethod
    async def update_vm(self, vm_id: int, **kwargs: Any) -> None:
        """Обновляет параметры виртуальной машины"""
        pass

    @abc.abstractmethod
    async def authenticate_vm(self, vm_id: int, password: str) -> bool:
        """Аутентифицирует виртуальную машину по ID и паролю"""
        pass

    @abc.abstractmethod
    async def get_all_connected_vms(self) -> list:
        """Возвращает список всех когда-либо подключавшихся виртуальных машин"""
        pass

    @abc.abstractmethod
    async def get_all_disks(self) -> list:
        """Возвращает список всех жестких дисков с их параметрами и привязкой к виртуальным машинам"""
        pass

    @abc.abstractmethod
    async def get_all_authorized_vms(self) -> list:
        """Возвращает список авторизованных виртуальных машин"""
        pass
