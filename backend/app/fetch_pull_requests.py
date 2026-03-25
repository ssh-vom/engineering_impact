from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
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
    cutoff = datetime.now(UTC) - timedelta(days=90)
    merged_since = cutoff.date().isoformat()
    processed = 0

    print(f"fetching merged pull requests since {merged_since}")

    with GitHubClient(token=settings.github_token) as client:
        for search_result in client.iter_merged_pull_requests_since(
            settings.github_owner, settings.github_repo, merged_since
        ):
            processed += 1
            number = search_result["number"]
            pull_request = client.get_pull_request(
                settings.github_owner, settings.github_repo, number
            )
            merged_at = pull_request["merged_at"]
            if not merged_at:
                continue

            merged_at_dt = datetime.fromisoformat(merged_at.replace("Z", "+00:00"))
            if merged_at_dt < cutoff:
                continue

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
                    "merged_at": merged_at,
                    "merged": True,
                    "changed_files_count": len(files),
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

            if processed % 25 == 0:
                print(f"processed {processed} pull requests")

    output_path = BACKEND_ROOT / "data" / "pull_requests.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(pull_requests, indent=2), encoding="utf-8")

    print(f"wrote {len(pull_requests)} merged pull requests to {output_path}")


if __name__ == "__main__":
    main()
