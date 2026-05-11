import uuid
from datetime import UTC

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from poly_core.services.billing import BillingService
from poly_db.database import get_db_session
from poly_db.repositories import InvoiceRepository, SubscriptionRepository, TeamRepository

from ..config import get_settings

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    session: Session = Depends(get_db_session),
):
    settings = get_settings()
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    billing_service = BillingService(session, settings.STRIPE_SECRET_KEY)
    team_repo = TeamRepository(session)
    invoice_repo = InvoiceRepository(session)
    sub_repo = SubscriptionRepository(session)

    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        metadata = session_obj.get("metadata", {})
        team_id_str = metadata.get("team_id")

        if team_id_str:
            team_id = uuid.UUID(team_id_str)
            if metadata.get("type") == "credits":
                amount = int(metadata.get("amount", 0))
                billing_service.handle_payment_succeeded(team_id, amount, session_obj["id"])
            elif metadata.get("plan_type"):
                # For subscriptions, checkout session completed is just the start
                # The subscription will be created and handled by other events
                pass

    elif (
        event["type"] in ["customer.subscription.created", "customer.subscription.updated"]
        or event["type"] == "customer.subscription.deleted"
    ):
        subscription = event["data"]["object"]
        if event["type"] == "customer.subscription.deleted":
            # Explicitly set team plan to FREE when subscription is deleted
            customer_id = subscription.get("customer")
            team = team_repo.get_by_stripe_customer_id(customer_id)
            if team:
                from poly_db.models.teams import PlanType

                team_repo.update(team.id, plan=PlanType.FREE)
                # Also delete local subscription record
                local_sub = sub_repo.get_by_team_id(team.id)
                if local_sub:
                    sub_repo.delete(local_sub.id)
        else:
            billing_service.sync_subscription(subscription["id"])

    elif event["type"] == "invoice.paid":
        invoice = event["data"]["object"]
        team = team_repo.get_by_stripe_customer_id(invoice.get("customer"))
        if team:
            from datetime import datetime

            invoice_id = invoice.get("id")
            existing = invoice_repo.get_by_stripe_invoice_id(invoice_id)
            payload = {
                "team_id": team.id,
                "stripe_invoice_id": invoice_id,
                "amount_due": invoice.get("amount_due", 0),
                "amount_paid": invoice.get("amount_paid", 0),
                "currency": invoice.get("currency", "usd"),
                "status": invoice.get("status", "paid"),
                "invoice_pdf": invoice.get("invoice_pdf"),
                "hosted_invoice_url": invoice.get("hosted_invoice_url"),
                "period_start": datetime.fromtimestamp(invoice.get("period_start", 0), tz=UTC),
                "period_end": datetime.fromtimestamp(invoice.get("period_end", 0), tz=UTC),
            }
            if existing:
                invoice_repo.update(existing.id, **payload)
            else:
                invoice_repo.create(**payload)

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        team = team_repo.get_by_stripe_customer_id(invoice.get("customer"))
        if team:
            invoice_id = invoice.get("id")
            existing = invoice_repo.get_by_stripe_invoice_id(invoice_id)
            if existing:
                invoice_repo.update(existing.id, status=invoice.get("status", "past_due"))
            # Mark subscription past_due if present
            sub = sub_repo.get_by_team_id(team.id)
            if sub:
                sub_repo.update(sub.id, status="past_due")

    session.commit()
    return {"status": "success"}


webhooks_router = router
