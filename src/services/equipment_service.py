from typing import List, Optional
from domain.models.equipment import EquipmentDomain
from domain.models.iequipment_repository import IEquipmentRepository

EQUIPMENT_TYPES = {'enlarger', 'camera', 'scanner', 'lighting', 'tripod', 'tank', 'other'}
EQUIPMENT_CONDITIONS = {'excellent', 'good', 'fair', 'poor', 'broken'}


class EquipmentService:
    def __init__(self, repository: IEquipmentRepository):
        self.repository = repository

    def create(self, provider_id: int, name: str, equipment_type: str, space_id=None,
               model_name=None, compatibility=None, condition='good', description=None,
               price_per_hour=0, is_available=True) -> EquipmentDomain:
        if equipment_type not in EQUIPMENT_TYPES:
            raise ValueError(f"equipment_type must be one of: {', '.join(EQUIPMENT_TYPES)}")
        if condition not in EQUIPMENT_CONDITIONS:
            raise ValueError(f"condition must be one of: {', '.join(EQUIPMENT_CONDITIONS)}")
        equipment = EquipmentDomain(
            provider_id=provider_id, space_id=space_id, name=name, model_name=model_name,
            equipment_type=equipment_type, compatibility=compatibility, condition=condition,
            description=description, price_per_hour=price_per_hour, is_available=is_available,
        )
        return self.repository.add(equipment)

    def get(self, equipment_id: int) -> Optional[EquipmentDomain]:
        return self.repository.get_by_id(equipment_id)

    def list(self, filters: dict = None) -> List[EquipmentDomain]:
        return self.repository.list(filters)

    def update(self, equipment_id: int, **kwargs) -> EquipmentDomain:
        existing = self.repository.get_by_id(equipment_id)
        if not existing:
            raise ValueError('Equipment not found')
        eq_type = kwargs.get('equipment_type')
        if eq_type and eq_type not in EQUIPMENT_TYPES:
            raise ValueError(f"equipment_type must be one of: {', '.join(EQUIPMENT_TYPES)}")
        condition = kwargs.get('condition')
        if condition and condition not in EQUIPMENT_CONDITIONS:
            raise ValueError(f"condition must be one of: {', '.join(EQUIPMENT_CONDITIONS)}")
        equipment = EquipmentDomain(id=equipment_id, **kwargs)
        return self.repository.update(equipment)

    def delete(self, equipment_id: int) -> None:
        existing = self.repository.get_by_id(equipment_id)
        if not existing:
            raise ValueError('Equipment not found')
        self.repository.delete(equipment_id)
