from poly_db.models import AdminUser, AuditLog
from poly_db.repositories import AdminUserRepository, AuditLogRepository


def test_admin_repositories(session):
    admin = AdminUser(email="admin@example.com", hashed_password="pw", full_name="Admin", is_active=True)
    session.add(admin)
    session.commit()

    log = AuditLog(
        admin_user_id=admin.id,
        target_type="team",
        target_id="team-1",
        action="suspend_team",
        previous_state={"is_suspended": False},
        new_state={"is_suspended": True},
        reason="test",
    )
    session.add(log)
    session.commit()

    admin_repo = AdminUserRepository(session)
    assert admin_repo.get_by_email("admin@example.com").id == admin.id
    assert admin.id in [a.id for a in admin_repo.list_active()]

    audit_repo = AuditLogRepository(session)
    assert log.id in [l.id for l in audit_repo.list_by_admin_user(admin.id)]
    assert log.id in [l.id for l in audit_repo.list_by_target("team", "team-1")]
