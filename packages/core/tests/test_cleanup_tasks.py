from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch

from poly_core.tasks.cleanup_tasks import _cleanup_soft_deleted_users_internal


def test_cleanup_soft_deleted_users_deletes_old_users():
    now = datetime.now(UTC)
    old_deleted = Mock(id="old", deleted_at=now - timedelta(days=40))
    recent_deleted = Mock(id="recent", deleted_at=now - timedelta(days=5))
    active = Mock(id="active", deleted_at=None)

    mock_repo = Mock()
    mock_repo.list.return_value = [old_deleted, recent_deleted, active]
    mock_repo.delete.side_effect = lambda user_id: user_id == "old"

    mock_db = Mock()

    with patch("poly_core.tasks.cleanup_tasks.UserRepository", return_value=mock_repo):
        result = _cleanup_soft_deleted_users_internal(mock_db, grace_days=30)

    assert result["deleted_users"] == 1
    mock_repo.delete.assert_called_with("old")
