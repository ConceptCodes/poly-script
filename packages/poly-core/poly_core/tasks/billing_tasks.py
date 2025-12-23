from sqlalchemy.orm import Session
from ..services.billing import BillingService
from poly_db.database import get_session_factory
from poly_db.repositories import TeamRepository
import stripe

def reset_all_monthly_usage(stripe_secret_key: str):
    """Resets monthly usage for all teams. Should be called by a cron job."""
    factory = get_session_factory()
    with factory() as session:
        billing_service = BillingService(session, stripe_secret_key)
        team_repo = TeamRepository(session)
        teams = team_repo.list()
        for team in teams:
            # Here we might check the team's billing cycle date
            # But for simplicity, we reset everyone (could be separate crons)
            billing_service.reset_monthly_usage(team.id)
        session.commit()

def sync_active_subscriptions(stripe_secret_key: str):
    """Syncs active subscriptions with Stripe. Should be called daily."""
    factory = get_session_factory()
    with factory() as session:
        billing_service = BillingService(session, stripe_secret_key)
        # Fetch all stripe subscriptions and sync them
        # This is a bit heavy, maybe just sync those that are active in our DB
        from poly_db.repositories import SubscriptionRepository
        sub_repo = SubscriptionRepository(session)
        subs = sub_repo.list()
        for sub in subs:
            if sub.status == "active":
                billing_service.sync_subscription(sub.stripe_subscription_id)
        session.commit()
