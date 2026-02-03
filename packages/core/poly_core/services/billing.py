import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import stripe
from sqlalchemy.orm import Session

from poly_core.constants import (
    CREDIT_PRICE_CENTS,
    PLAN_LIMITS,
    PLAN_STRIPE_IDS,
    SUPPORTED_LANGUAGES,
    I18nKeys,
)
from poly_db.models.teams import PlanType
from poly_db.repositories import (
    CreditPurchaseRepository,
    InvoiceRepository,
    SubscriptionRepository,
    TeamRepository,
    UsageLogRepository,
)


class BillingService:
    def __init__(self, session: Session, stripe_api_key: str):
        self.session = session
        stripe.api_key = stripe_api_key
        self.team_repo = TeamRepository(session)
        self.subscription_repo = SubscriptionRepository(session)
        self.usage_repo = UsageLogRepository(session)
        self.credit_repo = CreditPurchaseRepository(session)
        self.invoice_repo = InvoiceRepository(session)

    def create_stripe_customer(self, team_id: uuid.UUID, email: str, name: str) -> str:
        """Creates a Stripe customer for a team."""
        team = self.team_repo.get(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")

        if team.stripe_customer_id:
            return team.stripe_customer_id

        customer = stripe.Customer.create(
            email=email, name=name, metadata={"team_id": str(team_id)}
        )

        self.team_repo.update(team_id, stripe_customer_id=customer.id)
        return customer.id

    def get_subscription(self, team_id: uuid.UUID):
        """Returns the local subscription record if available."""
        return self.subscription_repo.get_by_team_id(team_id)

    def get_subscription_or_default(self, team_id: uuid.UUID) -> dict[str, Any]:
        """Returns subscription data or a default FREE plan response."""
        sub = self.subscription_repo.get_by_team_id(team_id)
        if sub:
            return sub
        team = self.team_repo.get(team_id)
        now = datetime.now(UTC)
        plan_id = team.plan.value if team else PlanType.FREE.value
        return {
            "stripe_subscription_id": "",
            "status": "active",
            "plan_id": plan_id,
            "current_period_start": now,
            "current_period_end": now + timedelta(days=30),
            "cancel_at_period_end": False,
        }

    def upgrade_plan(
        self, team_id: uuid.UUID, new_plan: PlanType, success_url: str, cancel_url: str
    ):
        """Creates a checkout session to upgrade a team to a paid plan."""
        return self.create_checkout_session(team_id, new_plan, success_url, cancel_url)

    def check_upload_limit(self, team_id: uuid.UUID) -> tuple[bool, str]:
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

    def increment_usage(self, team_id: uuid.UUID, job_id: uuid.UUID | None = None):
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
                description=f"Plan usage: {team.plan.value}",
            )
        elif team.extra_credits > 0:
            self.team_repo.update(team_id, extra_credits=team.extra_credits - 1)
            self.usage_repo.create(
                team_id=team_id,
                job_id=job_id,
                action="upload",
                amount=1,
                description="Credit usage",
            )
        else:
            raise ValueError("Usage limit exceeded and no credits available")

    def create_portal_session(
        self, team_id: uuid.UUID, return_url: str
    ) -> stripe.billing_portal.Session:
        """Creates a Stripe Billing Portal session."""
        team = self.team_repo.get(team_id)
        if not team or not team.stripe_customer_id:
            raise ValueError("Team or Stripe customer not found")

        session = stripe.billing_portal.Session.create(
            customer=team.stripe_customer_id, return_url=return_url
        )
        return session

    def create_checkout_session(
        self, team_id: uuid.UUID, plan_type: PlanType, success_url: str, cancel_url: str
    ) -> stripe.checkout.Session:
        """Creates a Stripe Checkout session for a subscription upgrade."""
        team = self.team_repo.get(team_id)
        if not team:
            raise ValueError("Team not found")

        # Lazily create Stripe customer on first payment
        if not team.stripe_customer_id:
            customer = stripe.Customer.create(
                email="",  # Will be filled by Stripe checkout
                metadata={"team_id": str(team_id)},
            )
            self.team_repo.update(team_id, stripe_customer_id=customer.id)
            team.stripe_customer_id = customer.id

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
            metadata={"team_id": str(team_id), "plan_type": plan_type.value},
        )
        return session

    def create_credits_checkout_session(
        self, team_id: uuid.UUID, amount: int, success_url: str, cancel_url: str
    ) -> stripe.checkout.Session:
        """Creates a Stripe Checkout session for purchasing credits."""
        team = self.team_repo.get(team_id)
        if not team:
            raise ValueError("Team not found")

        # Lazily create Stripe customer on first payment
        if not team.stripe_customer_id:
            customer = stripe.Customer.create(
                email="",  # Will be filled by Stripe checkout
                metadata={"team_id": str(team_id)},
            )
            self.team_repo.update(team_id, stripe_customer_id=customer.id)
            team.stripe_customer_id = customer.id

        # In a real app, you might have a specific price_id for credits,
        # or use ad-hoc line items if permitted.
        # For simplicity, we'll assume a unit price in cents.
        session = stripe.checkout.Session.create(
            customer=team.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": f"{amount} PolyScript Credits"},
                        "unit_amount": CREDIT_PRICE_CENTS,
                    },
                    "quantity": amount,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"team_id": str(team_id), "amount": str(amount), "type": "credits"},
        )
        return session

    def purchase_credits(self, team_id: uuid.UUID, amount: int, success_url: str, cancel_url: str):
        """Creates a checkout session to purchase credits."""
        return self.create_credits_checkout_session(team_id, amount, success_url, cancel_url)

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

        if local_sub:
            self.subscription_repo.update(
                local_sub.id,
                status=sub.status,
                plan_id=plan_id,
                current_period_start=datetime.fromtimestamp(sub.current_period_start, tz=UTC),
                current_period_end=datetime.fromtimestamp(sub.current_period_end, tz=UTC),
                cancel_at_period_end=sub.cancel_at_period_end,
                stripe_data=sub.to_dict(),
            )
        else:
            self.subscription_repo.create(
                team_id=team_id,
                stripe_subscription_id=sub.id,
                status=sub.status,
                plan_id=plan_id,
                current_period_start=datetime.fromtimestamp(sub.current_period_start, tz=UTC),
                current_period_end=datetime.fromtimestamp(sub.current_period_end, tz=UTC),
                cancel_at_period_end=sub.cancel_at_period_end,
                stripe_data=sub.to_dict(),
            )

        # Update Team plan
        self.team_repo.update(team_id, plan=PlanType(plan_type_str))

    def handle_payment_succeeded(self, team_id: uuid.UUID, amount: int, stripe_session_id: str):
        """Handles a successful checkout payment (e.g., for credits)."""
        purchase_repo = CreditPurchaseRepository(self.session)

        # Check if already processed
        # (This is just a simple check, in production you'd want more robust idempotency)
        existing = purchase_repo.get_by_stripe_session_id(stripe_session_id)
        if existing:
            return

        purchase_repo.create(
            team_id=team_id,
            stripe_session_id=stripe_session_id,
            amount=amount,
            price_paid=amount * 100,  # Simplified: $1 per credit
            currency="usd",
        )

        team = self.team_repo.get(team_id)
        self.team_repo.update(team_id, extra_credits=team.extra_credits + amount)

    def cancel_subscription(self, team_id: uuid.UUID, at_period_end: bool = True):
        """Cancels a team's subscription."""
        team = self.team_repo.get(team_id)
        if not team or not team.stripe_subscription_id:
            return

        if at_period_end:
            stripe.Subscription.modify(team.stripe_subscription_id, cancel_at_period_end=True)
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
        item_id = stripe_sub["items"]["data"][0]["id"]

        stripe.Subscription.modify(
            sub.stripe_subscription_id,
            items=[
                {
                    "id": item_id,
                    "price": new_price_id,
                }
            ],
            proration_behavior="always_invoice",  # Charge/Credit immediately
        )

    def reactivate_subscription(self, team_id: uuid.UUID):
        """Reactivates a subscription that is scheduled to cancel."""
        sub = self.subscription_repo.get_by_team_id(team_id)
        if not sub or not sub.stripe_subscription_id:
            raise ValueError("No subscription found")

        stripe.Subscription.modify(sub.stripe_subscription_id, cancel_at_period_end=False)

        # Update local state immediately
        self.subscription_repo.update(sub.id, cancel_at_period_end=False)

    def list_payment_methods(self, team_id: uuid.UUID):
        """Lists attached payment methods for the team."""
        team = self.team_repo.get(team_id)
        if not team or not team.stripe_customer_id:
            return []

        methods = stripe.PaymentMethod.list(customer=team.stripe_customer_id, type="card")
        results: list[dict[str, Any]] = []
        for method in methods.data:
            card = method.get("card") if isinstance(method, dict) else method.card
            if not card:
                continue
            results.append(
                {
                    "id": method["id"] if isinstance(method, dict) else method.id,
                    "brand": card.get("brand"),
                    "last4": card.get("last4"),
                    "exp_month": card.get("exp_month"),
                    "exp_year": card.get("exp_year"),
                }
            )
        return results

    def get_credits(self, team_id: uuid.UUID) -> dict[str, Any]:
        team = self.team_repo.get(team_id)
        if not team:
            raise ValueError("Team not found")
        return {"plan": team.plan, "extra_credits": team.extra_credits}

    def get_usage(self, team_id: uuid.UUID) -> dict[str, Any]:
        team = self.team_repo.get(team_id)
        if not team:
            raise ValueError("Team not found")
        limits = PLAN_LIMITS.get(team.plan.value, PLAN_LIMITS["FREE"])
        monthly_limit = limits["uploads_per_month"]
        if isinstance(monthly_limit, float) and monthly_limit == float("inf"):
            monthly_limit = "inf"
        return {
            "plan": team.plan,
            "monthly_upload_count": team.monthly_upload_count,
            "monthly_limit": monthly_limit,
            "extra_credits": team.extra_credits,
        }

    def get_usage_history(self, team_id: uuid.UUID) -> list[Any]:
        return self.usage_repo.get_by_team_id(team_id)

    def list_invoices(self, team_id: uuid.UUID) -> list[Any]:
        return self.invoice_repo.get_all_by_team(team_id)

    def get_invoice_for_team(self, team_id: uuid.UUID, invoice_id: uuid.UUID) -> Any | None:
        invoice = self.invoice_repo.get(invoice_id)
        if not invoice or invoice.team_id != team_id:
            return None
        return invoice

    def get_invoice_pdf_for_team(self, team_id: uuid.UUID, invoice_id: uuid.UUID) -> str | None:
        invoice = self.get_invoice_for_team(team_id, invoice_id)
        if not invoice:
            return None
        return invoice.invoice_pdf or invoice.hosted_invoice_url

    def list_credit_purchases(self, team_id: uuid.UUID) -> list[Any]:
        return self.credit_repo.get_all_by_team(team_id)

    def get_pricing(self) -> dict[str, Any]:
        plans = []
        for plan, limits in PLAN_LIMITS.items():
            normalized_limits = {
                key: ("inf" if isinstance(value, float) and value == float("inf") else value)
                for key, value in limits.items()
            }
            plans.append(
                {"plan": plan, "limits": normalized_limits, "price_id": PLAN_STRIPE_IDS.get(plan)}
            )
        return {"plans": plans, "credit_price_cents": CREDIT_PRICE_CENTS}

    def create_setup_session(
        self, team_id: uuid.UUID, success_url: str, cancel_url: str
    ) -> stripe.checkout.Session:
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

    def set_default_payment_method(self, team_id: uuid.UUID, payment_method_id: str):
        """Sets default payment method for a Stripe customer."""
        team = self.team_repo.get(team_id)
        if not team or not team.stripe_customer_id:
            raise ValueError("Team or Stripe customer not found")

        pm = stripe.PaymentMethod.retrieve(payment_method_id)
        if pm.customer != team.stripe_customer_id:
            raise ValueError("Payment method does not belong to this team")

        stripe.Customer.modify(
            team.stripe_customer_id, invoice_settings={"default_payment_method": payment_method_id}
        )

    def check_language_available(self, team_id: uuid.UUID, language: str | None) -> bool:
        """Check if language is available in team's plan.

        Args:
            team_id: Team ID
            language: Requested language code (None = auto-detect)

        Returns:
            True if language is available, False otherwise
        """
        if language is None:
            return True

        team = self.team_repo.get(team_id)
        if not team:
            return False

        if language not in SUPPORTED_LANGUAGES:
            return False

        limits = PLAN_LIMITS.get(team.plan.value, PLAN_LIMITS[PlanType.FREE])
        max_languages = limits["languages"]

        if max_languages >= len(SUPPORTED_LANGUAGES):
            return True

        allowed = []
        if team.host_language in SUPPORTED_LANGUAGES:
            allowed.append(team.host_language)
        for lang in SUPPORTED_LANGUAGES:
            if lang not in allowed:
                allowed.append(lang)
            if len(allowed) >= max_languages:
                break

        return language in allowed
