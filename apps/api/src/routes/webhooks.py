from fastapi import APIRouter, Request, Header, HTTPException, Depends
import stripe
from sqlalchemy.orm import Session
from poly_db.database import get_db_session
from poly_core.services.billing import BillingService
from ..config import get_settings
import uuid

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    session: Session = Depends(get_db_session)
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

    elif event["type"] in ["customer.subscription.created", "customer.subscription.updated"]:
        subscription = event["data"]["object"]
        billing_service.sync_subscription(subscription["id"])

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        billing_service.sync_subscription(subscription["id"])

    elif event["type"] == "invoice.paid":
        invoice = event["data"]["object"]
        # Update local invoice record
        from poly_db.repositories import InvoiceRepository
        from datetime import datetime
        inv_repo = InvoiceRepository(session)
        # Find or create invoice
        # In a real app, you'd want to sync all invoices
        pass

    session.commit()
    return {"status": "success"}
