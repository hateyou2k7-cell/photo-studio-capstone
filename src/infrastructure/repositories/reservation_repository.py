from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from domain.models.ireservation_repository import IReservationRepository
from domain.models.reservation import Reservation, ReservationItem, Payment, ServiceSession, Review
from infrastructure.models.film_reservation_model import (
    Reservation as ReservationModel,
    ReservationItem as ReservationItemModel,
    Payment as PaymentModel,
    ServiceSession as ServiceSessionModel,
    Review as ReviewModel,
)
from infrastructure.databases.factory_database import FactoryDatabase as db_factory


class ReservationRepository(IReservationRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, reservation: Reservation) -> ReservationModel:
        try:
            model = ReservationModel(
                user_id=reservation.user_id,
                provider_id=reservation.provider_id,
                space_id=reservation.space_id,
                package_id=reservation.package_id,
                start_time=reservation.start_time,
                end_time=reservation.end_time,
                total_price=reservation.total_price,
                status=reservation.status,
                qr_code=reservation.qr_code,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not create reservation')

    def get_by_id(self, reservation_id: int) -> Optional[ReservationModel]:
        return self.session.query(ReservationModel).filter_by(id=reservation_id).first()

    def list(self, user_id=None, provider_id=None, status=None) -> List[ReservationModel]:
        query = self.session.query(ReservationModel)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        if provider_id is not None:
            query = query.filter_by(provider_id=provider_id)
        if status is not None:
            query = query.filter(ReservationModel.status == status)
        return query.order_by(ReservationModel.created_at.desc()).all()

    def update(self, reservation: Reservation) -> ReservationModel:
        try:
            existing = self.session.query(ReservationModel).filter_by(id=reservation.id).first()
            if not existing:
                raise ValueError('Reservation not found')
            existing.user_id = reservation.user_id
            existing.provider_id = reservation.provider_id
            existing.space_id = reservation.space_id
            existing.package_id = reservation.package_id
            existing.start_time = reservation.start_time
            existing.end_time = reservation.end_time
            existing.total_price = reservation.total_price
            existing.status = reservation.status
            existing.qr_code = reservation.qr_code
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update reservation')

    def delete(self, reservation_id: int) -> None:
        try:
            model = self.session.query(ReservationModel).filter_by(id=reservation_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Reservation not found')
        except ValueError:
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Reservation not found')

    def update_status(self, reservation_id: int, status: str) -> ReservationModel:
        try:
            existing = self.session.query(ReservationModel).filter_by(id=reservation_id).first()
            if not existing:
                raise ValueError('Reservation not found')
            existing.status = status
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update reservation status')

    def add_item(self, item: ReservationItem) -> ReservationItemModel:
        try:
            model = ReservationItemModel(
                reservation_id=item.reservation_id,
                item_type=item.item_type,
                item_id=item.item_id,
                quantity=item.quantity,
                price_at_booking=item.price_at_booking,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not add reservation item')

    def list_items(self, reservation_id: int) -> List[ReservationItemModel]:
        return self.session.query(ReservationItemModel).filter_by(reservation_id=reservation_id).all()

    def add_payment(self, payment: Payment) -> PaymentModel:
        try:
            model = PaymentModel(
                reservation_id=payment.reservation_id,
                user_id=payment.user_id,
                amount=payment.amount,
                method=payment.method,
                status=payment.status,
                transaction_ref=payment.transaction_ref,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not add payment')

    def get_payment(self, reservation_id: int) -> Optional[PaymentModel]:
        return self.session.query(PaymentModel).filter_by(reservation_id=reservation_id).first()

    def update_payment_status(self, payment_id: int, status: str) -> PaymentModel:
        try:
            existing = self.session.query(PaymentModel).filter_by(id=payment_id).first()
            if not existing:
                raise ValueError('Payment not found')
            existing.status = status
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update payment status')

    def create_session(self, session_obj: ServiceSession) -> ServiceSessionModel:
        try:
            model = ServiceSessionModel(
                reservation_id=session_obj.reservation_id,
                checked_in_at=session_obj.checked_in_at,
                checked_out_at=session_obj.checked_out_at,
                actual_duration_minutes=session_obj.actual_duration_minutes,
                status=session_obj.status,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not create service session')

    def check_in(self, reservation_id: int) -> ServiceSessionModel:
        try:
            reservation = self.session.query(ReservationModel).filter_by(id=reservation_id).first()
            if not reservation:
                raise ValueError('Reservation not found')
            existing_session = self.session.query(ServiceSessionModel).filter_by(reservation_id=reservation_id).first()
            if existing_session:
                existing_session.checked_in_at = datetime.now(timezone.utc)
                existing_session.status = 'in_progress'
                self.session.commit()
                self.session.refresh(existing_session)
                return existing_session
            model = ServiceSessionModel(
                reservation_id=reservation_id,
                checked_in_at=datetime.now(timezone.utc),
                status='in_progress',
            )
            self.session.add(model)
            reservation.status = 'checked_in'
            self.session.commit()
            self.session.refresh(model)
            return model
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not check in')

    def check_out(self, reservation_id: int) -> ServiceSessionModel:
        try:
            reservation = self.session.query(ReservationModel).filter_by(id=reservation_id).first()
            if not reservation:
                raise ValueError('Reservation not found')
            session = self.session.query(ServiceSessionModel).filter_by(reservation_id=reservation_id).first()
            if not session:
                raise ValueError('No active session for this reservation')
            session.checked_out_at = datetime.now(timezone.utc)
            session.status = 'completed'
            if session.checked_in_at:
                duration = (session.checked_out_at - session.checked_in_at).total_seconds() / 60
                session.actual_duration_minutes = int(duration)
            reservation.status = 'checked_out'
            self.session.commit()
            self.session.refresh(session)
            return session
        except ValueError:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Could not check out: {e}')

    def add_review(self, review: Review) -> ReviewModel:
        try:
            model = ReviewModel(
                reservation_id=review.reservation_id,
                user_id=review.user_id,
                space_id=review.space_id,
                rating=review.rating,
                comment=review.comment,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not add review')

    def list_reviews(self, space_id: int) -> List[ReviewModel]:
        return self.session.query(ReviewModel).filter_by(space_id=space_id).order_by(ReviewModel.created_at.desc()).all()

    def check_overlap(self, space_id: int, start_time, end_time, exclude_id=None) -> bool:
        query = self.session.query(ReservationModel).filter(
            ReservationModel.space_id == space_id,
            ReservationModel.status != 'cancelled',
            ReservationModel.start_time < end_time,
            ReservationModel.end_time > start_time,
        )
        if exclude_id is not None:
            query = query.filter(ReservationModel.id != exclude_id)
        return query.first() is not None
