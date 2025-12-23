from typing import Optional
from sqlalchemy import select, func
from .base import BaseRepository
from ..models.teams import Team, PlanType
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

    def get_by_name(self, name: str) -> Optional[Team]:
        stmt = select(Team).where(Team.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_plan(self, plan: PlanType) -> list[Team]:
        stmt = select(Team).where(Team.plan == plan)
        return self.session.execute(stmt).scalars().all()


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session):
        super().__init__(Subscription, session)

    def get_by_team_id(self, team_id: uuid.UUID) -> Optional[Subscription]:
        stmt = select(Subscription).where(Subscription.team_id == team_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_stripe_subscription_id(self, stripe_id: str) -> Optional[Subscription]:
        stmt = select(Subscription).where(Subscription.stripe_subscription_id == stripe_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_status(self, status: str) -> list[Subscription]:
        stmt = select(Subscription).where(Subscription.status == status)
        return self.session.execute(stmt).scalars().all()


class UsageLogRepository(BaseRepository[UsageLog]):
    def __init__(self, session):
        super().__init__(UsageLog, session)

    def get_monthly_usage(self, team_id: uuid.UUID) -> int:
        stmt = select(func.coalesce(func.sum(UsageLog.amount), 0)).where(
            UsageLog.team_id == team_id
        )
        return int(self.session.execute(stmt).scalar_one() or 0)

    def get_by_team_id(self, team_id: uuid.UUID) -> list[UsageLog]:
        stmt = (
            select(UsageLog).where(UsageLog.team_id == team_id).order_by(UsageLog.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()


class CreditPurchaseRepository(BaseRepository[CreditPurchase]):
    def __init__(self, session):
        super().__init__(CreditPurchase, session)

    def get_all_by_team(self, team_id: uuid.UUID) -> list[CreditPurchase]:
        stmt = (
            select(CreditPurchase)
            .where(CreditPurchase.team_id == team_id)
            .order_by(CreditPurchase.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def get_by_stripe_session_id(self, stripe_session_id: str) -> Optional[CreditPurchase]:
        stmt = select(CreditPurchase).where(CreditPurchase.stripe_session_id == stripe_session_id)
        return self.session.execute(stmt).scalar_one_or_none()


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session):
        super().__init__(Invoice, session)

    def get_all_by_team(self, team_id: uuid.UUID) -> list[Invoice]:
        stmt = select(Invoice).where(Invoice.team_id == team_id).order_by(Invoice.created_at.desc())
        return self.session.execute(stmt).scalars().all()

    def get_by_stripe_invoice_id(self, stripe_invoice_id: str) -> Optional[Invoice]:
        stmt = select(Invoice).where(Invoice.stripe_invoice_id == stripe_invoice_id)
        return self.session.execute(stmt).scalar_one_or_none()
