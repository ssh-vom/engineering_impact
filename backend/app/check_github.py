from __future__ import annotations

from pprint import pprint

from app.config import load_settings
from app.github_client import GitHubClient


def main() -> None:
    settings = load_settings()
    assert settings.github_token, (
        "Set GITHUB_TOKEN in backend/.env before running this script."
    )

    with GitHubClient(token=settings.github_token) as client:
        viewer = client.get_viewer()
        rate_limit = client.get_rate_limit()["rate"]

    pprint(
        {
            "authenticated": True,
            "viewer": viewer["login"],
            "name": viewer.get("name"),
            "repo_configured": bool(settings.github_owner and settings.github_repo),
            "repo_slug": settings.repo_slug
            if settings.github_owner and settings.github_repo
            else None,
            "rate_limit_remaining": rate_limit["remaining"],
            "rate_limit_limit": rate_limit["limit"],
        }
    )


if __name__ == "__main__":
    main()
