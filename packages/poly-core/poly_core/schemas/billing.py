from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional, List, Union, Dict, Any
from poly_db.models.teams import PlanType
import uuid

class SubscriptionResponse(BaseModel):
    stripe_subscription_id: str
    status: str
    plan_id: str
    current_period_end: datetime
    cancel_at_period_end: bool
    model_config = {"from_attributes": True}

class UpgradeSubscriptionRequest(BaseModel):
    plan: PlanType
    success_url: str
    cancel_url: str

class DowngradeSubscriptionRequest(BaseModel):
    plan: PlanType

class PurchaseCreditsRequest(BaseModel):
    amount: int = Field(..., ge=1, le=100)
    success_url: str
    cancel_url: str

class UsageResponse(BaseModel):
    plan: PlanType
    monthly_upload_count: int
    monthly_limit: float | int | str # "inf" or number
    extra_credits: int
    model_config = {"from_attributes": True}

class InvoiceResponse(BaseModel):
    id: uuid.UUID
    stripe_invoice_id: str
    amount_paid: int
    status: str
    created_at: datetime
    hosted_invoice_url: Optional[str]
    model_config = {"from_attributes": True}

class CheckoutSessionResponse(BaseModel):
    checkout_url: str

class PortalSessionResponse(BaseModel):
    url: str

class PortalSessionRequest(BaseModel):
    return_url: str

class SetupSessionRequest(BaseModel):
    success_url: str
    cancel_url: str

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
    model_config = {"from_attributes": True}

class CreditsResponse(BaseModel):
    plan: PlanType
    extra_credits: int
    model_config = {"from_attributes": True}

class UsageLogResponse(BaseModel):
    action: str
    amount: int
    description: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}

class UsageHistoryResponse(BaseModel):
    items: List[UsageLogResponse]

class PricingPlanResponse(BaseModel):
    plan: str
    limits: Dict[str, Union[int, float]]
    price_id: Optional[str] = None

class PricingResponse(BaseModel):
    plans: List[PricingPlanResponse]
    credit_price_cents: int

class InvoicePdfResponse(BaseModel):
    url: Optional[str]
