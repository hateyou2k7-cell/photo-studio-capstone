from typing import List, Optional
from datetime import datetime
from business.models.reservation import Reservation, ReservationItem, Payment, ServiceSession, Review
from business.models.ireservation_repository import IReservationRepository

RESERVATION_STATUSES = {'pending', 'approved', 'confirmed', 'checked_in', 'checked_out', 'completed', 'cancelled'}
PAYMENT_METHODS = {'vnpay', 'momo', 'cash'}
PAYMENT_STATUSES = {'pending', 'success', 'failed', 'refunded'}


class ReservationService:
    def __init__(self, repository: IReservationRepository):
        self.repository = repository

    def create(self, user_id: int, provider_id: int, start_time, end_time,
               space_id=None, package_id=None, total_price=0, status='pending',
               qr_code=None) -> Reservation:
        if not start_time or not end_time:
            raise ValueError('start_time and end_time are required')
        if start_time >= end_time:
            raise ValueError('start_time must be before end_time')
        if space_id and self.repository.check_overlap(space_id, start_time, end_time):
            raise ValueError('Space is already booked for this time period')
        reservation = Reservation(
            id=None, user_id=user_id, provider_id=provider_id,
            space_id=space_id, package_id=package_id,
            start_time=start_time, end_time=end_time,
            total_price=total_price, status=status, qr_code=qr_code,
        )
        return self.repository.add(reservation)

    def get(self, reservation_id: int) -> Optional[Reservation]:
        return self.repository.get_by_id(reservation_id)

    def list(self, user_id=None, provider_id=None, status=None) -> List[Reservation]:
        if status and status not in RESERVATION_STATUSES:
            raise ValueError(f'status must be one of {RESERVATION_STATUSES}')
        return self.repository.list(user_id=user_id, provider_id=provider_id, status=status)

    def update(self, reservation_id: int, user_id: int, provider_id: int,
               start_time, end_time, space_id=None, package_id=None,
               total_price=0, status='pending', qr_code=None) -> Reservation:
        existing = self.repository.get_by_id(reservation_id)
        if not existing:
            raise ValueError('Reservation not found')
        if start_time and end_time and start_time >= end_time:
            raise ValueError('start_time must be before end_time')
        if space_id and start_time and end_time:
            if self.repository.check_overlap(space_id, start_time, end_time, exclude_id=reservation_id):
                raise ValueError('Space is already booked for this time period')
        reservation = Reservation(
            id=reservation_id, user_id=user_id, provider_id=provider_id,
            space_id=space_id, package_id=package_id,
            start_time=start_time, end_time=end_time,
            total_price=total_price, status=status, qr_code=qr_code,
        )
        return self.repository.update(reservation)

    def delete(self, reservation_id: int) -> None:
        existing = self.repository.get_by_id(reservation_id)
        if not existing:
            raise ValueError('Reservation not found')
        self.repository.delete(reservation_id)

    def approve(self, reservation_id: int) -> Reservation:
        return self._transition(reservation_id, 'approved')

    def confirm(self, reservation_id: int) -> Reservation:
        return self._transition(reservation_id, 'confirmed')

    def cancel(self, reservation_id: int) -> Reservation:
        return self._transition(reservation_id, 'cancelled')

    def complete(self, reservation_id: int) -> Reservation:
        return self._transition(reservation_id, 'completed')

    def _transition(self, reservation_id: int, target_status: str) -> Reservation:
        existing = self.repository.get_by_id(reservation_id)
        if not existing:
            raise ValueError('Reservation not found')
        current = existing.status
        if hasattr(current, 'value'):
            current = current.value
        transitions = {
            'pending': ['approved', 'cancelled'],
            'approved': ['confirmed', 'cancelled'],
            'confirmed': ['checked_in', 'cancelled'],
            'checked_in': ['checked_out'],
            'checked_out': ['completed'],
        }
        allowed = transitions.get(current, [])
        if target_status not in allowed:
            raise ValueError(f'Cannot transition from {current} to {target_status}')
        return self.repository.update_status(reservation_id, target_status)

    def add_item(self, reservation_id: int, item_type: str, item_id: int,
                 quantity=1, price_at_booking=0) -> ReservationItem:
        existing = self.repository.get_by_id(reservation_id)
        if not existing:
            raise ValueError('Reservation not found')
        item = ReservationItem(
            id=None, reservation_id=reservation_id,
            item_type=item_type, item_id=item_id,
            quantity=quantity, price_at_booking=price_at_booking,
        )
        return self.repository.add_item(item)

    def list_items(self, reservation_id: int) -> List[ReservationItem]:
        return self.repository.list_items(reservation_id)

    def create_payment(self, reservation_id: int, user_id: int, amount,
                       method='cash', transaction_ref=None) -> Payment:
        existing = self.repository.get_by_id(reservation_id)
        if not existing:
            raise ValueError('Reservation not found')
        if method not in PAYMENT_METHODS:
            raise ValueError(f'method must be one of {PAYMENT_METHODS}')
        payment = Payment(
            id=None, reservation_id=reservation_id, user_id=user_id,
            amount=amount, method=method, status='pending',
            transaction_ref=transaction_ref,
        )
        return self.repository.add_payment(payment)

    def get_payment(self, reservation_id: int) -> Optional[Payment]:
        return self.repository.get_payment(reservation_id)

    def confirm_payment(self, payment_id: int) -> Payment:
        return self.repository.update_payment_status(payment_id, 'success')

    def fail_payment(self, payment_id: int) -> Payment:
        return self.repository.update_payment_status(payment_id, 'failed')

    def refund_payment(self, payment_id: int) -> Payment:
        return self.repository.update_payment_status(payment_id, 'refunded')

    def check_in(self, reservation_id: int) -> ServiceSession:
        existing = self.repository.get_by_id(reservation_id)
        if not existing:
            raise ValueError('Reservation not found')
        current = existing.status
        if hasattr(current, 'value'):
            current = current.value
        if current not in ('confirmed', 'approved'):
            raise ValueError('Reservation must be confirmed before check-in')
        return self.repository.check_in(reservation_id)

    def check_out(self, reservation_id: int) -> ServiceSession:
        existing = self.repository.get_by_id(reservation_id)
        if not existing:
            raise ValueError('Reservation not found')
        current = existing.status
        if hasattr(current, 'value'):
            current = current.value
        if current != 'checked_in':
            raise ValueError('Reservation must be checked_in before check-out')
        return self.repository.check_out(reservation_id)

    def add_review(self, reservation_id: int, user_id: int, rating: int,
                   space_id=None, comment=None) -> Review:
        existing = self.repository.get_by_id(reservation_id)
        if not existing:
            raise ValueError('Reservation not found')
        if not 1 <= rating <= 5:
            raise ValueError('rating must be between 1 and 5')
        review = Review(
            id=None, reservation_id=reservation_id, user_id=user_id,
            space_id=space_id, rating=rating, comment=comment,
        )
        return self.repository.add_review(review)

    def list_reviews(self, space_id: int) -> List[Review]:
        return self.repository.list_reviews(space_id)
