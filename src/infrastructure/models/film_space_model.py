import enum
from sqlalchemy import func, Column, BigInteger, String, Text, Boolean, DateTime, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from infrastructure.databases.base import Base


class SpaceType(enum.Enum):
    darkroom = 'darkroom'
    studio = 'studio'


class ResourceCategory(enum.Enum):
    camera = 'camera'
    lens = 'lens'
    enlarger = 'enlarger'
    scanner = 'scanner'
    lighting = 'lighting'
    tripod = 'tripod'
    background = 'background'
    darkroom_equipment = 'darkroom_equipment'


class Space(Base):
    __tablename__ = 'spaces'

    id = Column(BigInteger, primary_key=True)
    provider_id = Column(BigInteger, ForeignKey('provider_profiles.id'), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(ENUM(SpaceType), nullable=False)
    description = Column(Text)
    address = Column(String(255))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    max_capacity = Column(Integer)
    dimensions = Column(String(100))
    art_style = Column(String(100))
    lighting = Column(String(100))
    ventilation = Column(String(100))
    acoustics = Column(String(100))
    amenities = Column(Text)
    operating_hours = Column(String(100))
    base_price_per_hour = Column(Numeric(12, 2), nullable=False, default=0)
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    provider = relationship('ProviderProfile', back_populates='spaces')
    resources = relationship('SpaceResource', back_populates='space')


class Resource(Base):
    __tablename__ = 'resources'

    id = Column(BigInteger, primary_key=True)
    provider_id = Column(BigInteger, ForeignKey('provider_profiles.id'), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(ENUM(ResourceCategory), nullable=False)
    description = Column(Text)
    condition = Column(String(20), default='good')
    rental_price_per_hour = Column(Numeric(12, 2), nullable=False, default=0)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    provider = relationship('ProviderProfile', back_populates='resources')
    spaces = relationship('SpaceResource', back_populates='resource')


class SpaceResource(Base):
    __tablename__ = 'space_resources'

    id = Column(BigInteger, primary_key=True)
    space_id = Column(BigInteger, ForeignKey('spaces.id', ondelete='CASCADE'), nullable=False)
    resource_id = Column(BigInteger, ForeignKey('resources.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, default=1)

    space = relationship('Space', back_populates='resources')
    resource = relationship('Resource', back_populates='spaces')


class Consumable(Base):
    __tablename__ = 'consumables'

    id = Column(BigInteger, primary_key=True)
    provider_id = Column(BigInteger, ForeignKey('provider_profiles.id'), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(50), default='chemical')
    unit = Column(String(20))
    quantity_in_stock = Column(Integer, default=0)
    unit_price = Column(Numeric(12, 2), nullable=False, default=0)
    is_available = Column(Boolean, default=True)

    provider = relationship('ProviderProfile', back_populates='consumables')
