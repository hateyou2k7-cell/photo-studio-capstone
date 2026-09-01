from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text
from database.databases.base import Base

class RoomModel(Base):
    __tablename__ = 'rooms'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    room_type = Column(String(50), nullable=False, default='standard')
    capacity = Column(Integer, nullable=False, default=1)
    price_per_hour = Column(Numeric(12, 2), nullable=False, default=0)
    status = Column(String(50), nullable=False, default='available')
    created_at = Column(DateTime)
    updated_at = Column(DateTime)