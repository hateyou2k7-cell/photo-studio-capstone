from abc import ABC, abstractmethod
from typing import List, Optional
from .room import Room

class IRoomRepository(ABC):
    @abstractmethod
    def add(self, room: Room) -> Room:
        pass

    @abstractmethod
    def get_by_id(self, room_id: int) -> Optional[Room]:
        pass

    @abstractmethod
    def find_by_name(self, name: str, exclude_id: Optional[int] = None) -> Optional[Room]:
        pass

    @abstractmethod
    def list(self) -> List[Room]:
        pass

    @abstractmethod
    def update(self, room: Room) -> Room:
        pass

    @abstractmethod
    def delete(self, room_id: int) -> None:
        pass