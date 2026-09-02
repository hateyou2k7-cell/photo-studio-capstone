from abc import ABC, abstractmethod
from typing import List, Optional
from business.models.provider_profile import ProviderProfile


class IProviderProfileRepository(ABC):
    @abstractmethod
    def add(self, profile: ProviderProfile) -> ProviderProfile:
        pass

    @abstractmethod
    def get_by_id(self, profile_id: int) -> Optional[ProviderProfile]:
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[ProviderProfile]:
        pass

    @abstractmethod
    def list(self) -> List[ProviderProfile]:
        pass

    @abstractmethod
    def update(self, profile: ProviderProfile) -> ProviderProfile:
        pass

    @abstractmethod
    def delete(self, profile_id: int) -> None:
        pass
