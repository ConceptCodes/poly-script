from poly_db.models import User, UserSettings
from poly_db.repositories import UserRepository, UserSettingsRepository
import uuid


def test_user_repository(session):
    user = User(email="user@example.com", hashed_password="hashed_pw", is_verified=True)
    session.add(user)
    session.commit()

    repo = UserRepository(session)
    assert repo.get_by_email("user@example.com").id == user.id
    assert repo.get_by_email("nonexistent@example.com") is None

    user.verification_token = "verify-token-123"
    session.commit()
    assert repo.get_by_verification_token("verify-token-123").id == user.id
    assert repo.get_by_verification_token("wrong-token") is None

    assert repo.get(user.id).id == user.id
    assert repo.get_by_id(user.id).id == user.id
    assert user.id in [u.id for u in repo.list()]

    new_user = repo.create(email="new@example.com", hashed_password="pw", is_verified=False)
    assert new_user.id is not None
    assert new_user.email == "new@example.com"

    user_obj = User(email="obj@example.com", hashed_password="pw", is_verified=True)
    created_user = repo.create(obj=user_obj)
    assert created_user.id is not None

    updated_user = repo.update(user.id, email="updated@example.com")
    assert updated_user.email == "updated@example.com"
    updated_obj = repo.update(updated_user, is_verified=False)
    assert updated_obj.is_verified is False

    assert repo.update(uuid.uuid4(), email="test@example.com") is None

    assert repo.delete(new_user.id) is True
    assert repo.get(new_user.id) is None

    assert repo.delete(uuid.uuid4()) is False


def test_user_settings_repository(session):
    user = User(email="settings@example.com", is_verified=True)
    session.add(user)
    session.commit()

    settings = UserSettings(user_id=user.id, host_language="en", notifications={"email": True})
    session.add(settings)
    session.commit()

    repo = UserSettingsRepository(session)
    assert repo.get_by_user_id(user.id).id == settings.id
    assert settings.id in [s.id for s in repo.list_by_language("en")]

    assert repo.get_by_user_id(user.id) is not None
    assert repo.get_by_user_id(uuid.uuid4()) is None

    assert repo.get(settings.id).id == settings.id
    assert settings.id in [s.id for s in repo.list()]

    user2 = User(email="settings2@example.com", is_verified=True)
    session.add(user2)
    session.commit()

    new_settings = repo.create(
        user_id=user2.id,
        host_language="de",
        notifications={"email": False}
    )
    assert new_settings.id is not None
    assert new_settings.host_language == "de"

    updated_settings = repo.update(settings.id, host_language="jp")
    assert updated_settings.host_language == "jp"

    assert repo.delete(new_settings.id) is True
    assert repo.get(new_settings.id) is None
