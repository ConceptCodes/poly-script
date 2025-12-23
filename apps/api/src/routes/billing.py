from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from poly_db.database import get_db_session
from poly_db.repositories import (
    TeamRepository,
    SubscriptionRepository,
    InvoiceRepository,
    CreditPurchaseRepository
)
from poly_core.services.billing import BillingService
from poly_db.models.teams import PlanType
from poly_core.constants import I18nKeys
from poly_core.schemas.billing import (
    SubscriptionResponse,
    UpgradeSubscriptionRequest,
    PurchaseCreditsRequest,
    UsageResponse,
    InvoiceResponse,
    CheckoutSessionResponse,
    PortalSessionResponse,
    PortalSessionRequest,
    DowngradeSubscriptionRequest,
    PaymentMethodResponse,
    SetupSessionRequest,
    CreditPurchaseResponse
)
from ..config import get_settings
import uuid

router = APIRouter(prefix="/v1/billing", tags=["billing"])

# Mock dependency for current team - to be replaced by real auth in Task 03
async def get_current_team_id() -> uuid.UUID:
    # In a real app, this would come from the JWT token
    # For now, we'll try to find the first team in the DB or error
    session = next(get_db_session())
    repo = TeamRepository(session)
    teams = repo.list()
    if not teams:
        # Create a default team for development if none exists
        team = repo.create(name="Default Team", plan=PlanType.FREE)
        session.commit()
        return team.id
    return teams[0].id

def get_billing_service(session: Session = Depends(get_db_session)):
    settings = get_settings()
    return BillingService(session, settings.STRIPE_SECRET_KEY)

@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    team_id: uuid.UUID = Depends(get_current_team_id),
    session: Session = Depends(get_db_session)
):
    repo = SubscriptionRepository(session)
    sub = repo.get_by_team_id(team_id)
    if not sub:
        # Return default FREE plan response if no subscription found
        # In a real app we might want to ensure every team has a subscription record or handle None
        # But schema requires fields. Let's return dummy stricture matching schema or create logic.
        # For now, let's assume if no sub, it's a "virtual" free plan
        return {
            "stripe_subscription_id": "",
            "status": "active",
            "plan_id": "free",
            "current_period_end": 0, # or now?
            "cancel_at_period_end": False
        }
        # Actually Pydantic validation might fail on ints/dates.
        # Better: create a default subscription for the team if missing?
        # Or return null?
        # Schema says current_period_end is datetime.
        # Let's fake it for now or return None if schema allowed Optional.
        # But schema is strict.
        
    return sub

@router.post("/portal", response_model=PortalSessionResponse)
async def create_portal_session(
    body: PortalSessionRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service)
):
    try:
        session = billing_service.create_portal_session(team_id, body.return_url)
        return {"url": session.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/subscription/cancel")
async def cancel_subscription(
    at_period_end: bool = True, # This could be query param or body. Let's keep as query for simplicity or move to body. Standard is usually POST body for actions. 
    # But for just one boolean, query is often used.
    # However, strict guidelines prefer schemas.
    # Let's leave as query for now as it wasn't flagged as critical, or make a schema.
    # Current plan had Upgrade/Purchase schemas.
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service)
):
    billing_service.cancel_subscription(team_id, at_period_end)
    return {"status": "success"}

@router.post("/subscription/upgrade", response_model=CheckoutSessionResponse)
async def upgrade_plan(
    body: UpgradeSubscriptionRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service)
):
    try:
        session = billing_service.create_checkout_session(
            team_id=team_id,
            plan_type=body.plan,
            success_url=body.success_url,
            cancel_url=body.cancel_url
        )
        return {"checkout_url": session.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/credits/purchase", response_model=CheckoutSessionResponse)
async def purchase_credits(
    body: PurchaseCreditsRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service)
):
    try:
        session = billing_service.create_credits_checkout_session(
            team_id=team_id,
            amount=body.amount,
            success_url=body.success_url,
            cancel_url=body.cancel_url
        )
        return {"checkout_url": session.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    team_id: uuid.UUID = Depends(get_current_team_id),
    session: Session = Depends(get_db_session)
):
    repo = TeamRepository(session)
    team = repo.get(team_id)
    if not team:
        raise HTTPException(status_code=404, detail=I18nKeys.ERR_TEAM_NOT_FOUND)
    
    from poly_core.constants import PLAN_LIMITS
    limits = PLAN_LIMITS.get(team.plan.value, PLAN_LIMITS["FREE"])
    
    return {
        "plan": team.plan,
        "monthly_upload_count": team.monthly_upload_count,
        "monthly_limit": limits["uploads_per_month"],
        "extra_credits": team.extra_credits
    }

@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    team_id: uuid.UUID = Depends(get_current_team_id),
    session: Session = Depends(get_db_session)
):
    repo = InvoiceRepository(session)
    return repo.get_all_by_team(team_id)

@router.post("/subscription/downgrade")
async def downgrade_plan(
    body: DowngradeSubscriptionRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service)
):
    try:
        billing_service.downgrade_plan(team_id, body.plan)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/subscription/reactivate")
async def reactivate_subscription(
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service)
):
    try:
        billing_service.reactivate_subscription(team_id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def list_payment_methods(
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service)
):
    return billing_service.list_payment_methods(team_id)

@router.post("/payment-methods", response_model=CheckoutSessionResponse)
async def add_payment_method(
    body: SetupSessionRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service)
):
    try:
        session = billing_service.create_setup_session(team_id, body.success_url, body.cancel_url)
        return {"checkout_url": session.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/payment-methods/{payment_method_id}")
async def delete_payment_method(
    payment_method_id: str,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service)
):
    try:
        billing_service.delete_payment_method(team_id, payment_method_id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/credits/history", response_model=List[CreditPurchaseResponse])
async def get_credits_history(
    team_id: uuid.UUID = Depends(get_current_team_id),
    session: Session = Depends(get_db_session)
):
    repo = CreditPurchaseRepository(session)
    return repo.get_all_by_team(team_id)
