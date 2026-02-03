import uuid

from sqlalchemy import select

from poly_db.models.payment_methods import PaymentMethod
from poly_db.repositories.base import BaseRepository


class PaymentMethodRepository(BaseRepository[PaymentMethod]):
    def __init__(self, session):
        super().__init__(PaymentMethod, session)

    def get_by_team_id(self, team_id: uuid.UUID) -> list[PaymentMethod]:
        stmt = select(PaymentMethod).where(PaymentMethod.team_id == team_id)
        return self.session.execute(stmt).scalars().all()

    def get_default_for_team(self, team_id: uuid.UUID) -> PaymentMethod | None:
        stmt = select(PaymentMethod).where(
            PaymentMethod.team_id == team_id, PaymentMethod.is_default.is_(True)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_stripe_payment_method_id(
        self, stripe_payment_method_id: str
    ) -> PaymentMethod | None:
        stmt = select(PaymentMethod).where(
            PaymentMethod.stripe_payment_method_id == stripe_payment_method_id
        )
        return self.session.execute(stmt).scalar_one_or_none()
