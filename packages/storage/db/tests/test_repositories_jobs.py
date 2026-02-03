import uuid

from poly_db.models import AudioAsset, JobStatus, PlanType, Team, TranscriptionJob
from poly_db.repositories import AudioAssetRepository, TranscriptionJobRepository


def test_job_repositories(session):
    team = Team(name="Jobs Team", plan=PlanType.FREE)
    other_team = Team(name="Other Jobs Team", plan=PlanType.STANDARD)
    session.add_all([team, other_team])
    session.commit()

    job = TranscriptionJob(team_id=team.id, status=JobStatus.QUEUED)
    other_job = TranscriptionJob(team_id=other_team.id, status=JobStatus.QUEUED)
    session.add_all([job, other_job])
    session.commit()

    asset = AudioAsset(
        job_id=job.id,
        storage_uri="local://audio1.wav",
        filename="audio1.wav",
        mime_type="audio/wav",
        file_size=1234,
        duration_seconds=12.5,
    )
    other_asset = AudioAsset(
        job_id=other_job.id,
        storage_uri="local://audio1.wav",
        filename="audio1.wav",
        mime_type="audio/wav",
        file_size=4321,
        duration_seconds=5.0,
    )
    session.add_all([asset, other_asset])
    session.commit()

    job_repo = TranscriptionJobRepository(session)
    assert job.id in [j.id for j in job_repo.get_by_team_id(team.id)]
    assert job.id in [j.id for j in job_repo.get_by_status(team.id, JobStatus.QUEUED)]
    assert job.id in [j.id for j in job_repo.get_by_team_and_status(team.id, JobStatus.QUEUED)]

    asset_repo = AudioAssetRepository(session)
    assert asset_repo.get_by_job_id(job.id).id == asset.id
    assert asset_repo.get_by_storage_uri(team.id, "local://audio1.wav").id == asset.id
    assert asset_repo.get_by_storage_uri(other_team.id, "local://audio1.wav").id == other_asset.id
    assert asset.id in [a.id for a in asset_repo.list_by_team_id(team.id)]


def test_job_repositories_negative_cases(session):
    team = Team(name="Test Jobs", plan=PlanType.FREE)
    session.add(team)
    session.commit()

    job_repo = TranscriptionJobRepository(session)
    assert len(job_repo.get_by_team_id(team.id)) == 0
    assert len(job_repo.get_by_status(team.id, JobStatus.QUEUED)) == 0
    assert len(job_repo.get_by_team_and_status(team.id, JobStatus.RUNNING)) == 0

    asset_repo = AudioAssetRepository(session)
    assert asset_repo.get_by_job_id(uuid.uuid4()) is None
    assert asset_repo.get_by_storage_uri(team.id, "nonexistent") is None
    assert len(asset_repo.list_by_team_id(team.id)) == 0

    job = TranscriptionJob(team_id=team.id, status=JobStatus.SUCCEEDED)
    session.add(job)
    session.commit()

    assert len(job_repo.get_by_status(team.id, JobStatus.FAILED)) == 0
    assert job.id not in [j.id for j in job_repo.get_by_status(team.id, JobStatus.QUEUED)]


def test_job_repositories_base_methods(session):
    team = Team(name="Base Jobs", plan=PlanType.FREE)
    session.add(team)
    session.commit()

    job_repo = TranscriptionJobRepository(session)
    new_job = job_repo.create(team_id=team.id, status=JobStatus.QUEUED)
    assert new_job.id is not None

    updated_job = job_repo.update(new_job.id, status=JobStatus.RUNNING)
    assert updated_job.status == JobStatus.RUNNING

    assert job_repo.delete(new_job.id) is True
    assert job_repo.get(new_job.id) is None

    asset_repo = AudioAssetRepository(session)
    new_job2 = job_repo.create(team_id=team.id, status=JobStatus.QUEUED)
    new_asset = asset_repo.create(
        job_id=new_job2.id,
        storage_uri="local://test.wav",
        filename="test.wav",
        mime_type="audio/wav",
        file_size=1000,
        duration_seconds=5.0,
    )
    assert new_asset.id is not None

    updated_asset = asset_repo.update(new_asset.id, filename="updated.wav")
    assert updated_asset.filename == "updated.wav"

    assert asset_repo.delete(new_asset.id) is True
    assert asset_repo.get(new_asset.id) is None
