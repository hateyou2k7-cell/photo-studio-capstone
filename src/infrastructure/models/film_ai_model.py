from sqlalchemy import func, Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base


class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    started_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    user = relationship('User')
    messages = relationship('Message', back_populates='conversation')


class Message(Base):
    __tablename__ = 'messages'

    id = Column(BigInteger, primary_key=True)
    conversation_id = Column(BigInteger, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False)
    sender_type = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    conversation = relationship('Conversation', back_populates='messages')
