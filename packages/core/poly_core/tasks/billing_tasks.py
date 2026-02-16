from datetime import UTC, datetime

from sqlalchemy.orm import Session

from poly_core.services.billing import BillingService
from poly_db.database import get_session_factory
from poly_db.repositories import SubscriptionRepository, TeamRepository


def _reset_all_monthly_usage_internal(db: Session, stripe_secret_key: str):
    """Resets monthly usage for all teams. Should be called by a cron job - internal function"""
    billing_service = BillingService(db, stripe_secret_key)
    team_repo = TeamRepository(db)
    teams = team_repo.list()
    for team in teams:
        if hasattr(team, "monthly_reset_date") and team.monthly_reset_date:
            if team.monthly_reset_date <= datetime.now(UTC):
                billing_service.reset_monthly_usage(team.id)
        else:
            billing_service.reset_monthly_usage(team.id)
    db.commit()


def _sync_active_subscriptions_internal(db: Session, stripe_secret_key: str):
    """Syncs active subscriptions with Stripe. Should be called daily - internal function"""
    billing_service = BillingService(db, stripe_secret_key)
    # Fetch all stripe subscriptions and sync them
    # This is a bit heavy, maybe just sync those that are active in our DB
    sub_repo = SubscriptionRepository(db)
    subs = sub_repo.list()
    for sub in subs:
        if sub.status in {"active", "trialing", "past_due"}:
            billing_service.sync_subscription(sub.stripe_subscription_id)
    db.commit()


# Public wrapper functions for APScheduler (create their own DB sessions)
def reset_all_monthly_usage():
    """Resets monthly usage for all teams. Should be called by a cron job."""
    import os
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", "")
    factory = get_session_factory()
    with factory() as db:
        return _reset_all_monthly_usage_internal(db, stripe_secret_key)


def sync_active_subscriptions():
    """Syncs active subscriptions with Stripe. Should be called daily."""
    import os
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", "")
    factory = get_session_factory()
    with factory() as db:
        return _sync_active_subscriptions_internal(db, stripe_secret_key)
