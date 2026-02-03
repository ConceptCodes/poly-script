from pathlib import Path


def test_worker_processor_has_translation_method():
    worker_path = Path("apps/worker/src/processor.py")
    content = worker_path.read_text()
    assert "def _translate_transcript" in content
    assert "TranslateGemmaEngine" in content
    assert "TranslationArtifactRepository" in content


def test_worker_progress_has_translating_stage():
    progress_path = Path("apps/worker/src/progress.py")
    content = progress_path.read_text()
    assert '"translating": 98' in content


def test_api_routes_accepts_target_language():
    routes_path = Path("apps/api/src/routes/jobs.py")
    content = routes_path.read_text()
    assert "target_language: str | None = Form(None)" in content
    assert "TranslationArtifactRepository" in content


def test_api_schemas_has_target_language():
    schemas_path = Path("apps/api/src/schemas/jobs.py")
    content = schemas_path.read_text()
    assert "target_language" in content.lower()


def test_db_has_translation_artifacts_model():
    model_path = Path("packages/storage/db/db/models/translation_artifacts.py")
    assert model_path.exists()
    content = model_path.read_text()
    assert "class TranslationArtifact" in content
    assert "class TranslationStatus" in content


def test_migration_exists():
    migration_path = Path("packages/storage/db/migrations/versions")
    migration_files = list(migration_path.glob("*_add_translation*.py"))
    assert len(migration_files) > 0


def test_db_has_translation_repository():
    repo_path = Path("packages/storage/db/db/repositories/translation_artifacts.py")
    assert repo_path.exists()
    content = repo_path.read_text()
    assert "class TranslationArtifactRepository" in content
    assert "get_by_job_id" in content


def test_worker_checks_plan_limits():
    worker_path = Path("apps/worker/src/processor.py")
    content = worker_path.read_text()
    assert "_check_translation_limit" in content
    assert "_increment_translation_count" in content


def test_translation_failures_dont_fail_job():
    worker_path = Path("apps/worker/src/processor.py")
    content = worker_path.read_text()
    assert "except Exception" in content
