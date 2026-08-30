from typing import List, Optional
from datetime import datetime
from domain.models.package_booking import PackageBookingDomain
from domain.models.ipackage_booking_repository import IPackageBookingRepository
from infrastructure.models.equipment_model import Equipment as EquipmentModel, package_equipments
from infrastructure.models.film_package_model import ServicePackage
from infrastructure.databases.factory_database import FactoryDatabase as db_factory


class ResourceAvailabilityService:
    def __init__(self):
        self.session = db_factory.get_database('POSTGREE').session

    def get_package_with_equipment(self, package_id: int):
        pkg = self.session.query(ServicePackage).filter_by(id=package_id).first()
        if not pkg:
            return None, []
        eq_ids = [row[0] for row in self.session.execute(
            package_equipments.select().where(package_equipments.c.package_id == package_id)
        ).fetchall()]
        equipments = self.session.query(EquipmentModel).filter(EquipmentModel.id.in_(eq_ids)).all() if eq_ids else []
        return pkg, equipments

    def check_availability(self, package_id: int, start_time, end_time, exclude_booking_id=None) -> list:
        pkg, equipments = self.get_package_with_equipment(package_id)
        if not pkg:
            return [{'resource_type': 'package', 'resource_id': package_id, 'resource_name': 'Package not found'}]
        conflicts = []
        from infrastructure.models.package_booking_model import PackageBooking
        space_bookings = self.session.query(PackageBooking).filter(
            PackageBooking.space_id == pkg.provider_id,
            PackageBooking.status.in_(['pending', 'confirmed']),
            PackageBooking.start_time < end_time,
            PackageBooking.end_time > start_time,
        )
        if exclude_booking_id:
            space_bookings = space_bookings.filter(PackageBooking.id != exclude_booking_id)
        for b in space_bookings.all():
            conflicts.append({
                'resource_type': 'space',
                'resource_id': pkg.provider_id,
                'resource_name': f'Space booking #{b.id}',
                'conflicting_start': b.start_time,
                'conflicting_end': b.end_time,
            })
        if equipments:
            for eq in equipments:
                pkg_ids = [row[0] for row in self.session.execute(
                    package_equipments.select().where(package_equipments.c.equipment_id == eq.id)
                ).fetchall()]
                if pkg_ids:
                    eq_bookings = self.session.query(PackageBooking).filter(
                        PackageBooking.package_id.in_(pkg_ids),
                        PackageBooking.status.in_(['pending', 'confirmed']),
                        PackageBooking.start_time < end_time,
                        PackageBooking.end_time > start_time,
                    )
                    if exclude_booking_id:
                        eq_bookings = eq_bookings.filter(PackageBooking.id != exclude_booking_id)
                    for b in eq_bookings.all():
                        conflicts.append({
                            'resource_type': 'equipment',
                            'resource_id': eq.id,
                            'resource_name': eq.name,
                            'conflicting_start': b.start_time,
                            'conflicting_end': b.end_time,
                        })
        seen = set()
        unique = []
        for c in conflicts:
            key = (c['resource_type'], c['resource_id'], str(c['conflicting_start']), str(c['conflicting_end']))
            if key not in seen:
                seen.add(key)
                unique.append(c)
        return unique

    def lock_resources(self, package_id: int):
        import hashlib
        pkg, equipments = self.get_package_with_equipment(package_id)
        if not pkg:
            return
        lock_keys = []
        if pkg.provider_id:
            lock_keys.append(f"space:{pkg.provider_id}")
        for eq in equipments:
            lock_keys.append(f"equipment:{eq.id}")
        lock_keys.sort()
        from sqlalchemy import text
        for key in lock_keys:
            h = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
            self.session.execute(text("SELECT pg_advisory_xact_lock(:key)"), {'key': h})


class PackageBookingService:
    def __init__(self, repository: IPackageBookingRepository):
        self.repository = repository
        self.availability_service = ResourceAvailabilityService()

    def create(self, package_id: int, customer_id: int, start_time, end_time, notes=None) -> PackageBookingDomain:
        if start_time >= end_time:
            raise ValueError('start_time must be before end_time')
        if start_time < datetime.utcnow():
            raise ValueError('start_time cannot be in the past')
        pkg, equipments = self.availability_service.get_package_with_equipment(package_id)
        if not pkg:
            raise ValueError('Package not found')
        if not getattr(pkg, 'status', True):
            raise ValueError('Package is not active')
        conflicts = self.availability_service.check_availability(package_id, start_time, end_time)
        if conflicts:
            raise ValueError(f'Resource conflict: {conflicts}')
        duration_hours = (end_time - start_time).total_seconds() / 3600
        total_price = int(float(pkg.price) * duration_hours) if pkg.price else 0
        booking = PackageBookingDomain(
            package_id=package_id, space_id=pkg.provider_id, customer_id=customer_id,
            start_time=start_time, end_time=end_time, total_price=total_price, notes=notes,
        )
        return self.repository.add(booking)

    def get(self, booking_id: int) -> Optional[PackageBookingDomain]:
        return self.repository.get_by_id(booking_id)

    def list(self, filters: dict = None) -> List[PackageBookingDomain]:
        return self.repository.list(filters)

    def cancel(self, booking_id: int) -> PackageBookingDomain:
        existing = self.repository.get_by_id(booking_id)
        if not existing:
            raise ValueError('Booking not found')
        booking = PackageBookingDomain(id=booking_id, status='cancelled')
        return self.repository.update(booking)
