from poly_db.models import Team, PlanType, TranscriptionJob, JobStatus, AudioAsset
from poly_db.repositories import TranscriptionJobRepository, AudioAssetRepository


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
