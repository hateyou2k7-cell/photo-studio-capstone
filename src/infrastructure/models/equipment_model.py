import enum
from sqlalchemy import func, Column, BigInteger, String, Text, Boolean, DateTime, Numeric, ForeignKey, Index, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from infrastructure.databases.base import Base


class EquipmentType(enum.Enum):
    enlarger = 'enlarger'
    camera = 'camera'
    scanner = 'scanner'
    lighting = 'lighting'
    tripod = 'tripod'
    tank = 'tank'
    other = 'other'


class EquipmentCondition(enum.Enum):
    excellent = 'excellent'
    good = 'good'
    fair = 'fair'
    poor = 'poor'
    broken = 'broken'


package_equipments = Table(
    'package_equipments', Base.metadata,
    Column('package_id', BigInteger, ForeignKey('service_packages.id', ondelete='CASCADE'), primary_key=True),
    Column('equipment_id', BigInteger, ForeignKey('equipments.id', ondelete='CASCADE'), primary_key=True),
)


class Equipment(Base):
    __tablename__ = 'equipments'

    id = Column(BigInteger, primary_key=True)
    provider_id = Column(BigInteger, ForeignKey('provider_profiles.id'), nullable=False)
    space_id = Column(BigInteger, ForeignKey('spaces.id'), nullable=True)
    name = Column(String(255), nullable=False)
    model_name = Column(String(255))
    type = Column(ENUM(EquipmentType), nullable=False)
    compatibility = Column(String(255))
    condition = Column(ENUM(EquipmentCondition), default=EquipmentCondition.good)
    description = Column(Text)
    price_per_hour = Column(Numeric(12, 2), default=0)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    space = relationship('Space', backref='equipments')
    packages = relationship('ServicePackage', secondary=package_equipments, back_populates='equipments')

    __table_args__ = (
        Index('ix_equipment_space_id', 'space_id'),
        Index('ix_equipment_provider_id', 'provider_id'),
    )
