from datetime import datetime, timedelta, timezone
from poly_db.models import Team, PlanType, Subscription, UsageLog, CreditPurchase, Invoice
from poly_db.repositories import (
    TeamRepository,
    SubscriptionRepository,
    UsageLogRepository,
    CreditPurchaseRepository,
    InvoiceRepository,
)
import uuid


def test_billing_repositories(session):
    team = Team(name="Billing Team", plan=PlanType.PRO, stripe_customer_id="cus_123")
    session.add(team)
    session.commit()

    team_repo = TeamRepository(session)
    assert team_repo.get_by_stripe_customer_id("cus_123").id == team.id
    assert team_repo.get_by_name("Billing Team").id == team.id
    assert team.id in [t.id for t in team_repo.list_by_plan(PlanType.PRO)]

    sub = Subscription(
        team_id=team.id,
        stripe_subscription_id="sub_123",
        status="active",
        plan_id="price_pro",
        current_period_start=datetime.now(timezone.utc),
        current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
        cancel_at_period_end=False,
    )
    session.add(sub)

    usage1 = UsageLog(team_id=team.id, action="upload", amount=2, description="test")
    usage2 = UsageLog(team_id=team.id, action="upload", amount=3, description="test")
    session.add_all([usage1, usage2])

    purchase = CreditPurchase(
        team_id=team.id,
        stripe_session_id="cs_123",
        amount=10,
        price_paid=1000,
        currency="usd",
    )
    session.add(purchase)

    invoice = Invoice(
        team_id=team.id,
        stripe_invoice_id="in_123",
        amount_due=1000,
        amount_paid=1000,
        currency="usd",
        status="paid",
        invoice_pdf=None,
        hosted_invoice_url=None,
        period_start=datetime.now(timezone.utc),
        period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )
    session.add(invoice)
    session.commit()

    sub_repo = SubscriptionRepository(session)
    assert sub_repo.get_by_team_id(team.id).id == sub.id
    assert sub_repo.get_by_stripe_subscription_id("sub_123").id == sub.id
    assert sub.id in [s.id for s in sub_repo.list_by_status("active")]

    usage_repo = UsageLogRepository(session)
    assert usage_repo.get_monthly_usage(team.id) == 5
    assert len(usage_repo.get_by_team_id(team.id)) == 2

    purchase_repo = CreditPurchaseRepository(session)
    assert purchase_repo.get_all_by_team(team.id)[0].id == purchase.id
    assert purchase_repo.get_by_stripe_session_id("cs_123").id == purchase.id

    invoice_repo = InvoiceRepository(session)
    assert invoice_repo.get_all_by_team(team.id)[0].id == invoice.id
    assert invoice_repo.get_by_stripe_invoice_id("in_123").id == invoice.id


def test_billing_repositories_negative_cases(session):
    team_repo = TeamRepository(session)
    assert team_repo.get_by_stripe_customer_id("nonexistent") is None
    assert team_repo.get_by_name("nonexistent") is None
    assert len(team_repo.list_by_plan(PlanType.FREE)) == 0

    sub_repo = SubscriptionRepository(session)
    assert sub_repo.get_by_team_id(uuid.uuid4()) is None
    assert sub_repo.get_by_stripe_subscription_id("nonexistent") is None
    assert len(sub_repo.list_by_status("canceled")) == 0

    usage_repo = UsageLogRepository(session)
    assert usage_repo.get_monthly_usage(uuid.uuid4()) == 0
    assert len(usage_repo.get_by_team_id(uuid.uuid4())) == 0

    purchase_repo = CreditPurchaseRepository(session)
    assert len(purchase_repo.get_all_by_team(uuid.uuid4())) == 0
    assert purchase_repo.get_by_stripe_session_id("nonexistent") is None

    invoice_repo = InvoiceRepository(session)
    assert len(invoice_repo.get_all_by_team(uuid.uuid4())) == 0
    assert invoice_repo.get_by_stripe_invoice_id("nonexistent") is None


def test_billing_repositories_base_methods(session):
    team = Team(name="Billing Test", plan=PlanType.FREE)
    session.add(team)
    session.commit()

    team_repo = TeamRepository(session)
    new_team = team_repo.create(name="New Team", plan=PlanType.STANDARD)
    assert new_team.id is not None

    updated_team = team_repo.update(new_team.id, name="Updated Team")
    assert updated_team.name == "Updated Team"

    assert team_repo.delete(new_team.id) is True
    assert team_repo.get(new_team.id) is None

    sub_repo = SubscriptionRepository(session)
    new_sub = sub_repo.create(
        team_id=team.id,
        stripe_subscription_id="sub_new",
        status="active",
        plan_id="price_std",
        current_period_start=datetime.now(timezone.utc),
        current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )
    assert new_sub.id is not None

    updated_sub = sub_repo.update(new_sub.id, status="past_due")
    assert updated_sub.status == "past_due"

    assert sub_repo.delete(new_sub.id) is True
    assert sub_repo.get(new_sub.id) is None

    usage_repo = UsageLogRepository(session)
    new_usage = usage_repo.create(team_id=team.id, action="upload", amount=1, description="test")
    assert new_usage.id is not None

    assert usage_repo.delete(new_usage.id) is True

    purchase_repo = CreditPurchaseRepository(session)
    new_purchase = purchase_repo.create(
        team_id=team.id,
        stripe_session_id="cs_new",
        amount=5,
        price_paid=500,
        currency="usd",
    )
    assert new_purchase.id is not None

    assert purchase_repo.delete(new_purchase.id) is True

    invoice_repo = InvoiceRepository(session)
    new_invoice = invoice_repo.create(
        team_id=team.id,
        stripe_invoice_id="in_new",
        amount_due=500,
        amount_paid=500,
        currency="usd",
        status="paid",
        period_start=datetime.now(timezone.utc),
        period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )
    assert new_invoice.id is not None

    updated_invoice = invoice_repo.update(new_invoice.id, status="void")
    assert updated_invoice.status == "void"

    assert invoice_repo.delete(new_invoice.id) is True
