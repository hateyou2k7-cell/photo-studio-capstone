from typing import List, Optional
from business.models.provider_profile import ProviderProfile
from business.models.iprovider_profile_repository import IProviderProfileRepository


class ProviderService:
    def __init__(self, repository: IProviderProfileRepository):
        self.repository = repository

    def create(self, user_id: int, business_name: str, description=None,
               address=None) -> ProviderProfile:
        existing = self.repository.get_by_user_id(user_id)
        if existing:
            raise ValueError('User already has a provider profile')
        profile = ProviderProfile(
            id=None,
            user_id=user_id,
            business_name=business_name,
            description=description,
            address=address,
            status='pending'
        )
        return self.repository.add(profile)

    def get(self, profile_id: int) -> Optional[ProviderProfile]:
        return self.repository.get_by_id(profile_id)

    def get_by_user_id(self, user_id: int) -> Optional[ProviderProfile]:
        return self.repository.get_by_user_id(user_id)

    def list(self) -> List[ProviderProfile]:
        return self.repository.list()

    def approve(self, profile_id: int) -> ProviderProfile:
        profile = self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError('Provider profile not found')
        profile.status = 'approved'
        return self.repository.update(profile)

    def reject(self, profile_id: int) -> ProviderProfile:
        profile = self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError('Provider profile not found')
        profile.status = 'rejected'
        return self.repository.update(profile)

    def delete(self, profile_id: int) -> None:
        self.repository.delete(profile_id)
