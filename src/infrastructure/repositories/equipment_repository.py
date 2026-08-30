from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from domain.models.iequipment_repository import IEquipmentRepository
from domain.models.equipment import EquipmentDomain
from infrastructure.models.equipment_model import Equipment as EquipmentModel
from infrastructure.databases.factory_database import FactoryDatabase as db_factory


class EquipmentRepository(IEquipmentRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, equipment: EquipmentDomain) -> EquipmentModel:
        try:
            model = EquipmentModel(
                provider_id=equipment.provider_id,
                space_id=equipment.space_id,
                name=equipment.name,
                model_name=equipment.model_name,
                type=equipment.equipment_type,
                compatibility=equipment.compatibility,
                condition=equipment.condition,
                description=equipment.description,
                price_per_hour=equipment.price_per_hour,
                is_available=equipment.is_available,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not create equipment')

    def get_by_id(self, equipment_id: int) -> Optional[EquipmentModel]:
        return self.session.query(EquipmentModel).filter_by(id=equipment_id).first()

    def list(self, filters: dict = None) -> List[EquipmentModel]:
        query = self.session.query(EquipmentModel)
        if filters:
            q = filters.get('q')
            if q:
                query = query.filter(or_(
                    EquipmentModel.name.ilike(f'%{q}%'),
                    EquipmentModel.description.ilike(f'%{q}%'),
                    EquipmentModel.model_name.ilike(f'%{q}%'),
                ))
            eq_type = filters.get('type')
            if eq_type:
                query = query.filter(EquipmentModel.type == eq_type)
            space_id = filters.get('space_id')
            if space_id is not None:
                query = query.filter(EquipmentModel.space_id == space_id)
            available = filters.get('available')
            if available is not None:
                query = query.filter(EquipmentModel.is_available == available)
        return query.all()

    def update(self, equipment: EquipmentDomain) -> EquipmentModel:
        try:
            existing = self.session.query(EquipmentModel).filter_by(id=equipment.id).first()
            if not existing:
                raise ValueError('Equipment not found')
            if equipment.name is not None:
                existing.name = equipment.name
            if equipment.model_name is not None:
                existing.model_name = equipment.model_name
            if equipment.equipment_type is not None:
                existing.type = equipment.equipment_type
            if equipment.compatibility is not None:
                existing.compatibility = equipment.compatibility
            if equipment.condition is not None:
                existing.condition = equipment.condition
            if equipment.description is not None:
                existing.description = equipment.description
            if equipment.price_per_hour is not None:
                existing.price_per_hour = equipment.price_per_hour
            if equipment.is_available is not None:
                existing.is_available = equipment.is_available
            if equipment.space_id is not None:
                existing.space_id = equipment.space_id
            existing.updated_at = func.now()
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update equipment')

    def delete(self, equipment_id: int) -> None:
        try:
            model = self.session.query(EquipmentModel).filter_by(id=equipment_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Equipment not found')
        except ValueError:
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not delete equipment')
