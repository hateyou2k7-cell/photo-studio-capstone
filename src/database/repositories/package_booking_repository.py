from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func as sa_func
from business.models.ipackage_booking_repository import IPackageBookingRepository
from business.models.package_booking import PackageBookingDomain
from database.models.package_booking_model import PackageBooking as BookingModel
from database.models.equipment_model import Equipment as EquipmentModel, package_equipments
from database.databases.factory_database import FactoryDatabase as db_factory


class PackageBookingRepository(IPackageBookingRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, booking: PackageBookingDomain) -> BookingModel:
        try:
            model = BookingModel(
                package_id=booking.package_id,
                space_id=booking.space_id,
                customer_id=booking.customer_id,
                start_time=booking.start_time,
                end_time=booking.end_time,
                status=booking.status,
                total_price=booking.total_price,
                notes=booking.notes,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not create package booking')

    def get_by_id(self, booking_id: int) -> Optional[BookingModel]:
        return self.session.query(BookingModel).filter_by(id=booking_id).first()

    def list(self, filters: dict = None) -> List[BookingModel]:
        query = self.session.query(BookingModel)
        if filters:
            pkg_id = filters.get('package_id')
            if pkg_id is not None:
                query = query.filter(BookingModel.package_id == pkg_id)
            customer_id = filters.get('customer_id')
            if customer_id is not None:
                query = query.filter(BookingModel.customer_id == customer_id)
            status = filters.get('status')
            if status:
                query = query.filter(BookingModel.status == status)
        return query.order_by(BookingModel.created_at.desc()).all()

    def update(self, booking: PackageBookingDomain) -> BookingModel:
        try:
            existing = self.session.query(BookingModel).filter_by(id=booking.id).first()
            if not existing:
                raise ValueError('Booking not found')
            if booking.status is not None:
                existing.status = booking.status
            if booking.notes is not None:
                existing.notes = booking.notes
            if booking.total_price is not None:
                existing.total_price = booking.total_price
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update booking')

    def find_conflicts(self, space_id: int, start_time, end_time, exclude_id=None) -> list:
        query = self.session.query(BookingModel).filter(
            BookingModel.space_id == space_id,
            BookingModel.status.in_(['pending', 'confirmed']),
            BookingModel.start_time < end_time,
            BookingModel.end_time > start_time,
        )
        if exclude_id:
            query = query.filter(BookingModel.id != exclude_id)
        return query.all()

    def find_equipment_conflicts(self, equipment_ids: list, start_time, end_time, exclude_id=None) -> list:
        if not equipment_ids:
            return []

        conflicting_booking_ids = set()
        for eq_id in equipment_ids:
            pkg_ids = [row[0] for row in self.session.execute(
                package_equipments.select().where(package_equipments.c.equipment_id == eq_id)
            ).fetchall()]
            if pkg_ids:
                bookings = self.session.query(BookingModel).filter(
                    BookingModel.package_id.in_(pkg_ids),
                    BookingModel.status.in_(['pending', 'confirmed']),
                    BookingModel.start_time < end_time,
                    BookingModel.end_time > start_time,
                )
                if exclude_id:
                    bookings = bookings.filter(BookingModel.id != exclude_id)
                for b in bookings.all():
                    conflicting_booking_ids.add(b.id)

        if not conflicting_booking_ids:
            return []
        return self.session.query(BookingModel).filter(BookingModel.id.in_(conflicting_booking_ids)).all()
