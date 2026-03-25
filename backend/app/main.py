from __future__ import annotations

from fastapi import FastAPI

from app.config import load_settings
from app.github_client import GitHubClient

app = FastAPI(title="Engineering Impact API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/github/check")
def github_check() -> dict[str, object]:
    settings = load_settings()
    assert settings.github_token, "GITHUB_TOKEN is not set"

    with GitHubClient(token=settings.github_token) as client:
        viewer = client.get_viewer()
        rate_limit = client.get_rate_limit()["rate"]

    return {
        "authenticated": True,
        "viewer": {
            "login": viewer["login"],
            "name": viewer.get("name"),
        },
        "rate_limit": {
            "remaining": rate_limit["remaining"],
            "limit": rate_limit["limit"],
            "reset": rate_limit["reset"],
        },
        "repo": {
            "owner": settings.github_owner,
            "name": settings.github_repo,
            "configured": bool(settings.github_owner and settings.github_repo),
        },
    }
