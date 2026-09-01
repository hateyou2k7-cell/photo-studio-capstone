from sqlalchemy import func, Column, Integer, BigInteger, String, Text, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database.databases.base import Base

import enum


class UserRole(enum.Enum):
    user = 'user'
    photographer = 'photographer'
    provider = 'provider'
    expert = 'expert'
    admin = 'admin'


class ProviderStatus(enum.Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    avatar_url = Column(String(500))
    role = Column(String(50), nullable=False, default='photographer')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    provider_profile = relationship('ProviderProfile', back_populates='user', uselist=False)


class ProviderProfile(Base):
    __tablename__ = 'provider_profiles'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    business_name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(String(255))
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, server_default=func.now())

    user = relationship('User', back_populates='provider_profile')
    spaces = relationship('Space', back_populates='provider')
    resources = relationship('Resource', back_populates='provider')
    consumables = relationship('Consumable', back_populates='provider')
    packages = relationship('ServicePackage', back_populates='provider')
