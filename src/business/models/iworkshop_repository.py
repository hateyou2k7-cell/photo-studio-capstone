from abc import ABC, abstractmethod
from typing import List, Optional
from .workshop import Workshop, WorkshopRegistration


class IWorkshopRepository(ABC):
    @abstractmethod
    def add(self, workshop: Workshop) -> Workshop:
        pass

    @abstractmethod
    def get_by_id(self, workshop_id: int) -> Optional[Workshop]:
        pass

    @abstractmethod
    def list(self, expert_id=None, status=None) -> List[Workshop]:
        pass

    @abstractmethod
    def update(self, workshop: Workshop) -> Workshop:
        pass

    @abstractmethod
    def delete(self, workshop_id: int) -> None:
        pass

    @abstractmethod
    def register(self, registration: WorkshopRegistration) -> WorkshopRegistration:
        pass

    @abstractmethod
    def list_registrations(self, workshop_id: int) -> List[WorkshopRegistration]:
        pass

    @abstractmethod
    def cancel_registration(self, registration_id: int) -> WorkshopRegistration:
        pass

    @abstractmethod
    def count_registrations(self, workshop_id: int) -> int:
        pass
