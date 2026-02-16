"""Async version of Billing repositories for use with SQLAlchemy AsyncSession."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from poly_db.models.credit_purchases import CreditPurchase
from poly_db.models.invoices import Invoice
from poly_db.models.subscriptions import Subscription
from poly_db.models.usage_logs import UsageLog
from poly_db.repositories.base_async import BaseRepositoryAsync


class SubscriptionRepositoryAsync(BaseRepositoryAsync[Subscription]):
    """Async repository for Subscription operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Subscription, session)

    async def get_by_team_id(self, team_id: uuid.UUID) -> Subscription | None:
        """Get a subscription by its team ID."""
        stmt = select(Subscription).where(Subscription.team_id == team_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_stripe_subscription_id(self, stripe_id: str) -> Subscription | None:
        """Get a subscription by its Stripe subscription ID."""
        stmt = select(Subscription).where(Subscription.stripe_subscription_id == stripe_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_status(self, status: str) -> list[Subscription]:
        """List all subscriptions with a specific status."""
        stmt = select(Subscription).where(Subscription.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class UsageLogRepositoryAsync(BaseRepositoryAsync[UsageLog]):
    """Async repository for UsageLog operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(UsageLog, session)

    async def get_monthly_usage(self, team_id: uuid.UUID) -> int:
        """Get the total monthly usage for a specific team."""
        stmt = select(func.coalesce(func.sum(UsageLog.amount), 0)).where(
            UsageLog.team_id == team_id
        )
        result = await self.session.execute(stmt)
        return int(result.scalar() or 0)

    async def get_by_team_id(self, team_id: uuid.UUID) -> list[UsageLog]:
        """Get all usage logs for a specific team, ordered by creation date."""
        stmt = (
            select(UsageLog).where(UsageLog.team_id == team_id).order_by(UsageLog.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class CreditPurchaseRepositoryAsync(BaseRepositoryAsync[CreditPurchase]):
    """Async repository for CreditPurchase operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(CreditPurchase, session)

    async def get_all_by_team(self, team_id: uuid.UUID) -> list[CreditPurchase]:
        """Get all credit purchases for a specific team, ordered by creation date."""
        stmt = (
            select(CreditPurchase)
            .where(CreditPurchase.team_id == team_id)
            .order_by(CreditPurchase.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_stripe_session_id(self, stripe_session_id: str) -> CreditPurchase | None:
        """Get a credit purchase by its Stripe session ID."""
        stmt = select(CreditPurchase).where(CreditPurchase.stripe_session_id == stripe_session_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class InvoiceRepositoryAsync(BaseRepositoryAsync[Invoice]):
    """Async repository for Invoice operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Invoice, session)

    async def get_all_by_team(self, team_id: uuid.UUID) -> list[Invoice]:
        """Get all invoices for a specific team, ordered by creation date."""
        stmt = select(Invoice).where(Invoice.team_id == team_id).order_by(Invoice.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_stripe_invoice_id(self, stripe_invoice_id: str) -> Invoice | None:
        """Get an invoice by its Stripe invoice ID."""
        stmt = select(Invoice).where(Invoice.stripe_invoice_id == stripe_invoice_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


__all__ = [
    "CreditPurchaseRepositoryAsync",
    "InvoiceRepositoryAsync",
    "SubscriptionRepositoryAsync",
    "UsageLogRepositoryAsync",
]
