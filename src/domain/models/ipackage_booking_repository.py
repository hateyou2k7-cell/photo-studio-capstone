from abc import ABC, abstractmethod
from typing import List, Optional
from .package_booking import PackageBookingDomain


class IPackageBookingRepository(ABC):
    @abstractmethod
    def add(self, booking: PackageBookingDomain) -> PackageBookingDomain:
        pass

    @abstractmethod
    def get_by_id(self, booking_id: int) -> Optional[PackageBookingDomain]:
        pass

    @abstractmethod
    def list(self, filters: dict = None) -> List[PackageBookingDomain]:
        pass

    @abstractmethod
    def update(self, booking: PackageBookingDomain) -> PackageBookingDomain:
        pass

    @abstractmethod
    def find_conflicts(self, space_id: int, start_time, end_time, exclude_id=None) -> list:
        pass

    @abstractmethod
    def find_equipment_conflicts(self, equipment_ids: list, start_time, end_time, exclude_id=None) -> list:
        pass
