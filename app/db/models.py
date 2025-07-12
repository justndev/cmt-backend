from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


campaign_placement_association = Table(
    'campaign_placements',
    Base.metadata,
    Column('campaign_id', Integer, ForeignKey('campaigns.id'), primary_key=True),
    Column('placement_id', Integer, ForeignKey('placements.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.now)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    campaigns = relationship("Campaign", back_populates="user")
    payouts = relationship("Payout", back_populates="user")

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    is_archived = Column(Boolean, default=False)
    url = Column(String(1024), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="campaigns")

    placements = relationship(
        "Placement",
        secondary=campaign_placement_association,
        back_populates="campaigns"
    )

    payouts = relationship("Payout", back_populates="campaign")

class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    placements = relationship("Placement", back_populates="provider")

class Placement(Base):
    __tablename__ = "placements"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(255), nullable=False, index=True)
    imp_price_in_eur = Column(Integer, nullable=False)  # Price in EUR cents
    created_at = Column(DateTime, default=datetime.now)

    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    provider = relationship("Provider", back_populates="placements")

    campaigns = relationship(
        "Campaign",
        secondary=campaign_placement_association,
        back_populates="placements"
    )

    payouts = relationship("Payout", back_populates="placement")

class Payout(Base):
    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)
    total_imp = Column(Integer, nullable=False)
    to_pay_in_eur = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    placement_id = Column(Integer, ForeignKey("placements.id"), nullable=False)

    user = relationship("User", back_populates="payouts")
    campaign = relationship("Campaign", back_populates="payouts")
    placement = relationship("Placement", back_populates="payouts")