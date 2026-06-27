"""Configuration loading tests."""

from pathlib import Path

from github_activity_automation.config.loader import load_settings


def test_configuration_loading(monkeypatch, tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        Path("config.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_USERNAME", "octocat")

    settings = load_settings(str(config_path))

    assert settings.enabled is True
    assert settings.github.token == "token"
    assert settings.project_creator.language == "python"

