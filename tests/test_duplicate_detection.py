"""Project duplicate detection tests."""

from github_activity_automation.repositories.project_repository import ProjectRepository


def test_duplicate_project_name_detection(session):
    repository = ProjectRepository(session)
    repository.record_generated_name("alpha-service", "Alpha service", "fallback")
    session.commit()

    assert repository.project_name_exists("alpha-service") is True
    assert repository.project_name_exists("new-service") is False

