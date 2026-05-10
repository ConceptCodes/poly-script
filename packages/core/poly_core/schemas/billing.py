import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from poly_db.models.teams import PlanType


class SubscriptionResponse(BaseModel):
    stripe_subscription_id: str
    status: str
    plan_id: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool


class UpgradeSubscriptionRequest(BaseModel):
    plan: PlanType
    success_url: str
    cancel_url: str


class DowngradeSubscriptionRequest(BaseModel):
    plan: PlanType


class CancelSubscriptionRequest(BaseModel):
    at_period_end: bool = True


class PurchaseCreditsRequest(BaseModel):
    amount: int = Field(..., ge=1, le=100)
    success_url: str
    cancel_url: str


class UsageResponse(BaseModel):
    plan: PlanType
    monthly_upload_count: int
    monthly_limit: float | int | str  # "inf" or number
    extra_credits: int


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    stripe_invoice_id: str
    amount_paid: int
    status: str
    created_at: datetime
    hosted_invoice_url: str | None


class CheckoutSessionResponse(BaseModel):
    checkout_url: str


class PortalSessionResponse(BaseModel):
    url: str


class PortalSessionRequest(BaseModel):
    return_url: str


class SetupSessionRequest(BaseModel):
    success_url: str
    cancel_url: str


class SetupIntentResponse(BaseModel):
    client_secret: str


class PaymentMethodResponse(BaseModel):
    id: str
    brand: str
    last4: str
    exp_month: int
    exp_year: int


class CreditPurchaseResponse(BaseModel):
    created_at: datetime
    amount: int
    price_paid: int
    currency: str


class CreditsResponse(BaseModel):
    plan: PlanType
    extra_credits: int


class UsageLogResponse(BaseModel):
    action: str
    amount: int
    description: str | None
    created_at: datetime


class UsageHistoryResponse(BaseModel):
    items: list[UsageLogResponse]


class PricingPlanResponse(BaseModel):
    plan: str
    limits: dict[str, int | float]
    price_id: str | None = None


class PricingResponse(BaseModel):
    plans: list[PricingPlanResponse]
    credit_price_cents: int


class InvoicePdfResponse(BaseModel):
    url: str | None
