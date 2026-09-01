import enum
from sqlalchemy import func, Column, BigInteger, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from database.databases.base import Base


class BookingStatus(enum.Enum):
    pending = 'pending'
    confirmed = 'confirmed'
    cancelled = 'cancelled'
    completed = 'completed'


class PackageBooking(Base):
    __tablename__ = 'package_bookings'

    id = Column(BigInteger, primary_key=True)
    package_id = Column(BigInteger, ForeignKey('service_packages.id'), nullable=False)
    space_id = Column(BigInteger, ForeignKey('spaces.id'), nullable=False)
    customer_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(50))
    total_price = Column(BigInteger, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    package = relationship('ServicePackage', backref='bookings')
    space = relationship('Space', backref='package_bookings')
    customer = relationship('User', backref='package_bookings')

    __table_args__ = (
        Index('ix_pkg_booking_package_time', 'package_id', 'start_time', 'end_time'),
        Index('ix_pkg_booking_space_time', 'space_id', 'start_time', 'end_time'),
        Index('ix_pkg_booking_customer', 'customer_id'),
    )
