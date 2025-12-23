from poly_db.models import User, UserSettings
from poly_db.repositories import UserSettingsRepository


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
