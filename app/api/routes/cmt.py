import traceback
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.api.deps import get_current_user
from app.db import models
from app.db.database import get_db
from app.schemas import schemas
from app.schemas.schemas import CampaignOut
from app.services import crud


router = APIRouter()

@router.get("/campaigns/filter", response_model=List[CampaignOut])
def filter_campaigns(
    search: Optional[str] = Query(None),
    is_running: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    return crud.filter_user_campaigns(
        db=db,
        user_id=current_user.id,
        search=search,
        is_running=is_running
    )

@router.post("/campaigns", response_model=schemas.CampaignOut)
def create_campaign(
        campaign: schemas.CampaignCreate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
):
    try:
        return crud.create_campaign(db, user_id=user.id, campaign_data=campaign)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create campaign")

@router.patch("/campaigns/{campaign_id}/status", response_model=schemas.CampaignOut)
def change_campaign_status(
        campaign_id: int,
        payload: schemas.CampaignStatusUpdate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
):
    campaign = crud.toggle_campaign_status(db, campaign_id, user.id, payload.is_active)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")
    return campaign

@router.get("/campaigns", response_model=List[schemas.CampaignOut])
def get_my_campaigns(
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
):
    try:
        return crud.get_user_campaigns(db, user.id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve campaigns")

@router.delete("/campaigns", response_model=schemas.CampaignOut)
def delete_campaign(
        campaign_id: int = Query(..., description="ID of the campaign"),
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
):
    campaign = crud.delete_campaign(db, campaign_id, user.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")
    return campaign

@router.get("/campaign", response_model=List[schemas.CampaignOut])
def get_campaign_by_id(
        campaign_id: int = Query(..., description="ID of the campaign"),
        db: Session = Depends(get_db),
        user=Depends(get_current_user),
):
    try:
        return crud.get_campaign_by_id(db, user.id, campaign_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve campaign"
        )


@router.get("/placements", response_model=List[schemas.PlacementOut])
def get_placements(
        db: Session = Depends(get_db),
):
    try:
        list = crud.get_placements(db)
        print(list)
        return list
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve placements")


@router.put("/payouts/{payout_id}", response_model=schemas.PayoutOut)
def update_payout_amounts(
        payout_id: int,
        total_imp: int,
        to_pay_in_eur: int,
        db: Session = Depends(get_db),
):
    payout = crud.update_payout(db, payout_id, total_imp, to_pay_in_eur)
    if payout is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payout not found")
    return payout
