from abc import ABC, abstractmethod
from typing import List, Optional
from .space_image import SpaceImage

class ISpaceImageRepository(ABC):
    @abstractmethod
    def add(self, image: SpaceImage) -> SpaceImage:
        pass

    @abstractmethod
    def get_by_id(self, image_id: int) -> Optional[SpaceImage]:
        pass

    @abstractmethod
    def list(self, space_id: int) -> List[SpaceImage]:
        pass

    @abstractmethod
    def update(self, image: SpaceImage) -> SpaceImage:
        pass

    @abstractmethod
    def delete(self, image_id: int) -> None:
        pass

    @abstractmethod
    def clear_primary(self, space_id: int) -> None:
        pass