from domain.models.iroom_repository import IRoomRepository
from domain.models.room import Room
from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.models.room_model import RoomModel
from infrastructure.databases.factory_database import FactoryDatabase as db_factory


class RoomRepository(IRoomRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, room: Room) -> RoomModel:
        try:
            room = RoomModel(
                name=room.name,
                description=room.description,
                room_type=room.room_type,
                capacity=room.capacity,
                price_per_hour=room.price_per_hour,
                status=room.status,
                created_at=room.created_at,
                updated_at=room.updated_at
            )
            self.session.add(room)
            self.session.commit()
            self.session.refresh(room)
            return room
        except Exception:
            self.session.rollback()
            raise ValueError('Could not create room')
        finally:
            self.session.close()

    def get_by_id(self, room_id: int) -> Optional[RoomModel]:
        return self.session.query(RoomModel).filter_by(id=room_id).first()

    def list(self) -> List[RoomModel]:
        return self.session.query(RoomModel).all()

    def update(self, room: Room) -> RoomModel:
        try:
            room = RoomModel(
                id=room.id,
                name=room.name,
                description=room.description,
                room_type=room.room_type,
                capacity=room.capacity,
                price_per_hour=room.price_per_hour,
                status=room.status,
                created_at=room.created_at,
                updated_at=room.updated_at
            )
            self.session.merge(room)
            self.session.commit()
            return room
        except Exception:
            self.session.rollback()
            raise ValueError('Room not found')
        finally:
            self.session.close()

    def delete(self, room_id: int) -> None:
        try:
            room = self.session.query(RoomModel).filter_by(id=room_id).first()
            if room:
                self.session.delete(room)
                self.session.commit()
            else:
                raise ValueError('Room not found')
        except Exception:
            self.session.rollback()
            raise ValueError('Room not found')
        finally:
            self.session.close()