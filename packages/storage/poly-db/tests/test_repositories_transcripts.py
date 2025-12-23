from poly_db.models import Team, PlanType, TranscriptionJob, Transcript, TranscriptEdit, User
from poly_db.repositories import TranscriptRepository, TranscriptEditRepository


def test_transcript_repositories(session):
    team = Team(name="Transcript Team", plan=PlanType.STANDARD)
    user = User(email="editor@example.com", is_verified=True)
    session.add_all([team, user])
    session.commit()

    job = TranscriptionJob(team_id=team.id)
    session.add(job)
    session.commit()

    transcript = Transcript(
        job_id=job.id,
        text="hello world",
        language="en",
        segments={"segments": []},
        engine_version="v1",
    )
    session.add(transcript)
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
    assert transcript_repo.get_by_job_id(job.id).id == transcript.id
    assert transcript.id in [t.id for t in transcript_repo.list_by_language("en")]
    assert transcript.id in [t.id for t in transcript_repo.list_recent(limit=5)]

    edit_repo = TranscriptEditRepository(session)
    assert edit.id in [e.id for e in edit_repo.get_history_by_transcript_id(transcript.id)]
    assert edit.id in [e.id for e in edit_repo.list_by_user_id(user.id)]
