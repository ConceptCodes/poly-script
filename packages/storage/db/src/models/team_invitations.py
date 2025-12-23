from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from .team_members import TeamRole
from datetime import datetime
import uuid

class TeamInvitation(Base, TimestampMixin):
    __tablename__ = "team_invitations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))
    email: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[TeamRole] = mapped_column(SQLEnum(TeamRole), default=TeamRole.MEMBER)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    team: Mapped["Team"] = relationship(back_populates="invitations")

    def __repr__(self):
        return f"<TeamInvitation(team_id={self.team_id}, email={self.email})>"
