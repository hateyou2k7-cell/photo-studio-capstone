from abc import ABC, abstractmethod
from typing import List, Optional
from .equipment import EquipmentDomain


class IEquipmentRepository(ABC):
    @abstractmethod
    def add(self, equipment: EquipmentDomain) -> EquipmentDomain:
        pass

    @abstractmethod
    def get_by_id(self, equipment_id: int) -> Optional[EquipmentDomain]:
        pass

    @abstractmethod
    def list(self, filters: dict = None) -> List[EquipmentDomain]:
        pass

    @abstractmethod
    def update(self, equipment: EquipmentDomain) -> EquipmentDomain:
        pass

    @abstractmethod
    def delete(self, equipment_id: int) -> None:
        pass
