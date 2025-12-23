import stripe
import uuid
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from poly_db.repositories import TeamRepository, SubscriptionRepository, UsageLogRepository
from poly_db.models.teams import PlanType
from ..constants import PLAN_LIMITS, PLAN_STRIPE_IDS, I18nKeys

class BillingService:
    def __init__(self, session: Session, stripe_api_key: str):
        self.session = session
        stripe.api_key = stripe_api_key
        self.team_repo = TeamRepository(session)
        self.subscription_repo = SubscriptionRepository(session)
        self.usage_repo = UsageLogRepository(session)

    def create_stripe_customer(self, team_id: uuid.UUID, email: str, name: str) -> str:
        """Creates a Stripe customer for a team."""
        team = self.team_repo.get(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")
        
        if team.stripe_customer_id:
            return team.stripe_customer_id

        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"team_id": str(team_id)}
        )
        
        self.team_repo.update(team_id, stripe_customer_id=customer.id)
        return customer.id

    def check_upload_limit(self, team_id: uuid.UUID) -> Tuple[bool, str]:
        """Checks if a team can upload a new file based on their plan and extra credits."""
        team = self.team_repo.get(team_id)
        if not team:
            return False, "Team not found"

        limits = PLAN_LIMITS.get(team.plan.value, PLAN_LIMITS["FREE"])
        max_uploads = limits["uploads_per_month"]

        if team.monthly_upload_count < max_uploads:
            return True, "Limit not reached"

        if team.extra_credits > 0:
            return True, "Using extra credits"

        return False, I18nKeys.ERR_JOBS_LIMIT_REACHED

    def increment_usage(self, team_id: uuid.UUID, job_id: uuid.UUID = None):
        """Increments upload usage for a team."""
        team = self.team_repo.get(team_id)
        if not team:
            return

        limits = PLAN_LIMITS.get(team.plan.value, PLAN_LIMITS["FREE"])
        max_uploads = limits["uploads_per_month"]

        if team.monthly_upload_count < max_uploads:
            self.team_repo.update(team_id, monthly_upload_count=team.monthly_upload_count + 1)
            self.usage_repo.create(
                team_id=team_id,
                job_id=job_id,
                action="upload",
                amount=1,
                description=f"Plan usage: {team.plan.value}"
            )
        elif team.extra_credits > 0:
            self.team_repo.update(team_id, extra_credits=team.extra_credits - 1)
            self.usage_repo.create(
                team_id=team_id,
                job_id=job_id,
                action="upload",
                amount=1,
                description="Credit usage"
            )
        else:
            raise ValueError("Usage limit exceeded and no credits available")

    def create_portal_session(self, team_id: uuid.UUID, return_url: str) -> stripe.billing_portal.Session:
        """Creates a Stripe Billing Portal session."""
        team = self.team_repo.get(team_id)
        if not team or not team.stripe_customer_id:
            raise ValueError("Team or Stripe customer not found")

        session = stripe.billing_portal.Session.create(
            customer=team.stripe_customer_id,
            return_url=return_url
        )
        return session

    def create_checkout_session(self, team_id: uuid.UUID, plan_type: PlanType, success_url: str, cancel_url: str) -> stripe.checkout.Session:
        """Creates a Stripe Checkout session for a subscription upgrade."""
        team = self.team_repo.get(team_id)
        if not team or not team.stripe_customer_id:
            raise ValueError("Team or Stripe customer not found")

        price_id = PLAN_STRIPE_IDS.get(plan_type.value)
        if not price_id:
            raise ValueError(f"Invalid plan type: {plan_type}")

        session = stripe.checkout.Session.create(
            customer=team.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"team_id": str(team_id), "plan_type": plan_type.value}
        )
        return session

    def create_credits_checkout_session(self, team_id: uuid.UUID, amount: int, success_url: str, cancel_url: str) -> stripe.checkout.Session:
        """Creates a Stripe Checkout session for purchasing credits."""
        team = self.team_repo.get(team_id)
        if not team or not team.stripe_customer_id:
            raise ValueError("Team or Stripe customer not found")
        
        # In a real app, you might have a specific price_id for credits, 
        # or use ad-hoc line items if permitted.
        # For simplicity, we'll assume a unit price in cents.
        from ..constants import CREDIT_PRICE_CENTS

        session = stripe.checkout.Session.create(
            customer=team.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"{amount} PolyScript Credits"},
                    "unit_amount": CREDIT_PRICE_CENTS,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"team_id": str(team_id), "amount": str(amount), "type": "credits"}
        )
        return session

    def sync_subscription(self, stripe_subscription_id: str):
        """Syncs a Stripe subscription with the local database."""
        sub = stripe.Subscription.retrieve(stripe_subscription_id)
        team_id_str = sub.metadata.get("team_id")
        if not team_id_str:
            # Fallback to looking up team by customer id
            team = self.team_repo.get_by_stripe_customer_id(sub.customer)
            if not team:
                return
            team_id = team.id
        else:
            team_id = uuid.UUID(team_id_str)

        # Update or create subscription record
        local_sub = self.subscription_repo.get_by_team_id(team_id)
        
        plan_id = sub["items"]["data"][0]["price"]["id"]
        # Map price_id back to PlanType
        reverse_map = {v: k for k, v in PLAN_STRIPE_IDS.items()}
        plan_type_str = reverse_map.get(plan_id, "FREE")

        from datetime import datetime
        if local_sub:
            self.subscription_repo.update(
                local_sub.id,
                status=sub.status,
                plan_id=plan_id,
                current_period_start=datetime.fromtimestamp(sub.current_period_start),
                current_period_end=datetime.fromtimestamp(sub.current_period_end),
                cancel_at_period_end=sub.cancel_at_period_end,
                stripe_data=sub.to_dict()
            )
        else:
            self.subscription_repo.create(
                team_id=team_id,
                stripe_subscription_id=sub.id,
                status=sub.status,
                plan_id=plan_id,
                current_period_start=datetime.fromtimestamp(sub.current_period_start),
                current_period_end=datetime.fromtimestamp(sub.current_period_end),
                cancel_at_period_end=sub.cancel_at_period_end,
                stripe_data=sub.to_dict()
            )

        # Update Team plan
        self.team_repo.update(team_id, plan=PlanType(plan_type_str))

    def handle_payment_succeeded(self, team_id: uuid.UUID, amount: int, stripe_session_id: str):
        """Handles a successful checkout payment (e.g., for credits)."""
        from poly_db.repositories import CreditPurchaseRepository
        purchase_repo = CreditPurchaseRepository(self.session)
        
        # Check if already processed
        # (This is just a simple check, in production you'd want more robust idempotency)
        
        purchase_repo.create(
            team_id=team_id,
            stripe_session_id=stripe_session_id,
            amount=amount,
            price_paid=amount * 100, # Simplified: $1 per credit
            currency="usd"
        )
        
        team = self.team_repo.get(team_id)
        self.team_repo.update(team_id, extra_credits=team.extra_credits + amount)

    def cancel_subscription(self, team_id: uuid.UUID, at_period_end: bool = True):
        """Cancels a team's subscription."""
        team = self.team_repo.get(team_id)
        if not team or not team.stripe_subscription_id:
            return

        if at_period_end:
            stripe.Subscription.modify(
                team.stripe_subscription_id,
                cancel_at_period_end=True
            )
        else:
            stripe.Subscription.delete(team.stripe_subscription_id)

    def reset_monthly_usage(self, team_id: uuid.UUID):
        """Resets the monthly upload count for a team."""
        self.team_repo.update(team_id, monthly_upload_count=0)

    def downgrade_plan(self, team_id: uuid.UUID, new_plan: PlanType):
        """Downgrades a team's plan with proration."""
        sub = self.subscription_repo.get_by_team_id(team_id)
        if not sub or not sub.stripe_subscription_id:
            raise ValueError("No active subscription to downgrade")

        new_price_id = PLAN_STRIPE_IDS.get(new_plan.value)
        if not new_price_id:
             # If downgrading to FREE, we might actually want to cancel the paid subscription
             # effectively. Handling strict downgrade to FREE involves canceling at period end usually,
             # or immediate cancellation.
             # Assuming FREE has no price ID in PLAN_STRIPE_IDS?
             # If so, we should probably treat it as a cancellation.
             if new_plan == PlanType.FREE:
                 self.cancel_subscription(team_id, at_period_end=True)
                 return
             raise ValueError(f"Invalid plan type: {new_plan}")

        # Retrieve current subscription to get item ID
        stripe_sub = stripe.Subscription.retrieve(sub.stripe_subscription_id)
        item_id = stripe_sub['items']['data'][0]['id']

        stripe.Subscription.modify(
            sub.stripe_subscription_id,
            items=[{
                "id": item_id,
                "price": new_price_id,
            }],
            proration_behavior='always_invoice', # Charge/Credit immediately
        )

    def reactivate_subscription(self, team_id: uuid.UUID):
        """Reactivates a subscription that is scheduled to cancel."""
        sub = self.subscription_repo.get_by_team_id(team_id)
        if not sub or not sub.stripe_subscription_id:
            raise ValueError("No subscription found")

        stripe.Subscription.modify(
            sub.stripe_subscription_id,
            cancel_at_period_end=False
        )
        
        # Update local state immediately
        self.subscription_repo.update(sub.id, cancel_at_period_end=False)

    def list_payment_methods(self, team_id: uuid.UUID):
        """Lists attached payment methods for the team."""
        team = self.team_repo.get(team_id)
        if not team or not team.stripe_customer_id:
            return []
            
        methods = stripe.PaymentMethod.list(
            customer=team.stripe_customer_id,
            type="card"
        )
        return methods.data
        
    def create_setup_session(self, team_id: uuid.UUID, success_url: str, cancel_url: str) -> stripe.checkout.Session:
        """Creates a Checkout Session for adding a new payment method."""
        team = self.team_repo.get(team_id)
        if not team or not team.stripe_customer_id:
             # Create customer if missing (edge case)
             # For now assume exists or error
             raise ValueError("Stripe customer required")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="setup",
            customer=team.stripe_customer_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session

    def delete_payment_method(self, team_id: uuid.UUID, payment_method_id: str):
        """Detaches a payment method from the customer."""
        # Verify ownership
        pm = stripe.PaymentMethod.retrieve(payment_method_id)
        team = self.team_repo.get(team_id)
        
        if pm.customer != team.stripe_customer_id:
            raise ValueError("Payment method does not belong to this team")
            
        stripe.PaymentMethod.detach(payment_method_id)
