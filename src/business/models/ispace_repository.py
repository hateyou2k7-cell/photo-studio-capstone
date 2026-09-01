from abc import ABC, abstractmethod
from typing import List, Optional
from .space import Space

class ISpaceRepository(ABC):
    @abstractmethod
    def add(self, space: Space) -> Space:
        pass

    @abstractmethod
    def get_by_id(self, space_id: int) -> Optional[Space]:
        pass

    @abstractmethod
    def list(self) -> List[Space]:
        pass

    @abstractmethod
    def search(self, filters: dict) -> List[Space]:
        pass

    @abstractmethod
    def update(self, space: Space) -> Space:
        pass

    @abstractmethod
    def delete(self, space_id: int) -> None:
        pass