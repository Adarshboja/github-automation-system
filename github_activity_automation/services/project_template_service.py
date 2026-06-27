"""Project file template generation."""

from __future__ import annotations

from github_activity_automation.config.settings import ProjectCreatorSettings
from github_activity_automation.models.domain import ProjectContent


class ProjectTemplateService:
    """Build initial repository files by language."""

    def __init__(self, settings: ProjectCreatorSettings) -> None:
        self._settings = settings

    def build_content(self, name: str, description: str, readme: str) -> ProjectContent:
        language = self._settings.language
        template = self._settings.templates[language]
        starter_code = self._starter_code(language)
        requirements_filename = "requirements.txt" if language == "python" else "package.json"
        requirements_content = self._requirements_content(language, name)
        return ProjectContent(
            readme=readme,
            gitignore=self._gitignore(language),
            license_text=self._license_text(name),
            starter_filename=template.starter_filename,
            starter_code=starter_code,
            requirements_filename=requirements_filename,
            requirements_content=requirements_content,
        )

    def _starter_code(self, language: str) -> str:
        if language == "javascript":
            return (
                "const express = require('express');\n\n"
                "const app = express();\n"
                "app.get('/health', (_req, res) => res.json({ status: 'ok' }));\n\n"
                "app.listen(3000, () => console.log('Service listening on port 3000'));\n"
            )
        return (
            "from fastapi import FastAPI\n\n"
            "app = FastAPI(title='Generated Service')\n\n\n"
            "@app.get('/health')\n"
            "def health() -> dict[str, str]:\n"
            "    return {'status': 'ok'}\n"
        )

    def _requirements_content(self, language: str, name: str) -> str:
        requirements = self._settings.templates[language].requirements
        if language == "javascript":
            dependencies = ",\n".join(
                f'    "{dependency}": "latest"' for dependency in requirements
            )
            return (
                "{\n"
                f'  "name": "{name}",\n'
                '  "version": "1.0.0",\n'
                '  "main": "index.js",\n'
                '  "scripts": {"start": "node index.js"},\n'
                f'  "dependencies": {{\n{dependencies}\n  }}\n'
                "}\n"
            )
        return "\n".join(requirements) + "\n"

    def _gitignore(self, language: str) -> str:
        if language == "javascript":
            return "node_modules/\n.env\nnpm-debug.log*\n"
        return "__pycache__/\n*.py[cod]\n.env\n.venv/\n*.sqlite3\n"

    def _license_text(self, name: str) -> str:
        return (
            "MIT License\n\n"
            f"Copyright (c) 2026 {name}\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy "
            "of this software and associated documentation files to deal in the Software "
            "without restriction, including without limitation the rights to use, copy, "
            "modify, merge, publish, distribute, sublicense, and/or sell copies of the "
            "Software, and to permit persons to whom the Software is furnished to do so, "
            "subject to the following conditions:\n\n"
            "The above copyright notice and this permission notice shall be included in all "
            "copies or substantial portions of the Software.\n\n"
            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR "
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE "
            "SOFTWARE.\n"
        )
