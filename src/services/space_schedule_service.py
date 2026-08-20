from typing import List, Optional
from datetime import datetime
from domain.models.space_schedule import SpaceSchedule
from domain.models.ispace_schedule_repository import ISpaceScheduleRepository

DAYS = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']


class SpaceScheduleService:
    def __init__(self, repository: ISpaceScheduleRepository):
        self.repository = repository

    def create(self, space_id: int, day_of_week: int, start_time, end_time,
               is_available: bool = True) -> SpaceSchedule:
        if day_of_week < 0 or day_of_week > 6:
            raise ValueError('day_of_week must be between 0 (Sunday) and 6 (Saturday)')
        if end_time <= start_time:
            raise ValueError('end_time must be after start_time')
        schedule = SpaceSchedule(id=None, space_id=space_id, day_of_week=day_of_week,
                                 start_time=start_time, end_time=end_time,
                                 is_available=is_available, created_at=None, updated_at=None)
        return self.repository.add(schedule)

    def list(self, space_id: int) -> List[SpaceSchedule]:
        return self.repository.list(space_id)

    def update(self, schedule_id: int, space_id: int, day_of_week: int, start_time,
               end_time, is_available: bool) -> SpaceSchedule:
        existing = self.repository.get_by_id(schedule_id)
        if not existing or existing.space_id != space_id:
            raise ValueError('Schedule slot not found')
        if day_of_week < 0 or day_of_week > 6:
            raise ValueError('day_of_week must be between 0 (Sunday) and 6 (Saturday)')
        if end_time <= start_time:
            raise ValueError('end_time must be after start_time')
        schedule = SpaceSchedule(id=schedule_id, space_id=space_id, day_of_week=day_of_week,
                                 start_time=start_time, end_time=end_time,
                                 is_available=is_available,
                                 created_at=existing.created_at,
                                 updated_at=datetime.utcnow())
        return self.repository.update(schedule)

    def delete(self, space_id: int, schedule_id: int) -> None:
        existing = self.repository.get_by_id(schedule_id)
        if not existing or existing.space_id != space_id:
            raise ValueError('Schedule slot not found')
        self.repository.delete(schedule_id)