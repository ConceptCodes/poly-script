from typing import List, Optional
from sqlalchemy import String, Integer, BigInteger, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
import enum
import uuid

class PlanType(str, enum.Enum):
    FREE = "FREE"
    STANDARD = "STANDARD"
    PRO = "PRO"

class Team(Base, TimestampMixin):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    host_language: Mapped[str] = mapped_column(String(10), default="en")
    
    # Subscription info
    plan: Mapped[PlanType] = mapped_column(SQLEnum(PlanType), default=PlanType.FREE)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Limits
    monthly_upload_count: Mapped[int] = mapped_column(Integer, default=0)
    extra_credits: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    members: Mapped[List["TeamMember"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    invitations: Mapped[List["TeamInvitation"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    jobs: Mapped[List["TranscriptionJob"]] = relationship(back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, plan={self.plan})>"
