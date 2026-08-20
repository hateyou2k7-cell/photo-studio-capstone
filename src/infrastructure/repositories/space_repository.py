from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from domain.models.ispace_repository import ISpaceRepository
from domain.models.space import Space
from infrastructure.models.film_space_model import Space as SpaceModel, SpaceType
from infrastructure.databases.factory_database import FactoryDatabase as db_factory


class SpaceRepository(ISpaceRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, space: Space) -> SpaceModel:
        try:
            model = SpaceModel(
                provider_id=space.provider_id,
                name=space.name,
                type=SpaceType(space.space_type),
                description=space.description,
                address=space.address,
                max_capacity=space.max_capacity,
                dimensions=space.dimensions,
                art_style=space.art_style,
                lighting=space.lighting,
                ventilation=space.ventilation,
                acoustics=space.acoustics,
                amenities=space.amenities,
                operating_hours=space.operating_hours,
                base_price_per_hour=space.base_price_per_hour,
                status=space.status
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not create space')
        finally:
            self.session.close()

    def get_by_id(self, space_id: int) -> Optional[SpaceModel]:
        return self.session.query(SpaceModel).filter_by(id=space_id).first()

    def list(self) -> List[SpaceModel]:
        return self.session.query(SpaceModel).all()

    def search(self, filters: dict) -> List[SpaceModel]:
        query = self.session.query(SpaceModel)
        q = filters.get('q')
        if q:
            query = query.filter(or_(
                SpaceModel.name.ilike(f'%{q}%'),
                SpaceModel.description.ilike(f'%{q}%'),
                SpaceModel.address.ilike(f'%{q}%'),
            ))
        space_type = filters.get('space_type')
        if space_type:
            query = query.filter(SpaceModel.type == SpaceType(space_type))
        min_price = filters.get('min_price')
        if min_price is not None:
            query = query.filter(SpaceModel.base_price_per_hour >= min_price)
        max_price = filters.get('max_price')
        if max_price is not None:
            query = query.filter(SpaceModel.base_price_per_hour <= max_price)
        min_capacity = filters.get('min_capacity')
        if min_capacity is not None:
            query = query.filter(SpaceModel.max_capacity >= min_capacity)
        if filters.get('available') is not None:
            query = query.filter(SpaceModel.status == filters['available'])
        return query.all()

    def update(self, space: Space) -> SpaceModel:
        try:
            existing = self.session.query(SpaceModel).filter_by(id=space.id).first()
            if not existing:
                raise ValueError('Space not found')
            existing.provider_id = space.provider_id
            existing.name = space.name
            existing.type = SpaceType(space.space_type)
            existing.description = space.description
            existing.address = space.address
            existing.max_capacity = space.max_capacity
            existing.dimensions = space.dimensions
            existing.art_style = space.art_style
            existing.lighting = space.lighting
            existing.ventilation = space.ventilation
            existing.acoustics = space.acoustics
            existing.amenities = space.amenities
            existing.operating_hours = space.operating_hours
            existing.base_price_per_hour = space.base_price_per_hour
            existing.status = space.status
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update space')
        finally:
            self.session.close()

    def delete(self, space_id: int) -> None:
        try:
            model = self.session.query(SpaceModel).filter_by(id=space_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Space not found')
        except Exception:
            self.session.rollback()
            raise ValueError('Space not found')
        finally:
            self.session.close()