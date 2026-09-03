import enum
from sqlalchemy import func, Column, BigInteger, String, Text, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.databases.base import Base


class PostCategory(enum.Enum):
    article = 'article'
    tutorial = 'tutorial'
    equipment_review = 'equipment_review'
    technique = 'technique'


class WorkshopStatus(enum.Enum):
    open = 'open'
    full = 'full'
    cancelled = 'cancelled'
    done = 'done'


class Post(Base):
    __tablename__ = 'posts'

    id = Column(BigInteger, primary_key=True)
    author_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default='article')
    is_published = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    author = relationship('User')
    comments = relationship('Comment', back_populates='post')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(BigInteger, primary_key=True)
    post_id = Column(BigInteger, ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    post = relationship('Post', back_populates='comments')
    user = relationship('User')


class Workshop(Base):
    __tablename__ = 'workshops'

    id = Column(BigInteger, primary_key=True)
    expert_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    scheduled_at = Column(DateTime, nullable=False)
    location = Column(String(255))
    capacity = Column(Integer, nullable=False, default=10)
    price = Column(Integer, default=0)
    status = Column(String(50), default='open')

    expert = relationship('User')
    registrations = relationship('WorkshopRegistration', back_populates='workshop', cascade='all, delete-orphan')


class WorkshopRegistration(Base):
    __tablename__ = 'workshop_registrations'

    id = Column(BigInteger, primary_key=True)
    workshop_id = Column(BigInteger, ForeignKey('workshops.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='registered')
    registered_at = Column(DateTime, server_default=func.now())

    workshop = relationship('Workshop', back_populates='registrations')
    user = relationship('User')
