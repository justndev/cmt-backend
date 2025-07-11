from typing import List
from datetime import datetime
from pydantic import BaseModel, constr, conint

from app.schemas.user import UserResponse

class ProviderCreate(BaseModel):
    name: constr(min_length=1, max_length=255)

class ProviderOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        orm_mode = True

class PlacementCreate(BaseModel):
    country: constr(min_length=1, max_length=255)
    imp_price_in_eur: conint(ge=0)
    provider_id: int

class PlacementOut(BaseModel):
    id: int
    country: constr(max_length=255)
    imp_price_in_eur: conint(ge=0)
    created_at: datetime
    provider: ProviderOut


    class Config:
        orm_mode = True

class PayoutOut(BaseModel):
    id: int
    total_imp: conint(ge=0)
    to_pay_in_eur: conint(ge=0)
    created_at: datetime
    placement: PlacementOut

    class Config:
        orm_mode = True

class CampaignCreate(BaseModel):
    title: constr(min_length=1, max_length=255)
    url: str
    placement_ids: List[int]

class CampaignOut(BaseModel):
    id: int
    title: constr(max_length=255)
    url: str
    is_active: bool
    is_archived: bool
    created_at: datetime
    placements: List[PlacementOut]
    payouts: List[PayoutOut]

    user: UserResponse

    class Config:
        orm_mode = True

class CampaignStatusUpdate(BaseModel):
    is_active: bool