from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
import pytest
from poly_db.models.teams import PlanType
from poly_db.models.subscriptions import Subscription
import uuid
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def mock_billing_service():
    with patch("src.routes.billing.BillingService") as mock:
        yield mock

@pytest.fixture
def mock_db_session():
    with patch("src.routes.billing.get_db_session") as mock:
        yield mock

def test_get_subscription_not_found(mock_db_session):
    # Mock return value of get_by_team_id to None
    with patch("poly_db.repositories.SubscriptionRepository.get_by_team_id", return_value=None):
        response = client.get("/v1/billing/subscription")
        assert response.status_code == 200
        assert response.json()["status"] == "active"
        assert response.json()["plan_id"] == "FREE"

def test_upgrade_plan_success(mock_billing_service):
    # Override auth dependency to avoid DB hit
    async def mock_get_current_team_id():
        return uuid.uuid4()
    
    app.dependency_overrides[uuid.UUID] = mock_get_current_team_id # This mock might be tricky if it dep is used elsewhere
    # Better to override by function reference
    from src.routes.billing import get_current_team_id
    app.dependency_overrides[get_current_team_id] = mock_get_current_team_id
    
    mock_instance = mock_billing_service.return_value
    mock_instance.create_checkout_session.return_value.url = "http://stripe.com/checkout"
    
    response = client.post("/v1/billing/subscription/upgrade", json={
        "plan": "STANDARD",
        "success_url": "http://localhost/success",
        "cancel_url": "http://localhost/cancel"
    })
    
    assert response.status_code == 200
    assert response.json()["checkout_url"] == "http://stripe.com/checkout"
