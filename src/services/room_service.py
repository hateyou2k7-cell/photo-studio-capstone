from typing import List, Optional
from business.models.room import Room
from business.models.iroom_repository import IRoomRepository


class RoomService:
    def __init__(self, repository: IRoomRepository):
        self.repository = repository

    def create_room(self, name: str, description: str, room_type: str, capacity: int,
                    price_per_hour: float, status: str, created_at, updated_at) -> Room:
        room = Room(id=None, name=name, description=description, room_type=room_type,
                    capacity=capacity, price_per_hour=price_per_hour, status=status,
                    created_at=created_at, updated_at=updated_at)
        return self.repository.add(room)

    def get_room(self, room_id: int) -> Optional[Room]:
        return self.repository.get_by_id(room_id)

    def get_by_name(self, name: str, exclude_id: Optional[int] = None) -> Optional[Room]:
        return self.repository.find_by_name(name, exclude_id)

    def list_rooms(self) -> List[Room]:
        return self.repository.list()

    def update_room(self, room_id: int, name: str, description: str, room_type: str,
                    capacity: int, price_per_hour: float, status: str,
                    created_at, updated_at) -> Room:
        room = Room(id=room_id, name=name, description=description, room_type=room_type,
                    capacity=capacity, price_per_hour=price_per_hour, status=status,
                    created_at=created_at, updated_at=updated_at)
        return self.repository.update(room)

    def delete_room(self, room_id: int) -> None:
        self.repository.delete(room_id)