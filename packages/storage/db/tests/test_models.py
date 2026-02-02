from poly_db.models import User, Team, PlanType, TeamMember, TeamRole
import uuid


def test_create_user(session):
    """Test creating a user."""
    unique_email = f"{uuid.uuid4()}@example.com"
    user = User(email=unique_email, hashed_password="hashed_pw", is_verified=True)
    session.add(user)
    session.commit()

    assert user.id is not None
    assert user.email == unique_email
    assert user.is_verified is True
    assert user.is_active is True


def test_create_team(session):
    """Test creating a team."""
    unique_name = f"Test Team {uuid.uuid4()}"
    team = Team(name=unique_name, plan=PlanType.FREE, host_language="en")
    session.add(team)
    session.commit()

    assert team.id is not None
    assert team.name == unique_name
    assert team.plan == PlanType.FREE
    assert team.monthly_upload_count == 0
    assert team.extra_credits == 0


def test_create_team_member(session):
    """Test creating a team member relationship."""
    unique_email = f"{uuid.uuid4()}@example.com"
    user = User(email=unique_email, is_verified=True)
    unique_name = f"Team {uuid.uuid4()}"
    team = Team(name=unique_name, plan=PlanType.STANDARD)
    session.add_all([user, team])
    session.commit()

    member = TeamMember(team_id=team.id, user_id=user.id, role=TeamRole.ADMIN)
    session.add(member)
    session.commit()

    assert member.id is not None
    assert member.team_id == team.id
    assert member.user_id == user.id
    assert member.role == TeamRole.ADMIN


def test_soft_delete(session):
    """Test soft delete functionality via TimestampMixin."""
    unique_email = f"{uuid.uuid4()}@example.com"
    user = User(email=unique_email, is_verified=True)
    session.add(user)
    session.commit()

    from datetime import datetime, timezone

    user.deleted_at = datetime.now(timezone.utc)
    session.commit()

    assert user.deleted_at is not None
