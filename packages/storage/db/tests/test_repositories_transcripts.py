import uuid

from poly_db.models import PlanType, Team, Transcript, TranscriptEdit, TranscriptionJob, User
from poly_db.repositories import TranscriptEditRepository, TranscriptRepository


def test_transcript_repositories(session):
    team = Team(name="Transcript Team", plan=PlanType.STANDARD)
    other_team = Team(name="Other Transcript Team", plan=PlanType.FREE)
    user = User(email="editor@example.com", is_verified=True)
    session.add_all([team, other_team, user])
    session.commit()

    job = TranscriptionJob(team_id=team.id)
    other_job = TranscriptionJob(team_id=other_team.id)
    session.add_all([job, other_job])
    session.commit()

    transcript = Transcript(
        job_id=job.id,
        text="hello world",
        language="en",
        segments={"segments": []},
        engine_version="v1",
    )
    other_transcript = Transcript(
        job_id=other_job.id,
        text="other team",
        language="en",
        segments={"segments": []},
        engine_version="v1",
    )
    session.add_all([transcript, other_transcript])
    session.commit()

    edit = TranscriptEdit(
        transcript_id=transcript.id,
        user_id=user.id,
        previous_text="hello",
        new_text="hello world",
        previous_segments={"segments": []},
        new_segments={"segments": []},
    )
    session.add(edit)
    session.commit()

    transcript_repo = TranscriptRepository(session)
    assert transcript_repo.get_by_job_id(team.id, job.id).id == transcript.id
    assert transcript.id in [t.id for t in transcript_repo.list_by_language(team.id, "en")]
    assert other_transcript.id not in [
        t.id for t in transcript_repo.list_by_language(team.id, "en")
    ]
    assert transcript.id in [t.id for t in transcript_repo.list_recent(team.id, limit=5)]
    assert other_transcript.id not in [t.id for t in transcript_repo.list_recent(team.id, limit=5)]

    edit_repo = TranscriptEditRepository(session)
    assert edit.id in [e.id for e in edit_repo.get_history_by_transcript_id(team.id, transcript.id)]
    assert edit.id in [e.id for e in edit_repo.list_by_user_id(team.id, user.id)]


def test_transcript_repositories_negative_cases(session):
    team = Team(name="Test Transcript", plan=PlanType.FREE)
    user = User(email="editor2@example.com", is_verified=True)
    session.add_all([team, user])
    session.commit()

    job = TranscriptionJob(team_id=team.id)
    session.add(job)
    session.commit()

    transcript_repo = TranscriptRepository(session)
    assert transcript_repo.get_by_job_id(team.id, job.id) is None
    assert len(transcript_repo.list_by_language(team.id, "en")) == 0
    assert len(transcript_repo.list_recent(team.id, limit=5)) == 0

    edit_repo = TranscriptEditRepository(session)
    assert len(edit_repo.get_history_by_transcript_id(team.id, uuid.uuid4())) == 0
    assert len(edit_repo.list_by_user_id(team.id, user.id)) == 0

    transcript = Transcript(
        job_id=job.id,
        text="test transcript",
        language="en",
        segments={"segments": []},
        engine_version="v1",
    )
    session.add(transcript)
    session.commit()

    assert transcript_repo.get_by_job_id(team.id, uuid.uuid4()) is None
    assert len(transcript_repo.list_by_language(team.id, "de")) == 0


def test_transcript_repositories_base_methods(session):
    team = Team(name="Base Transcript", plan=PlanType.FREE)
    user = User(email="editor3@example.com", is_verified=True)
    session.add_all([team, user])
    session.commit()

    job = TranscriptionJob(team_id=team.id)
    session.add(job)
    session.commit()

    transcript_repo = TranscriptRepository(session)
    new_transcript = transcript_repo.create(
        job_id=job.id,
        text="new transcript",
        language="en",
        segments={"segments": []},
        engine_version="v1",
    )
    assert new_transcript.id is not None

    updated_transcript = transcript_repo.update(new_transcript.id, text="updated transcript")
    assert updated_transcript.text == "updated transcript"

    assert transcript_repo.delete(new_transcript.id) is True
    assert transcript_repo.get(new_transcript.id) is None

    transcript2 = transcript_repo.create(
        job_id=job.id,
        text="another transcript",
        language="es",
        segments={"segments": []},
        engine_version="v1",
    )
    session.add(transcript2)
    session.commit()

    edit_repo = TranscriptEditRepository(session)
    new_edit = edit_repo.create(
        transcript_id=transcript2.id,
        user_id=user.id,
        previous_text="old",
        new_text="new",
        previous_segments={"segments": []},
        new_segments={"segments": []},
    )
    assert new_edit.id is not None

    updated_edit = edit_repo.update(new_edit.id, new_text="updated")
    assert updated_edit.new_text == "updated"

    assert edit_repo.delete(new_edit.id) is True
    assert edit_repo.get(new_edit.id) is None
