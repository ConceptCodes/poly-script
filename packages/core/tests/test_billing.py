import uuid
from unittest.mock import MagicMock

import pytest

from poly_core.constants import I18nKeys
from poly_core.services.billing import BillingService
from poly_db.models.teams import PlanType, Team


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def billing_service(mock_session):
    return BillingService(mock_session, "sk_test_mock")


def test_check_upload_limit_free_under_limit(billing_service, mock_session):
    team_id = uuid.uuid4()
    team = MagicMock(spec=Team)
    team.plan = PlanType.FREE
    team.monthly_upload_count = 0
    team.extra_credits = 0
    mock_session.query.return_value.get.return_value = team

    # Mock repository get
    billing_service.team_repo.get = MagicMock(return_value=team)

    allowed, reason = billing_service.check_upload_limit(team_id)
    assert allowed is True
    assert reason == "Limit not reached"


def test_check_upload_limit_free_over_limit_no_credits(billing_service, mock_session):
    team_id = uuid.uuid4()
    team = MagicMock(spec=Team)
    team.plan = PlanType.FREE
    team.monthly_upload_count = 5  # Limit is 5
    team.extra_credits = 0
    billing_service.team_repo.get = MagicMock(return_value=team)

    allowed, reason = billing_service.check_upload_limit(team_id)
    assert allowed is False
    assert reason == I18nKeys.ERR_JOBS_LIMIT_REACHED


def test_check_upload_limit_free_over_limit_with_credits(billing_service, mock_session):
    team_id = uuid.uuid4()
    team = MagicMock(spec=Team)
    team.plan = PlanType.FREE
    team.monthly_upload_count = 5
    team.extra_credits = 1
    billing_service.team_repo.get = MagicMock(return_value=team)

    allowed, reason = billing_service.check_upload_limit(team_id)
    assert allowed is True
    assert reason == "Using extra credits"


def test_increment_usage_free_under_limit(billing_service, mock_session):
    team_id = uuid.uuid4()
    team = MagicMock(spec=Team)
    team.id = team_id
    team.plan = PlanType.FREE
    team.monthly_upload_count = 0
    team.extra_credits = 0
    billing_service.team_repo.get = MagicMock(return_value=team)
    billing_service.team_repo.update = MagicMock()
    billing_service.usage_repo.create = MagicMock()

    billing_service.increment_usage(team_id)

    billing_service.team_repo.update.assert_called_with(team_id, monthly_upload_count=1)
    billing_service.usage_repo.create.assert_called()


def test_increment_usage_credits(billing_service, mock_session):
    team_id = uuid.uuid4()
    team = MagicMock(spec=Team)
    team.id = team_id
    team.plan = PlanType.FREE
    team.monthly_upload_count = 5
    team.extra_credits = 1
    billing_service.team_repo.get = MagicMock(return_value=team)
    billing_service.team_repo.update = MagicMock()
    billing_service.usage_repo.create = MagicMock()

    billing_service.increment_usage(team_id)

    billing_service.team_repo.update.assert_called_with(team_id, extra_credits=0)
    billing_service.usage_repo.create.assert_called()


def test_reset_monthly_usage(billing_service, mock_session):
    team_id = uuid.uuid4()
    billing_service.team_repo.update = MagicMock()

    billing_service.reset_monthly_usage(team_id)

    billing_service.team_repo.update.assert_called_with(team_id, monthly_upload_count=0)
