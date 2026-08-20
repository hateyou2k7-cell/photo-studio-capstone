from domain.models.ispace_image_repository import ISpaceImageRepository
from domain.models.space_image import SpaceImage
from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.models.space_management_model import SpaceImage as SpaceImageModel
from infrastructure.databases.factory_database import FactoryDatabase as db_factory


class SpaceImageRepository(ISpaceImageRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, image: SpaceImage) -> SpaceImageModel:
        try:
            model = SpaceImageModel(
                space_id=image.space_id,
                url=image.url,
                is_primary=image.is_primary,
                sort_order=image.sort_order
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not save image')
        finally:
            self.session.close()

    def get_by_id(self, image_id: int) -> Optional[SpaceImageModel]:
        return self.session.query(SpaceImageModel).filter_by(id=image_id).first()

    def list(self, space_id: int) -> List[SpaceImageModel]:
        return self.session.query(SpaceImageModel).filter_by(space_id=space_id).order_by(SpaceImageModel.sort_order).all()

    def update(self, image: SpaceImage) -> SpaceImageModel:
        try:
            model = SpaceImageModel(
                id=image.id,
                space_id=image.space_id,
                url=image.url,
                is_primary=image.is_primary,
                sort_order=image.sort_order,
                created_at=image.created_at
            )
            self.session.merge(model)
            self.session.commit()
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Image not found')
        finally:
            self.session.close()

    def delete(self, image_id: int) -> None:
        try:
            model = self.session.query(SpaceImageModel).filter_by(id=image_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Image not found')
        except Exception:
            self.session.rollback()
            raise ValueError('Image not found')
        finally:
            self.session.close()

    def clear_primary(self, space_id: int) -> None:
        try:
            self.session.query(SpaceImageModel).filter_by(space_id=space_id).update(
                {SpaceImageModel.is_primary: False}
            )
            self.session.commit()
        except Exception:
            self.session.rollback()
        finally:
            self.session.close()