from poly_db.models import Team, PlanType, PaymentMethod
from poly_db.repositories import PaymentMethodRepository


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
