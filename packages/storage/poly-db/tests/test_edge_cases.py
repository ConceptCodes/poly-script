from datetime import datetime, timedelta, timezone
from poly_db.models import Team, PlanType, User, TeamMember, TeamRole, UsageLog
from poly_db.repositories import (
    TeamRepository,
    UserRepository,
    TeamMemberRepository,
    UsageLogRepository,
)
import pytest


def test_edge_case_zero_values(session):
    team = Team(name="Zero Team", plan=PlanType.FREE)
    session.add(team)
    session.commit()

    usage = UsageLog(team_id=team.id, action="upload", amount=0, description="zero")
    session.add(usage)
    session.commit()

    usage_repo = UsageLogRepository(session)
    assert usage_repo.get_monthly_usage(team.id) == 0
    assert len(usage_repo.get_by_team_id(team.id)) == 1


def test_edge_case_unicode_strings(session):
    team = Team(
        name="日本語チーム",
        plan=PlanType.FREE,
        host_language="ja",
    )
    session.add(team)
    session.commit()

    team_repo = TeamRepository(session)
    found = team_repo.get_by_name("日本語チーム")
    assert found is not None
    assert found.name == "日本語チーム"


def test_edge_case_future_and_past_dates(session):
    team = Team(name="Date Team", plan=PlanType.FREE)
    user = User(email="date@example.com", hashed_password="pw", is_verified=True)
    session.add_all([team, user])
    session.commit()

    member = TeamMember(
        team_id=team.id,
        user_id=user.id,
        role=TeamRole.ADMIN,
    )
    session.add(member)
    session.commit()

    member_repo = TeamMemberRepository(session)
    found = member_repo.get_by_user_and_team(user.id, team.id)
    assert found is not None
    if found.created_at.tzinfo is not None:
        assert found.created_at < datetime.now(timezone.utc)
    else:
        assert found.created_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc)


def test_edge_case_multiple_same_values(session):
    team = Team(name="Same Team", plan=PlanType.FREE)
    session.add(team)
    session.commit()

    usage1 = UsageLog(team_id=team.id, action="upload", amount=5, description="same")
    usage2 = UsageLog(team_id=team.id, action="upload", amount=5, description="same")
    usage3 = UsageLog(team_id=team.id, action="upload", amount=5, description="same")
    session.add_all([usage1, usage2, usage3])
    session.commit()

    usage_repo = UsageLogRepository(session)
    assert usage_repo.get_monthly_usage(team.id) == 15
    assert len(usage_repo.get_by_team_id(team.id)) == 3


def test_edge_case_case_sensitivity(session):
    team = Team(name="CaseTeam", plan=PlanType.FREE)
    session.add(team)
    session.commit()

    team_repo = TeamRepository(session)
    assert team_repo.get_by_name("caseteam") is None
    assert team_repo.get_by_name("CaseTeam").id == team.id

    user = User(email="test@example.com", hashed_password="pw", is_verified=True)
    session.add(user)
    session.commit()

    user_repo = UserRepository(session)
    assert user_repo.get_by_email("test@example.com").id == user.id
    assert user_repo.get_by_email("different@example.com") is None
