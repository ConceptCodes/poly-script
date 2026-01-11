from poly_db.models import AdminUser, AuditLog
from poly_db.repositories import AdminUserRepository, AuditLogRepository
import uuid


def test_admin_repositories(session):
    admin = AdminUser(
        email="admin@example.com", hashed_password="pw", full_name="Admin", is_active=True
    )
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


def test_admin_repositories_negative_cases(session):
    admin_repo = AdminUserRepository(session)
    assert admin_repo.get_by_email("nonexistent@example.com") is None
    assert len(admin_repo.list_active()) == 0

    audit_repo = AuditLogRepository(session)
    assert len(audit_repo.list_by_admin_user(uuid.uuid4())) == 0
    assert len(audit_repo.list_by_target("team", "nonexistent")) == 0
    assert len(audit_repo.list_by_target("user", "user-1")) == 0


def test_admin_repositories_base_methods(session):
    admin_repo = AdminUserRepository(session)
    new_admin = admin_repo.create(
        email="new@example.com",
        hashed_password="pw",
        full_name="New Admin",
        is_active=True,
    )
    assert new_admin.id is not None

    updated_admin = admin_repo.update(new_admin.id, full_name="Updated Admin")
    assert updated_admin.full_name == "Updated Admin"

    assert admin_repo.delete(new_admin.id) is True
    assert admin_repo.get(new_admin.id) is None

    admin2 = admin_repo.create(
        email="admin2@example.com",
        hashed_password="pw",
        full_name="Admin 2",
        is_active=False,
    )
    session.add(admin2)
    session.commit()

    audit_repo = AuditLogRepository(session)
    new_log = audit_repo.create(
        admin_user_id=admin2.id,
        target_type="user",
        target_id="user-1",
        action="suspend_user",
        previous_state={"is_active": True},
        new_state={"is_active": False},
        reason="test",
    )
    assert new_log.id is not None

    updated_log = audit_repo.update(new_log.id, reason="updated reason")
    assert updated_log.reason == "updated reason"

    assert audit_repo.delete(new_log.id) is True
    assert audit_repo.get(new_log.id) is None
