from datetime import datetime, timedelta, timezone
from poly_db.models import Team, PlanType, User, TeamMember, TeamRole, TeamInvitation
from poly_db.repositories import TeamMemberRepository, TeamInvitationRepository


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
    session.add(invitation)
    session.commit()

    member_repo = TeamMemberRepository(session)
    assert member.id in [m.id for m in member_repo.get_by_team_id(team.id)]
    assert member.id in [m.id for m in member_repo.get_by_user_id(user.id)]

    invitation_repo = TeamInvitationRepository(session)
    assert invitation_repo.get_by_token("invite-token").id == invitation.id
    assert invitation.id in [i.id for i in invitation_repo.get_by_email("invitee@example.com")]
