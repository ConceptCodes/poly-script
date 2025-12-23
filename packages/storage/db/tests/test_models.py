import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, User, Team, PlanType, TeamMember, TeamRole

@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(engine):
    """Create a new database session for a test."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_user(session):
    """Test creating a user."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_pw",
        is_verified=True
    )
    session.add(user)
    session.commit()
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.is_verified is True
    assert user.is_active is True

def test_create_team(session):
    """Test creating a team."""
    team = Team(
        name="Test Team",
        plan=PlanType.FREE,
        host_language="en"
    )
    session.add(team)
    session.commit()
    
    assert team.id is not None
    assert team.name == "Test Team"
    assert team.plan == PlanType.FREE
    assert team.monthly_upload_count == 0
    assert team.extra_credits == 0

def test_create_team_member(session):
    """Test creating a team member relationship."""
    user = User(email="user@example.com", is_verified=True)
    team = Team(name="Team 1", plan=PlanType.STANDARD)
    session.add_all([user, team])
    session.commit()
    
    member = TeamMember(
        team_id=team.id,
        user_id=user.id,
        role=TeamRole.ADMIN
    )
    session.add(member)
    session.commit()
    
    assert member.id is not None
    assert member.team_id == team.id
    assert member.user_id == user.id
    assert member.role == TeamRole.ADMIN

def test_soft_delete(session):
    """Test soft delete functionality via TimestampMixin."""
    user = User(email="delete@example.com", is_verified=True)
    session.add(user)
    session.commit()
    
    # Soft delete by setting deleted_at
    from datetime import datetime, timezone
    user.deleted_at = datetime.now(timezone.utc)
    session.commit()
    
    assert user.deleted_at is not None
