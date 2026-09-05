from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ProviderProfile:
    id: Optional[int]
    user_id: int
    business_name: str
    description: Optional[str] = None
    address: Optional[str] = None
    status: str = 'pending'
    created_at: Optional[datetime] = None
