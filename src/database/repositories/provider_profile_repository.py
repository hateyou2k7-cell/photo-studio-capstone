from typing import List, Optional
from sqlalchemy.orm import Session
from business.models.iprovider_profile_repository import IProviderProfileRepository
from business.models.provider_profile import ProviderProfile
from database.databases.factory_database import FactoryDatabase as db_factory


class ProviderProfileRepository(IProviderProfileRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def _get_model(self):
        from database.models.film_user_model import ProviderProfile as ProviderProfileModel
        return ProviderProfileModel

    def add(self, profile: ProviderProfile):
        Model = self._get_model()
        try:
            model = Model(
                user_id=profile.user_id,
                business_name=profile.business_name,
                description=profile.description,
                address=profile.address,
                status=profile.status
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not create provider profile')

    def get_by_id(self, profile_id: int):
        Model = self._get_model()
        return self.session.query(Model).filter_by(id=profile_id).first()

    def get_by_user_id(self, user_id: int):
        Model = self._get_model()
        return self.session.query(Model).filter_by(user_id=user_id).first()

    def list(self):
        Model = self._get_model()
        return self.session.query(Model).all()

    def update(self, profile: ProviderProfile):
        Model = self._get_model()
        try:
            existing = self.session.query(Model).filter_by(id=profile.id).first()
            if not existing:
                raise ValueError('Provider profile not found')
            existing.business_name = profile.business_name
            existing.description = profile.description
            existing.address = profile.address
            existing.status = profile.status
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update provider profile')

    def delete(self, profile_id: int) -> None:
        Model = self._get_model()
        try:
            model = self.session.query(Model).filter_by(id=profile_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Provider profile not found')
        except ValueError:
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Provider profile not found')
