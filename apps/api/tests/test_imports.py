import pytest
from fastapi.testclient import TestClient

# Test that core imports work
def test_core_imports():
    from poly_core.constants import I18nKeys
    from poly_core.services.billing import BillingService

# Test that poly_db imports work
def test_poly_db_imports():
    from poly_db.repositories import TeamRepository
    from poly_db.models.teams import Team

# Test that poly_redis imports work
def test_poly_redis_imports():
    from poly_redis.client import get_redis_client
    from poly_redis.queue import TranscriptionQueue
