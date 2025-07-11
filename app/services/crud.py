from typing import Optional, List, Type

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.db import models
from app.db.models import Campaign
from app.schemas import schemas


def create_campaign(db: Session, user_id: int, campaign_data: schemas.CampaignCreate):
    campaign = models.Campaign(
        title=campaign_data.title,
        url=campaign_data.url,
        user_id=user_id
    )

    placements = db.query(models.Placement).filter(
        models.Placement.id.in_(campaign_data.placement_ids)
    ).all()

    campaign.placements = placements
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    for placement in placements:
        payout = models.Payout(
            user_id=user_id,
            campaign_id=campaign.id,
            placement_id=placement.id,
            total_imp=0,
            to_pay_in_eur=0
        )
        db.add(payout)
    db.commit()

    return campaign

def toggle_campaign_status(db: Session, campaign_id: int, user_id: int, is_active: bool):
    campaign = db.query(models.Campaign).filter_by(id=campaign_id, user_id=user_id, is_archived = False).first()
    if not campaign:
        return None
    campaign.is_active = is_active
    db.commit()
    return campaign

def get_user_campaigns(db: Session, user_id: int):
    return db.query(models.Campaign).options(
        joinedload(models.Campaign.placements),
        joinedload(models.Campaign.payouts)
    ).filter(models.Campaign.user_id == user_id,
             models.Campaign.is_archived == False
             ).all()

def get_campaign_by_id(db: Session, user_id: int, campaign_id: int):
    return db.query(models.Campaign).options(
        joinedload(models.Campaign.placements),
        joinedload(models.Campaign.payouts)
    ).filter(
        models.Campaign.id == campaign_id,
        models.Campaign.is_archived == False
    ).all()

def update_payout(
    db: Session,
    payout_id: int,
    total_imp: int,
    to_pay_in_eur: int
):
    payout = db.query(models.Payout).filter_by(id=payout_id).first()
    if not payout:
        return None
    payout.total_imp = total_imp
    payout.to_pay_in_eur = to_pay_in_eur
    db.commit()
    db.refresh(payout)
    return payout

def create_provider(db: Session, name: str):
    provider = models.Provider(
        name=name
    )

    db.add(provider)
    db.commit()
    db.refresh(provider)

    return provider

def create_placement(db: Session, placement_data: schemas.PlacementCreate):
    provider = db.query(models.Provider).filter_by(id=placement_data.provider_id).first()

    if not provider:
        return None

    placement = models.Placement(
        country=placement_data.country,
        imp_price_in_eur=placement_data.imp_price_in_eur,
        provider=provider
    )

    db.add(placement)
    db.commit()
    db.refresh(placement)

    return placement

def get_placements(db):
    return db.query(models.Placement).options(
        joinedload(models.Placement.provider),
    ).all()

def delete_campaign(db, campaign_id, user_id):
    campaign = db.query(models.Campaign).filter_by(id=campaign_id, user_id=user_id).first()
    if not campaign:
        return None
    campaign.is_archived = True
    db.commit()
    return campaign

def filter_user_campaigns(
    db: Session,
    user_id: int,
    search: Optional[str] = None,
    is_running: Optional[bool] = None,
) -> list[Type[Campaign]]:
    query = db.query(models.Campaign).options(
        joinedload(models.Campaign.placements),
        joinedload(models.Campaign.payouts)
    ).filter(
        models.Campaign.user_id == user_id,
        models.Campaign.is_archived == False
    )

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Campaign.title.ilike(search_term),
                models.Campaign.url.ilike(search_term)
            )
        )

    if is_running is not None:
        query = query.filter(models.Campaign.is_active == is_running)

    return query.order_by(models.Campaign.created_at.desc()).all()
