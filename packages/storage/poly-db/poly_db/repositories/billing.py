from typing import Optional
from sqlalchemy import select
from .base import BaseRepository
from ..models.teams import Team
from ..models.subscriptions import Subscription
from ..models.usage_logs import UsageLog
from ..models.credit_purchases import CreditPurchase
from ..models.invoices import Invoice
import uuid

class TeamRepository(BaseRepository[Team]):
    def __init__(self, session):
        super().__init__(Team, session)

    def get_by_stripe_customer_id(self, stripe_customer_id: str) -> Optional[Team]:
        stmt = select(Team).where(Team.stripe_customer_id == stripe_customer_id)
        return self.session.execute(stmt).scalar_one_or_none()

class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session):
        super().__init__(Subscription, session)

    def get_by_team_id(self, team_id: uuid.UUID) -> Optional[Subscription]:
        stmt = select(Subscription).where(Subscription.team_id == team_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_stripe_subscription_id(self, stripe_id: str) -> Optional[Subscription]:
        stmt = select(Subscription).where(Subscription.stripe_subscription_id == stripe_id)
        return self.session.execute(stmt).scalar_one_or_none()

class UsageLogRepository(BaseRepository[UsageLog]):
    def __init__(self, session):
        super().__init__(UsageLog, session)

    def get_monthly_usage(self, team_id: uuid.UUID) -> int:
        # Simplified for now: just return the current count from Team model
        # but in real usage we might want to aggregate logs
        pass

class CreditPurchaseRepository(BaseRepository[CreditPurchase]):
    def __init__(self, session):
        super().__init__(CreditPurchase, session)

    def get_all_by_team(self, team_id: uuid.UUID) -> list[CreditPurchase]:
        stmt = select(CreditPurchase).where(CreditPurchase.team_id == team_id).order_by(CreditPurchase.created_at.desc())
        return self.session.execute(stmt).scalars().all()

class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session):
        super().__init__(Invoice, session)

    def get_all_by_team(self, team_id: uuid.UUID) -> list[Invoice]:
        stmt = select(Invoice).where(Invoice.team_id == team_id).order_by(Invoice.created_at.desc())
        return self.session.execute(stmt).scalars().all()
