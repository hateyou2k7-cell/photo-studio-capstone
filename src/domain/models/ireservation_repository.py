from abc import ABC, abstractmethod
from typing import List, Optional
from .reservation import Reservation, ReservationItem, Payment, ServiceSession, Review


class IReservationRepository(ABC):
    @abstractmethod
    def add(self, reservation: Reservation) -> Reservation:
        pass

    @abstractmethod
    def get_by_id(self, reservation_id: int) -> Optional[Reservation]:
        pass

    @abstractmethod
    def list(self, user_id=None, provider_id=None, status=None) -> List[Reservation]:
        pass

    @abstractmethod
    def update(self, reservation: Reservation) -> Reservation:
        pass

    @abstractmethod
    def delete(self, reservation_id: int) -> None:
        pass

    @abstractmethod
    def update_status(self, reservation_id: int, status: str) -> Reservation:
        pass

    @abstractmethod
    def add_item(self, item: ReservationItem) -> ReservationItem:
        pass

    @abstractmethod
    def list_items(self, reservation_id: int) -> List[ReservationItem]:
        pass

    @abstractmethod
    def add_payment(self, payment: Payment) -> Payment:
        pass

    @abstractmethod
    def get_payment(self, reservation_id: int) -> Optional[Payment]:
        pass

    @abstractmethod
    def update_payment_status(self, payment_id: int, status: str) -> Payment:
        pass

    @abstractmethod
    def create_session(self, session: ServiceSession) -> ServiceSession:
        pass

    @abstractmethod
    def check_in(self, reservation_id: int) -> ServiceSession:
        pass

    @abstractmethod
    def check_out(self, reservation_id: int) -> ServiceSession:
        pass

    @abstractmethod
    def add_review(self, review: Review) -> Review:
        pass

    @abstractmethod
    def list_reviews(self, space_id: int) -> List[Review]:
        pass

    @abstractmethod
    def check_overlap(self, space_id: int, start_time, end_time, exclude_id=None) -> bool:
        pass
