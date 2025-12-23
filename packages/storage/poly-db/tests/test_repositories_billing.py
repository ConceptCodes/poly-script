from datetime import datetime, timedelta, timezone
from poly_db.models import Team, PlanType, Subscription, UsageLog, CreditPurchase, Invoice
from poly_db.repositories import (
    TeamRepository,
    SubscriptionRepository,
    UsageLogRepository,
    CreditPurchaseRepository,
    InvoiceRepository,
)


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
