from __future__ import annotations

import json
from pathlib import Path

from app.config import BACKEND_ROOT, load_settings
from app.github_client import GitHubClient


def main() -> None:
    settings = load_settings()
    assert settings.github_token, (
        "Set GITHUB_TOKEN in backend/.env before running this script."
    )
    assert settings.github_owner, (
        "Set GITHUB_OWNER in backend/.env before running this script."
    )
    assert settings.github_repo, (
        "Set GITHUB_REPO in backend/.env before running this script."
    )

    pull_requests: list[dict[str, object]] = []

    with GitHubClient(token=settings.github_token) as client:
        for pull_request in client.iter_pull_requests(
            settings.github_owner, settings.github_repo
        ):
            if not pull_request["merged_at"]:
                continue

            number = pull_request["number"]
            files = client.get_pull_request_files(
                settings.github_owner, settings.github_repo, number
            )
            reviews = client.get_pull_request_reviews(
                settings.github_owner, settings.github_repo, number
            )

            pull_requests.append(
                {
                    "number": number,
                    "title": pull_request["title"],
                    "url": pull_request["html_url"],
                    "author_login": pull_request["user"]["login"],
                    "author_avatar": pull_request["user"]["avatar_url"],
                    "created_at": pull_request["created_at"],
                    "merged_at": pull_request["merged_at"],
                    "merged": True,
                    "changed_files_count": pull_request["changed_files"],
                    "top_level_areas": sorted(
                        {
                            Path(file["filename"]).parts[0]
                            for file in files
                            if file["filename"]
                        }
                    ),
                    "reviews": [
                        {
                            "reviewer_login": review["user"]["login"],
                            "review_state": review["state"],
                            "submitted_at": review["submitted_at"],
                        }
                        for review in reviews
                        if review.get("user")
                    ],
                }
            )

    output_path = BACKEND_ROOT / "data" / "pull_requests.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(pull_requests, indent=2), encoding="utf-8")

    print(f"wrote {len(pull_requests)} merged pull requests to {output_path}")


if __name__ == "__main__":
    main()
