from sqlalchemy import func, Column, BigInteger, Integer, String, Boolean, DateTime, Time, ForeignKey
from sqlalchemy.orm import relationship
from database.databases.base import Base


class SpaceImage(Base):
    __tablename__ = 'space_images'

    id = Column(BigInteger, primary_key=True)
    space_id = Column(BigInteger, ForeignKey('spaces.id', ondelete='CASCADE'), nullable=False)
    url = Column(String(500), nullable=False)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    space = relationship('Space', back_populates='images')


class SpaceSchedule(Base):
    __tablename__ = 'space_schedules'

    id = Column(BigInteger, primary_key=True)
    space_id = Column(BigInteger, ForeignKey('spaces.id', ondelete='CASCADE'), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    space = relationship('Space', back_populates='schedule')