import traceback
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db import models
from app.db.database import get_db
from app.schemas import schemas
from app.schemas.schemas import CampaignOut
from app.services import crud
from app.services.validator import validate_string_field

router = APIRouter()

@router.get("/campaigns/filter", response_model=List[CampaignOut])
def filter_campaigns(
    search: Optional[str] = Query(None),
    is_running: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        return crud.filter_user_campaigns(
            db=db,
            user_id=current_user.id,
            search=search,
            is_running=is_running
        )
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/campaigns", response_model=schemas.CampaignOut)
def create_campaign(
    campaign: schemas.CampaignCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    validate_string_field("campaign title", campaign.title)
    validate_string_field("campaign url", campaign.url)

    try:
        campaign = crud.create_campaign(db, user_id=user.id, campaign_data=campaign)
        if not campaign:
            raise HTTPException(status_code=400, detail="Incorrect provider ids")
        return campaign
    except DataError:
        raise HTTPException(
            status_code=400,
            detail="Invalid data: one or more fields exceed length limits"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/campaigns/{campaign_id}/status", response_model=schemas.CampaignOut)
def change_campaign_status(
    campaign_id: int,
    payload: schemas.CampaignStatusUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        campaign = crud.toggle_campaign_status(db, campaign_id, user.id, payload.is_active)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")
        return campaign
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns", response_model=List[schemas.CampaignOut])
def get_my_campaigns(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return crud.get_user_campaigns(db, user.id)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/campaigns", response_model=schemas.CampaignOut)
def delete_campaign(
    campaign_id: int = Query(..., description="ID of the campaign"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        campaign = crud.delete_campaign(db, campaign_id, user.id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")
        return campaign
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaign", response_model=List[schemas.CampaignOut])
def get_campaign_by_id(
    campaign_id: int = Query(..., description="ID of the campaign"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        campaign = crud.get_campaign_by_id(db, user.id, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Could not retrieve campaign")

@router.get("/placements", response_model=List[schemas.PlacementOut])
def get_placements(
    db: Session = Depends(get_db),
):
    try:
        return crud.get_placements(db)
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Could not retrieve placements")

@router.put("/payouts/{payout_id}", response_model=schemas.PayoutOut)
def update_payout_amounts(
    payout_id: int,
    total_imp: int,
    to_pay_in_eur: int,
    db: Session = Depends(get_db),
):
    try:
        payout = crud.update_payout(db, payout_id, total_imp, to_pay_in_eur)
        if payout is None:
            raise HTTPException(status_code=404, detail="Payout not found")
        return payout
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to update payout")

@router.post("/providers", response_model=schemas.ProviderOut)
def create_provider(provider: schemas.ProviderCreate, db: Session = Depends(get_db)):
    validate_string_field('provider name', provider.name)

    try:
        return crud.create_provider(name=provider.name, db=db)
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to create provider")

@router.post("/placements", response_model=schemas.PlacementOut)
def create_placement(placement: schemas.PlacementCreate, db: Session = Depends(get_db)):
    validate_string_field('placement country', placement.country)

    try:
        placement = crud.create_placement(db=db, placement_data=placement)
        if not placement:
            raise HTTPException(status_code=404, detail="Provider not found")
        return placement
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to create placement")