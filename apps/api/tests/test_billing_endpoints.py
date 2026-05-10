import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

# Add apps/api to path before other imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# From setup paths import
from . import setup_paths as _setup_paths
from ..main import app

del _setup_paths

from src.dependencies import get_current_team_id as dependency_get_current_team_id
from src.dependencies import get_current_user
from src.routes.billing import get_billing_service, get_current_team_id

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    original = app.dependency_overrides.copy()
    yield
    app.dependency_overrides = original


@pytest.fixture
def mock_billing_service():
    return MagicMock()


@pytest.fixture
def mock_team_id():
    async def _mock_get_current_team_id():
        return uuid.uuid4()

    return _mock_get_current_team_id


@pytest.fixture
def mock_current_user():
    async def _mock_get_current_user():
        return {
            "id": uuid.uuid4(),
            "email": "test@example.com",
            "full_name": "Test User",
            "is_verified": True,
            "is_active": True,
            "is_suspended": False,
            "created_at": "2025-01-01T00:00:00Z",
        }

    return _mock_get_current_user


@pytest.fixture
def override_billing_service(mock_billing_service):
    app.dependency_overrides[get_billing_service] = lambda: mock_billing_service
    return mock_billing_service


def test_get_subscription_not_found(override_billing_service, mock_team_id, mock_current_user):
    app.dependency_overrides[get_current_user] = mock_current_user
    app.dependency_overrides[dependency_get_current_team_id] = mock_team_id
    app.dependency_overrides[get_current_team_id] = mock_team_id
    override_billing_service.get_subscription_or_default.return_value = {
        "stripe_subscription_id": "",
        "status": "active",
        "plan_id": "FREE",
        "current_period_start": datetime(2025, 1, 1, tzinfo=UTC),
        "current_period_end": datetime(2025, 2, 1, tzinfo=UTC),
        "cancel_at_period_end": False,
    }

    response = client.get("/v1/billing/subscription")

    assert response.status_code == 200
    assert response.json()["status"] == "active"
    assert response.json()["plan_id"] == "FREE"


def test_upgrade_plan_success(override_billing_service, mock_team_id):
    app.dependency_overrides[get_current_user] = mock_current_user
    app.dependency_overrides[dependency_get_current_team_id] = mock_team_id
    app.dependency_overrides[get_current_team_id] = mock_team_id
    override_billing_service.create_checkout_session.return_value.url = (
        "http://stripe.com/checkout"
    )

    response = client.post(
        "/v1/billing/subscription/upgrade",
        json={
            "plan": "STANDARD",
            "success_url": "http://localhost/success",
            "cancel_url": "http://localhost/cancel",
        },
    )

    assert response.status_code == 200
    assert response.json()["checkout_url"] == "http://stripe.com/checkout"


def test_create_payment_method_setup_intent(
    override_billing_service, mock_team_id, mock_current_user
):
    app.dependency_overrides[get_current_user] = mock_current_user
    app.dependency_overrides[dependency_get_current_team_id] = mock_team_id
    app.dependency_overrides[get_current_team_id] = mock_team_id
    override_billing_service.create_setup_intent.return_value.client_secret = "seti_secret_123"

    response = client.post("/v1/billing/payment-methods/setup-intent")

    assert response.status_code == 200
    assert response.json()["client_secret"] == "seti_secret_123"
