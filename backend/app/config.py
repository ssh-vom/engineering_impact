from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(BACKEND_ROOT / ".env")
load_dotenv()


@dataclass(frozen=True)
class Settings:
    github_token: str
    github_owner: str
    github_repo: str

    @property
    def repo_slug(self) -> str:
        return f"{self.github_owner}/{self.github_repo}"


def load_settings() -> Settings:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    owner = os.environ.get("GITHUB_OWNER", "PostHog").strip()
    repo = os.environ.get("GITHUB_REPO", "posthog").strip()
    return Settings(
        github_token=token,
        github_owner=owner,
        github_repo=repo,
    )
