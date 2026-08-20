from typing import List, Optional
from domain.models.space import Space
from domain.models.ispace_repository import ISpaceRepository

SPACE_TYPES = {'darkroom', 'studio'}


class SpaceService:
    def __init__(self, repository: ISpaceRepository):
        self.repository = repository

    def create(self, provider_id: int, name: str, space_type: str, description=None,
               address=None, max_capacity=None, base_price_per_hour=0, status=True,
               **optional) -> Space:
        if space_type not in SPACE_TYPES:
            raise ValueError("space_type must be 'darkroom' or 'studio'")
        space = Space(id=None, provider_id=provider_id, name=name, space_type=space_type,
                      description=description, address=address, max_capacity=max_capacity,
                      base_price_per_hour=base_price_per_hour, status=status)
        return self.repository.add(space)

    def get(self, space_id: int) -> Optional[Space]:
        return self.repository.get_by_id(space_id)

    def list(self) -> List[Space]:
        return self.repository.list()

    def update(self, space_id: int, provider_id: int, name: str, space_type: str,
               description=None, address=None, max_capacity=None,
               base_price_per_hour=0, status=True, **optional) -> Space:
        if space_type not in SPACE_TYPES:
            raise ValueError("space_type must be 'darkroom' or 'studio'")
        existing = self.repository.get_by_id(space_id)
        if not existing:
            raise ValueError('Space not found')
        space = Space(id=space_id, provider_id=provider_id, name=name, space_type=space_type,
                      description=description, address=address, max_capacity=max_capacity,
                      base_price_per_hour=base_price_per_hour, status=status)
        return self.repository.update(space)

    def delete(self, space_id: int) -> None:
        self.repository.delete(space_id)