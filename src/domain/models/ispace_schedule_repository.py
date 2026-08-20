from abc import ABC, abstractmethod
from typing import List, Optional
from .space_schedule import SpaceSchedule

class ISpaceScheduleRepository(ABC):
    @abstractmethod
    def add(self, schedule: SpaceSchedule) -> SpaceSchedule:
        pass

    @abstractmethod
    def get_by_id(self, schedule_id: int) -> Optional[SpaceSchedule]:
        pass

    @abstractmethod
    def list(self, space_id: int) -> List[SpaceSchedule]:
        pass

    @abstractmethod
    def update(self, schedule: SpaceSchedule) -> SpaceSchedule:
        pass

    @abstractmethod
    def delete(self, schedule_id: int) -> None:
        pass