from poly_db.models import Team, PlanType, PaymentMethod
from poly_db.repositories import PaymentMethodRepository
import uuid


def test_payment_method_repository(session):
    team = Team(name="Pay Team", plan=PlanType.FREE)
    session.add(team)
    session.commit()

    pm_default = PaymentMethod(
        team_id=team.id,
        stripe_payment_method_id="pm_1",
        brand="visa",
        last4="4242",
        exp_month=12,
        exp_year=2030,
        is_default=True,
    )
    pm_other = PaymentMethod(
        team_id=team.id,
        stripe_payment_method_id="pm_2",
        brand="mastercard",
        last4="4444",
        exp_month=1,
        exp_year=2031,
        is_default=False,
    )
    session.add_all([pm_default, pm_other])
    session.commit()

    repo = PaymentMethodRepository(session)
    assert len(repo.get_by_team_id(team.id)) == 2
    assert repo.get_default_for_team(team.id).id == pm_default.id
    assert repo.get_by_stripe_payment_method_id("pm_2").id == pm_other.id


def test_payment_method_repository_negative_cases(session):
    team = Team(name="Test Pay", plan=PlanType.FREE)
    session.add(team)
    session.commit()

    repo = PaymentMethodRepository(session)
    assert len(repo.get_by_team_id(team.id)) == 0
    assert repo.get_default_for_team(team.id) is None
    assert repo.get_by_stripe_payment_method_id("nonexistent") is None


def test_payment_method_repository_base_methods(session):
    team = Team(name="Base Pay", plan=PlanType.FREE)
    session.add(team)
    session.commit()

    repo = PaymentMethodRepository(session)
    new_pm = repo.create(
        team_id=team.id,
        stripe_payment_method_id="pm_new",
        brand="amex",
        last4="1234",
        exp_month=6,
        exp_year=2025,
        is_default=False,
    )
    assert new_pm.id is not None

    updated_pm = repo.update(new_pm.id, is_default=True)
    assert updated_pm.is_default is True

    assert repo.delete(new_pm.id) is True
    assert repo.get(new_pm.id) is None

    assert repo.delete(uuid.uuid4()) is False

    pm2 = repo.create(
        team_id=team.id,
        stripe_payment_method_id="pm_2",
        brand="visa",
        last4="5678",
        exp_month=9,
        exp_year=2026,
        is_default=True,
    )
    assert pm2.id is not None
    assert pm2.id in [p.id for p in repo.list()]

    pm3 = repo.create(
        team_id=team.id,
        stripe_payment_method_id="pm_3",
        brand="mastercard",
        last4="9999",
        exp_month=12,
        exp_year=2027,
        is_default=False,
    )
    assert pm3.id is not None

    assert len(repo.get_by_team_id(team.id)) == 2
    assert repo.get_default_for_team(team.id).id == pm2.id

    repo.update(pm2.id, is_default=False)
    repo.update(pm3.id, is_default=True)
    assert repo.get_default_for_team(team.id).id == pm3.id
