import uuid
from enum import Enum

from pydantic import BaseModel, Field


class TeamRoleSchema(str, Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class PlanTypeSchema(str, Enum):
    FREE = "FREE"
    STANDARD = "STANDARD"
    PRO = "PRO"


class CreateTeamRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    host_language: str = "en"


class UpdateTeamRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    host_language: str | None = None


class TeamResponse(BaseModel):
    id: uuid.UUID
    name: str
    host_language: str
    plan: PlanTypeSchema
    stripe_customer_id: str | None = None
    monthly_upload_count: int
    extra_credits: int
    created_at: str
    updated_at: str


class TeamMemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    team_id: uuid.UUID
    role: TeamRoleSchema
    created_at: str
    user_email: str | None = None
    user_full_name: str | None = None


class UpdateMemberRoleRequest(BaseModel):
    role: TeamRoleSchema


class CreateInvitationRequest(BaseModel):
    email: str
    role: TeamRoleSchema


class InvitationResponse(BaseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    email: str
    role: TeamRoleSchema
    expires_at: str
    accepted_at: str | None = None
    created_at: str


class AcceptInvitationRequest(BaseModel):
    token: str
