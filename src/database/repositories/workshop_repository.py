from typing import List, Optional
from sqlalchemy.orm import Session
from business.models.iworkshop_repository import IWorkshopRepository
from business.models.workshop import Workshop, WorkshopRegistration
from database.models.film_community_model import Workshop as WorkshopModel, WorkshopRegistration as RegistrationModel
from database.databases.factory_database import FactoryDatabase as db_factory


class WorkshopRepository(IWorkshopRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, workshop: Workshop) -> WorkshopModel:
        try:
            model = WorkshopModel(
                expert_id=workshop.expert_id,
                title=workshop.title,
                description=workshop.description,
                scheduled_at=workshop.scheduled_at,
                location=workshop.location,
                capacity=workshop.capacity,
                price=workshop.price,
                status=workshop.status,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception as e:
            self.session.rollback()
            raise ValueError('Could not create workshop')

    def get_by_id(self, workshop_id: int) -> Optional[WorkshopModel]:
        return self.session.query(WorkshopModel).filter_by(id=workshop_id).first()

    def list(self, expert_id=None, status=None) -> List[WorkshopModel]:
        query = self.session.query(WorkshopModel)
        if expert_id is not None:
            query = query.filter_by(expert_id=expert_id)
        if status is not None:
            query = query.filter_by(status=status)
        return query.order_by(WorkshopModel.scheduled_at.desc()).all()

    def update(self, workshop: Workshop) -> WorkshopModel:
        try:
            existing = self.session.query(WorkshopModel).filter_by(id=workshop.id).first()
            if not existing:
                raise ValueError('Workshop not found')
            existing.title = workshop.title
            existing.description = workshop.description
            existing.scheduled_at = workshop.scheduled_at
            existing.location = workshop.location
            existing.capacity = workshop.capacity
            existing.price = workshop.price
            existing.status = workshop.status
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update workshop')

    def delete(self, workshop_id: int) -> None:
        try:
            model = self.session.query(WorkshopModel).filter_by(id=workshop_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Workshop not found')
        except ValueError:
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not delete workshop')

    def register(self, registration: WorkshopRegistration) -> RegistrationModel:
        try:
            existing = self.session.query(RegistrationModel).filter_by(
                workshop_id=registration.workshop_id,
                user_id=registration.user_id,
            ).first()
            if existing:
                raise ValueError('Already registered for this workshop')
            model = RegistrationModel(
                workshop_id=registration.workshop_id,
                user_id=registration.user_id,
                status=registration.status,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not register for workshop')

    def list_registrations(self, workshop_id: int) -> List[RegistrationModel]:
        return self.session.query(RegistrationModel).filter_by(workshop_id=workshop_id).order_by(RegistrationModel.registered_at.asc()).all()

    def cancel_registration(self, registration_id: int) -> RegistrationModel:
        try:
            existing = self.session.query(RegistrationModel).filter_by(id=registration_id).first()
            if not existing:
                raise ValueError('Registration not found')
            existing.status = 'cancelled'
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not cancel registration')

    def count_registrations(self, workshop_id: int) -> int:
        return self.session.query(RegistrationModel).filter_by(
            workshop_id=workshop_id,
            status='registered',
        ).count()
