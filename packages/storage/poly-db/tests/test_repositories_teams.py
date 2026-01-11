from datetime import datetime, timedelta, timezone
from poly_db.models import Team, PlanType, User, TeamMember, TeamRole, TeamInvitation
from poly_db.repositories import TeamMemberRepository, TeamInvitationRepository
import uuid


def test_team_repositories(session):
    team = Team(name="Team Repo", plan=PlanType.FREE)
    user = User(email="member@example.com", is_verified=True)
    session.add_all([team, user])
    session.commit()

    member = TeamMember(team_id=team.id, user_id=user.id, role=TeamRole.ADMIN)
    session.add(member)

    invitation = TeamInvitation(
        team_id=team.id,
        email="invitee@example.com",
        role=TeamRole.MEMBER,
        token="invite-token",
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        accepted_at=None,
    )
    expired_invitation = TeamInvitation(
        team_id=team.id,
        email="expired@example.com",
        role=TeamRole.MEMBER,
        token="expired-token",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        accepted_at=None,
    )
    session.add_all([invitation, expired_invitation])
    session.commit()

    member_repo = TeamMemberRepository(session)
    assert member.id in [m.id for m in member_repo.get_by_team_id(team.id)]
    assert member.id in [m.id for m in member_repo.list_by_user_id(user.id)]
    assert member_repo.get_by_user_and_team(user.id, team.id).id == member.id

    invitation_repo = TeamInvitationRepository(session)
    assert invitation_repo.get_by_token("invite-token").id == invitation.id
    assert invitation.id in [
        i.id for i in invitation_repo.get_by_email(team.id, "invitee@example.com")
    ]
    assert invitation.id in [i.id for i in invitation_repo.list_by_team_id(team.id)]
    deleted = invitation_repo.delete_expired()
    assert expired_invitation.id in [i.id for i in deleted]


def test_team_repositories_negative_cases(session):
    team = Team(name="Team Test", plan=PlanType.FREE)
    user = User(email="user@example.com", is_verified=True)
    other_user = User(email="other@example.com", is_verified=True)
    session.add_all([team, user, other_user])
    session.commit()

    member_repo = TeamMemberRepository(session)
    assert len(member_repo.get_by_team_id(team.id)) == 0
    assert len(member_repo.list_by_user_id(user.id)) == 0
    assert member_repo.get_by_user_and_team(user.id, team.id) is None
    assert member_repo.get_by_user_and_team(user.id, uuid.uuid4()) is None
    assert member_repo.get_by_user_and_team(uuid.uuid4(), team.id) is None

    member = TeamMember(team_id=team.id, user_id=user.id, role=TeamRole.ADMIN)
    session.add(member)
    session.commit()

    assert member_repo.get_by_user_and_team(user.id, team.id).id == member.id
    assert member_repo.get_by_user_and_team(other_user.id, team.id) is None

    invitation_repo = TeamInvitationRepository(session)
    assert invitation_repo.get_by_token("nonexistent") is None
    assert len(invitation_repo.get_by_email(team.id, "unknown@example.com")) == 0
    assert len(invitation_repo.list_by_team_id(uuid.uuid4())) == 0

    active_invitation = TeamInvitation(
        team_id=team.id,
        email="active@example.com",
        role=TeamRole.MEMBER,
        token="active-token",
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    session.add(active_invitation)
    session.commit()

    deleted = invitation_repo.delete_expired()
    assert len(deleted) == 0
    assert invitation_repo.get_by_token("active-token").id == active_invitation.id


def test_team_repositories_base_methods(session):
    team = Team(name="Team Base", plan=PlanType.STANDARD)
    user = User(email="base@example.com", is_verified=True)
    session.add_all([team, user])
    session.commit()

    member_repo = TeamMemberRepository(session)
    new_member = member_repo.create(team_id=team.id, user_id=user.id, role=TeamRole.MEMBER)
    assert new_member.id is not None
    assert new_member.role == TeamRole.MEMBER

    updated_member = member_repo.update(new_member.id, role=TeamRole.VIEWER)
    assert updated_member.role == TeamRole.VIEWER

    assert member_repo.delete(new_member.id) is True
    assert member_repo.get(new_member.id) is None

    assert member_repo.delete(uuid.uuid4()) is False

    invitation_repo = TeamInvitationRepository(session)
    new_invitation = invitation_repo.create(
        team_id=team.id,
        email="new@example.com",
        role=TeamRole.MEMBER,
        token="new-token",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    assert new_invitation.id is not None

    assert new_invitation.id in [i.id for i in invitation_repo.list()]

    updated = invitation_repo.update(new_invitation.id, email="updated@example.com")
    assert updated.email == "updated@example.com"

    assert invitation_repo.delete(new_invitation.id) is True
    assert invitation_repo.get(new_invitation.id) is None
