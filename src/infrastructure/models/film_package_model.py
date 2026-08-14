import enum
from sqlalchemy import func, Column, BigInteger, String, Text, Boolean, DateTime, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from infrastructure.databases.base import Base


class ItemType(enum.Enum):
    space = 'space'
    resource = 'resource'
    consumable = 'consumable'


class ServicePackage(Base):
    __tablename__ = 'service_packages'

    id = Column(BigInteger, primary_key=True)
    provider_id = Column(BigInteger, ForeignKey('provider_profiles.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(12, 2), nullable=False, default=0)
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    provider = relationship('ProviderProfile', back_populates='packages')
    items = relationship('PackageItem', back_populates='package')


class PackageItem(Base):
    __tablename__ = 'package_items'

    id = Column(BigInteger, primary_key=True)
    package_id = Column(BigInteger, ForeignKey('service_packages.id', ondelete='CASCADE'), nullable=False)
    item_type = Column(ENUM(ItemType), nullable=False)
    item_id = Column(BigInteger, nullable=False)
    quantity = Column(Integer, default=1)

    package = relationship('ServicePackage', back_populates='items')
