from domain.models.ispace_schedule_repository import ISpaceScheduleRepository
from domain.models.space_schedule import SpaceSchedule
from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.models.space_management_model import SpaceSchedule as SpaceScheduleModel
from infrastructure.databases.factory_database import FactoryDatabase as db_factory


class SpaceScheduleRepository(ISpaceScheduleRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, schedule: SpaceSchedule) -> SpaceScheduleModel:
        try:
            model = SpaceScheduleModel(
                space_id=schedule.space_id,
                day_of_week=schedule.day_of_week,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                is_available=schedule.is_available
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not create schedule slot')
        finally:
            self.session.close()

    def get_by_id(self, schedule_id: int) -> Optional[SpaceScheduleModel]:
        return self.session.query(SpaceScheduleModel).filter_by(id=schedule_id).first()

    def list(self, space_id: int) -> List[SpaceScheduleModel]:
        return self.session.query(SpaceScheduleModel).filter_by(space_id=space_id).all()

    def update(self, schedule: SpaceSchedule) -> SpaceScheduleModel:
        try:
            model = SpaceScheduleModel(
                id=schedule.id,
                space_id=schedule.space_id,
                day_of_week=schedule.day_of_week,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                is_available=schedule.is_available,
                created_at=schedule.created_at,
                updated_at=schedule.updated_at
            )
            self.session.merge(model)
            self.session.commit()
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Schedule slot not found')
        finally:
            self.session.close()

    def delete(self, schedule_id: int) -> None:
        try:
            model = self.session.query(SpaceScheduleModel).filter_by(id=schedule_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Schedule slot not found')
        except Exception:
            self.session.rollback()
            raise ValueError('Schedule slot not found')
        finally:
            self.session.close()