import enum
from sqlalchemy import func, Column, BigInteger, String, DateTime, Numeric, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from infrastructure.databases.base import Base
from infrastructure.models.film_package_model import ItemType


class ReservationStatus(enum.Enum):
    pending = 'pending'
    approved = 'approved'
    confirmed = 'confirmed'
    checked_in = 'checked_in'
    checked_out = 'checked_out'
    completed = 'completed'
    cancelled = 'cancelled'


class PaymentMethod(enum.Enum):
    vnpay = 'vnpay'
    momo = 'momo'
    cash = 'cash'


class PaymentStatus(enum.Enum):
    pending = 'pending'
    success = 'success'
    failed = 'failed'
    refunded = 'refunded'


class SessionStatus(enum.Enum):
    in_progress = 'in_progress'
    completed = 'completed'


class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    provider_id = Column(BigInteger, ForeignKey('provider_profiles.id'), nullable=False)
    space_id = Column(BigInteger, ForeignKey('spaces.id'))
    package_id = Column(BigInteger, ForeignKey('service_packages.id'))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False, default=0)
    status = Column(ENUM(ReservationStatus), default=ReservationStatus.pending)
    qr_code = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    user = relationship('User')
    items = relationship('ReservationItem', back_populates='reservation')
    payments = relationship('Payment', back_populates='reservation')
    session = relationship('ServiceSession', back_populates='reservation', uselist=False)


class ReservationItem(Base):
    __tablename__ = 'reservation_items'

    id = Column(BigInteger, primary_key=True)
    reservation_id = Column(BigInteger, ForeignKey('reservations.id', ondelete='CASCADE'), nullable=False)
    item_type = Column(ENUM(ItemType), nullable=False)
    item_id = Column(BigInteger, nullable=False)
    quantity = Column(Integer, default=1)
    price_at_booking = Column(Numeric(12, 2), nullable=False, default=0)

    reservation = relationship('Reservation', back_populates='items')


class Payment(Base):
    __tablename__ = 'payments'

    id = Column(BigInteger, primary_key=True)
    reservation_id = Column(BigInteger, ForeignKey('reservations.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    method = Column(ENUM(PaymentMethod), nullable=False)
    status = Column(ENUM(PaymentStatus), default=PaymentStatus.pending)
    transaction_ref = Column(String(255))
    created_at = Column(DateTime, default=func.now())

    reservation = relationship('Reservation', back_populates='payments')


class ServiceSession(Base):
    __tablename__ = 'service_sessions'

    id = Column(BigInteger, primary_key=True)
    reservation_id = Column(BigInteger, ForeignKey('reservations.id'), nullable=False)
    checked_in_at = Column(DateTime)
    checked_out_at = Column(DateTime)
    actual_duration_minutes = Column(Integer)
    status = Column(ENUM(SessionStatus), default=SessionStatus.in_progress)

    reservation = relationship('Reservation', back_populates='session')


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(BigInteger, primary_key=True)
    reservation_id = Column(BigInteger, ForeignKey('reservations.id'))
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    space_id = Column(BigInteger, ForeignKey('spaces.id'))
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=func.now())
