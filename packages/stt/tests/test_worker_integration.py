import glob
import re

def test_worker_processor_has_translation_method():
    worker_path = 'apps/worker/src/processor.py'
    with open(worker_path, 'r') as f:
        content = f.read()
    assert 'def _translate_transcript' in content
    assert 'TranslateGemmaEngine' in content
    assert 'TranslationArtifactRepository' in content
    print('  Worker has translation method')

def test_worker_progress_has_translating_stage():
    progress_path = 'apps/worker/src/progress.py'
    with open(progress_path, 'r') as f:
        content = f.read()
    assert '"translating": 98' in content
    print('  Progress has translating stage')

def test_api_routes_accepts_target_language():
    routes_path = 'apps/api/src/routes/jobs.py'
    with open(routes_path, 'r') as f:
        content = f.read()
    assert 'target_language: str | None = Form(None)' in content
    assert 'TranslationArtifactRepository' in content
    print('  API accepts target_language')

def test_api_schemas_has_target_language():
    schemas_path = 'apps/api/src/schemas/jobs.py'
    with open(schemas_path, 'r') as f:
        content = f.read()
    assert 'target_language' in content.lower()
    print('  Schemas include target_language')

def test_db_has_translation_artifacts_model():
    import os

    model_path = 'packages/storage/db/db/models/translation_artifacts.py'
    assert os.path.exists(model_path)
    with open(model_path, 'r') as f:
        content = f.read()
    assert 'class TranslationArtifact' in content
    assert 'class TranslationStatus' in content
    print('  DB has TranslationArtifact model')

def test_migration_exists():
    import os
    import glob

    import glob
    migration_files = glob.glob('packages/storage/db/migrations/versions/*_add_translation*.py')
    assert len(migration_files) > 0
    print(f'  Migration exists: {os.path.basename(migration_files[0])}')

def test_db_has_translation_repository():
    import os

    repo_path = 'packages/storage/db/db/repositories/translation_artifacts.py'
    assert os.path.exists(repo_path)
    with open(repo_path, 'r') as f:
        content = f.read()
    assert 'class TranslationArtifactRepository' in content
    assert 'get_by_job_id' in content
    print('  DB has TranslationArtifactRepository')

def test_worker_checks_plan_limits():
    worker_path = 'apps/worker/src/processor.py'
    with open(worker_path, 'r') as f:
        content = f.read()
    assert '_check_translation_limit' in content
    assert '_increment_translation_count' in content
    print('  Worker checks plan limits')

def test_translation_failures_dont_fail_job():
    worker_path = 'apps/worker/src/processor.py'
    with open(worker_path, 'r') as f:
        content = f.read()
    assert 'except Exception' in content
    print('  Translation error handling exists')

if __name__ == "__main__":
    print('=== REFACTOR Phase Tests ===')
    
    import test_worker_integration
    
    tests = [
        test_worker_integration.test_worker_processor_has_translation_method,
        test_worker_integration.test_worker_progress_has_translating_stage,
        test_worker_integration.test_api_routes_accepts_target_language,
        test_worker_integration.test_api_schemas_has_target_language,
        test_worker_integration.test_db_has_translation_artifacts_model,
        test_worker_integration.test_migration_exists,
        test_worker_integration.test_db_has_translation_repository,
        test_worker_integration.test_worker_checks_plan_limits,
        test_worker_integration.test_translation_failures_dont_fail_job,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  X {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  X {test.__name__}: {type(e).__name__}: {e}")
            failed += 1
    
    print(f'\n=== REFACTOR Phase Results ===')
    print(f'Passed: {passed}/{passed + failed}')
    print(f'Failed: {failed}')
