"""AI project generation using Gemini or OpenRouter."""

from __future__ import annotations

import json
import logging

import requests

from github_activity_automation.config.settings import AISettings
from github_activity_automation.exceptions import AIServiceError

logger = logging.getLogger(__name__)


class AIService:
    """Generate project metadata and README content."""

    def __init__(self, settings: AISettings) -> None:
        self._settings = settings

    def generate_project_idea(self, language: str) -> tuple[str, str]:
        """Generate a project name and description."""

        prompt = (
            "Return strict JSON with keys name and description for one practical "
            f"{language} backend project. Use a short kebab-case repository name."
        )
        text = self._request_text(prompt)
        try:
            payload = json.loads(text)
            return str(payload["name"]), str(payload["description"])
        except (json.JSONDecodeError, KeyError) as exc:
            raise AIServiceError("AI returned invalid project JSON") from exc

    def generate_readme(self, name: str, description: str, language: str) -> str:
        """Generate README markdown for a project."""

        prompt = (
            f"Write a concise production README for {name}, a {language} project. "
            f"Description: {description}. Include overview, setup, and usage."
        )
        return self._request_text(prompt)

    def _request_text(self, prompt: str) -> str:
        if self._settings.provider == "openrouter":
            return self._request_openrouter(prompt)
        return self._request_gemini(prompt)

    def _request_gemini(self, prompt: str) -> str:
        if not self._settings.gemini_api_key:
            raise AIServiceError("GEMINI_API_KEY is not configured")
        url = self._settings.gemini_url.format(model=self._settings.model)
        response = requests.post(
            url,
            params={"key": self._settings.gemini_api_key},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=self._settings.timeout_seconds,
        )
        if response.status_code >= 400:
            raise AIServiceError(f"Gemini API failed with status {response.status_code}")
        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError) as exc:
            raise AIServiceError("Gemini response did not contain text") from exc

    def _request_openrouter(self, prompt: str) -> str:
        if not self._settings.openrouter_api_key:
            raise AIServiceError("OPENROUTER_API_KEY is not configured")
        response = requests.post(
            self._settings.openrouter_url,
            headers={
                "Authorization": f"Bearer {self._settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._settings.model,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=self._settings.timeout_seconds,
        )
        if response.status_code >= 400:
            raise AIServiceError(f"OpenRouter API failed with status {response.status_code}")
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise AIServiceError("OpenRouter response did not contain text") from exc

