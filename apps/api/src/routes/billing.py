import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from poly_core.constants import I18nKeys
from poly_core.schemas.billing import (
    CancelSubscriptionRequest,
    CheckoutSessionResponse,
    CreditPurchaseResponse,
    CreditsResponse,
    DowngradeSubscriptionRequest,
    InvoicePdfResponse,
    InvoiceResponse,
    PaymentMethodResponse,
    PortalSessionRequest,
    PortalSessionResponse,
    PricingResponse,
    PurchaseCreditsRequest,
    SetupIntentResponse,
    SetupSessionRequest,
    SubscriptionResponse,
    UpgradeSubscriptionRequest,
    UsageHistoryResponse,
    UsageResponse,
)
from poly_core.services.billing import BillingService
from poly_db.database import get_db_session
from src.dependencies import get_current_team_id

from ..config import get_settings

router = APIRouter(prefix="/v1/billing", tags=["billing"])


def get_billing_service(session: Session = Depends(get_db_session)):
    settings = get_settings()
    return BillingService(session, settings.STRIPE_SECRET_KEY)


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    return billing_service.get_subscription_or_default(team_id)


@router.post("/portal", response_model=PortalSessionResponse)
async def create_portal_session(
    body: PortalSessionRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    try:
        session = billing_service.create_portal_session(team_id, body.return_url)
        return {"url": session.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscription/cancel")
async def cancel_subscription(
    body: CancelSubscriptionRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    billing_service.cancel_subscription(team_id, body.at_period_end)
    return {"status": "success"}


@router.post("/subscription/upgrade", response_model=CheckoutSessionResponse)
async def upgrade_plan(
    body: UpgradeSubscriptionRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    try:
        session = billing_service.create_checkout_session(
            team_id=team_id,
            plan_type=body.plan,
            success_url=body.success_url,
            cancel_url=body.cancel_url,
        )
        return {"checkout_url": session.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/credits/purchase", response_model=CheckoutSessionResponse)
async def purchase_credits(
    body: PurchaseCreditsRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    try:
        session = billing_service.purchase_credits(
            team_id=team_id,
            amount=body.amount,
            success_url=body.success_url,
            cancel_url=body.cancel_url,
        )
        return {"checkout_url": session.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    try:
        return billing_service.get_usage(team_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=I18nKeys.ERR_TEAM_NOT_FOUND)


@router.get("/usage/history", response_model=UsageHistoryResponse)
async def get_usage_history(
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    items = billing_service.get_usage_history(team_id)
    return {"items": items}


@router.get("/invoices", response_model=list[InvoiceResponse])
async def list_invoices(
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    return billing_service.list_invoices(team_id)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: uuid.UUID,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    invoice = billing_service.get_invoice_for_team(team_id, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.get("/invoices/{invoice_id}/pdf", response_model=InvoicePdfResponse)
async def get_invoice_pdf(
    invoice_id: uuid.UUID,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    url = billing_service.get_invoice_pdf_for_team(team_id, invoice_id)
    if not url:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"url": url}


@router.post("/subscription/downgrade")
async def downgrade_plan(
    body: DowngradeSubscriptionRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    try:
        billing_service.downgrade_plan(team_id, body.plan)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscription/reactivate")
async def reactivate_subscription(
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    try:
        billing_service.reactivate_subscription(team_id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payment-methods", response_model=list[PaymentMethodResponse])
async def list_payment_methods(
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    return billing_service.list_payment_methods(team_id)


@router.patch("/payment-methods/{payment_method_id}/default")
async def set_default_payment_method(
    payment_method_id: str,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    try:
        billing_service.set_default_payment_method(team_id, payment_method_id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payment-methods", response_model=CheckoutSessionResponse)
async def add_payment_method(
    body: SetupSessionRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    try:
        session = billing_service.create_setup_session(team_id, body.success_url, body.cancel_url)
        return {"checkout_url": session.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payment-methods/setup-intent", response_model=SetupIntentResponse)
async def create_payment_method_setup_intent(
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    try:
        intent = billing_service.create_setup_intent(team_id)
        return {"client_secret": intent.client_secret}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/payment-methods/{payment_method_id}")
async def delete_payment_method(
    payment_method_id: str,
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    try:
        billing_service.delete_payment_method(team_id, payment_method_id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/credits/history", response_model=list[CreditPurchaseResponse])
async def get_credits_history(
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    return billing_service.list_credit_purchases(team_id)


@router.get("/credits", response_model=CreditsResponse)
async def get_credits(
    team_id: uuid.UUID = Depends(get_current_team_id),
    billing_service: BillingService = Depends(get_billing_service),
):
    try:
        return billing_service.get_credits(team_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=I18nKeys.ERR_TEAM_NOT_FOUND)


@router.get("/pricing", response_model=PricingResponse)
async def get_pricing(billing_service: BillingService = Depends(get_billing_service)):
    return billing_service.get_pricing()

billing_router = router
