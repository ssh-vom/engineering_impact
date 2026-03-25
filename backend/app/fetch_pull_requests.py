from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, cast

from app.config import BACKEND_ROOT, load_settings
from app.github_client import GitHubClient
from app.scoring import build_dashboard
from app.schema import PullRequestRecord, RawPullRequestData

WINDOW_DAYS = 90
TOP_CANDIDATE_COUNT = 10
MAX_CLOSED_PAGES = int(os.environ.get("MAX_CLOSED_PAGES", "0"))
MAX_MERGED_PAGES = int(os.environ.get("MAX_MERGED_PAGES", "0"))
MAX_ENRICHED_PRS = int(os.environ.get("MAX_ENRICHED_PRS", "0"))
PARTIAL_RAW_PATH = BACKEND_ROOT / "data" / "pull_requests.partial.json"
FINAL_RAW_PATH = BACKEND_ROOT / "data" / "pull_requests.json"
PARTIAL_DASHBOARD_PATH = BACKEND_ROOT / "data" / "dashboard.partial.json"
FINAL_DASHBOARD_PATH = BACKEND_ROOT / "data" / "dashboard.json"


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def pull_request_to_record(
    pull_request: dict[str, Any], top_level_areas: list[str] | None = None
) -> PullRequestRecord:
    reviews = pull_request["reviews"]["nodes"]
    author = pull_request["author"] or {}
    return {
        "number": pull_request["number"],
        "title": pull_request["title"],
        "url": pull_request["url"],
        "author_login": author.get("login", "unknown"),
        "author_avatar": author.get("avatarUrl", ""),
        "created_at": pull_request["createdAt"],
        "merged_at": pull_request["mergedAt"],
        "merged": True,
        "changed_files_count": pull_request["changedFiles"],
        "top_level_areas": top_level_areas or [],
        "reviews": [
            {
                "reviewer_login": review["author"]["login"],
                "review_state": review["state"],
                "submitted_at": review["submittedAt"],
            }
            for review in reviews
            if review.get("author") and review.get("submittedAt")
        ],
    }


def extract_top_level_areas(files: list[dict[str, Any]]) -> list[str]:
    return sorted(
        {Path(file["filename"]).parts[0] for file in files if file["filename"]}
    )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_dashboard_files(raw_data: dict[str, Any], *, final: bool) -> dict[str, Any]:
    dashboard = build_dashboard(cast(RawPullRequestData, raw_data))
    write_json(PARTIAL_RAW_PATH, raw_data)
    write_json(PARTIAL_DASHBOARD_PATH, dashboard)
    if final:
        write_json(FINAL_RAW_PATH, raw_data)
        write_json(FINAL_DASHBOARD_PATH, dashboard)
    return dashboard


def candidate_logins_from_dashboard(dashboard: dict[str, Any]) -> list[str]:
    return [
        engineer["login"]
        for engineer in dashboard["topEngineers"][:TOP_CANDIDATE_COUNT]
    ]


def count_closed_pull_requests(
    client: GitHubClient, owner: str, repo: str, cutoff: datetime
) -> tuple[int, int, int]:
    after: str | None = None
    page_count = 0
    closed_count = 0
    merged_count = 0

    while True:
        page = client.get_closed_pull_request_page(owner, repo, after)
        page_count += 1
        nodes = page["pullRequests"]["nodes"]
        if not nodes:
            return closed_count, merged_count, page_count

        latest_remaining = page["rateLimit"]["remaining"]
        print(
            f"closed-pr page {page_count}: {len(nodes)} nodes, remaining rate limit {latest_remaining}"
        )

        keep_going = False
        for node in nodes:
            closed_at = parse_datetime(node["closedAt"])
            if closed_at is None:
                continue
            if closed_at >= cutoff:
                closed_count += 1
                if node["mergedAt"] is not None:
                    merged_count += 1
                keep_going = True

        if not page["pullRequests"]["pageInfo"]["hasNextPage"]:
            return closed_count, merged_count, page_count
        if not keep_going:
            return closed_count, merged_count, page_count
        if MAX_CLOSED_PAGES and page_count >= MAX_CLOSED_PAGES:
            print(f"stopping closed-pr scan early at page limit {MAX_CLOSED_PAGES}")
            return closed_count, merged_count, page_count

        after = page["pullRequests"]["pageInfo"]["endCursor"]


def fetch_merged_pull_requests(
    client: GitHubClient,
    owner: str,
    repo: str,
    cutoff: datetime,
    on_page: Callable[[list[PullRequestRecord], int], None] | None = None,
) -> tuple[list[PullRequestRecord], int, int]:
    after: str | None = None
    page_count = 0
    records: list[PullRequestRecord] = []

    while True:
        page = client.get_pull_request_page(owner, repo, ["MERGED"], after)
        page_count += 1
        nodes = page["pullRequests"]["nodes"]
        if not nodes:
            return records, page_count, 0

        latest_remaining = page["rateLimit"]["remaining"]
        print(
            f"merged-pr page {page_count}: {len(nodes)} nodes, remaining rate limit {latest_remaining}"
        )

        keep_going = False
        for node in nodes:
            merged_at = parse_datetime(node["mergedAt"])
            if merged_at is None:
                continue
            if merged_at < cutoff:
                continue

            keep_going = True
            records.append(pull_request_to_record(node))

            if len(records) % 25 == 0:
                print(f"processed {len(records)} merged pull requests")

        if on_page is not None:
            on_page(records, page_count)

        if not page["pullRequests"]["pageInfo"]["hasNextPage"]:
            return records, page_count, 0
        if not keep_going:
            return records, page_count, 0
        if MAX_MERGED_PAGES and page_count >= MAX_MERGED_PAGES:
            print(f"stopping merged-pr scan early at page limit {MAX_MERGED_PAGES}")
            return records, page_count, 0

        after = page["pullRequests"]["pageInfo"]["endCursor"]


def enrich_candidate_pull_requests(
    client: GitHubClient,
    owner: str,
    repo: str,
    pull_requests: list[PullRequestRecord],
    candidate_logins: list[str],
) -> int:
    rest_file_requests = 0
    candidate_set = set(candidate_logins)
    candidate_pull_requests = [
        pull_request
        for pull_request in pull_requests
        if pull_request["author_login"] in candidate_set
    ]
    if MAX_ENRICHED_PRS:
        candidate_pull_requests = candidate_pull_requests[:MAX_ENRICHED_PRS]

    print(
        f"starting targeted area enrichment for {len(candidate_pull_requests)} pull requests across {len(candidate_logins)} candidates"
    )

    for index, pull_request in enumerate(candidate_pull_requests, start=1):
        files = client.get_pull_request_files(owner, repo, pull_request["number"])
        pull_request["top_level_areas"] = extract_top_level_areas(files)
        rest_file_requests += 1
        if index % 10 == 0 or index == len(candidate_pull_requests):
            print(
                f"enriched {index}/{len(candidate_pull_requests)} candidate pull requests"
            )

    return rest_file_requests


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

    generated_at = datetime.now(UTC)
    cutoff = generated_at - timedelta(days=WINDOW_DAYS)
    raw_data: dict[str, Any] = {
        "summary": {
            "repo": settings.repo_slug,
            "windowDays": WINDOW_DAYS,
            "generatedAt": generated_at.isoformat(),
            "closedPrs": 0,
            "mergedPrs": 0,
            "graphqlPagesFetched": 0,
            "restFileRequests": 0,
            "phase": "counting_closed_prs",
            "topCandidateLogins": [],
            "areaEnrichmentComplete": False,
        },
        "pullRequests": [],
    }

    with GitHubClient(token=settings.github_token) as client:
        closed_prs, merged_prs, closed_pages = count_closed_pull_requests(
            client, settings.github_owner, settings.github_repo, cutoff
        )
        raw_data["summary"]["closedPrs"] = closed_prs
        raw_data["summary"]["mergedPrs"] = merged_prs
        raw_data["summary"]["graphqlPagesFetched"] = closed_pages
        write_json(PARTIAL_RAW_PATH, raw_data)

        def on_merged_page(records: list[PullRequestRecord], page_count: int) -> None:
            raw_data["pullRequests"] = list(records)
            raw_data["summary"]["graphqlPagesFetched"] = closed_pages + page_count
            raw_data["summary"]["phase"] = "provisional_scoring"
            provisional_dashboard = write_dashboard_files(raw_data, final=False)
            candidate_logins = candidate_logins_from_dashboard(provisional_dashboard)
            raw_data["summary"]["topCandidateLogins"] = candidate_logins
            print(
                "provisional top 5: "
                + ", ".join(
                    f"{engineer['rank']}. {engineer['login']} ({engineer['impactScore']})"
                    for engineer in provisional_dashboard["topEngineers"]
                )
            )

        pull_requests, merged_pages, _ = fetch_merged_pull_requests(
            client,
            settings.github_owner,
            settings.github_repo,
            cutoff,
            on_page=on_merged_page,
        )

        raw_data["pullRequests"] = pull_requests
        raw_data["summary"]["graphqlPagesFetched"] = closed_pages + merged_pages
        raw_data["summary"]["phase"] = "provisional_scoring"
        provisional_dashboard = write_dashboard_files(raw_data, final=False)
        candidate_logins = candidate_logins_from_dashboard(provisional_dashboard)
        raw_data["summary"]["topCandidateLogins"] = candidate_logins

        print(f"current top candidates: {', '.join(candidate_logins[:5])}")

        raw_data["summary"]["phase"] = "targeted_area_enrichment"
        rest_file_requests = enrich_candidate_pull_requests(
            client,
            settings.github_owner,
            settings.github_repo,
            raw_data["pullRequests"],
            candidate_logins,
        )

    raw_data["summary"]["restFileRequests"] = rest_file_requests
    raw_data["summary"]["phase"] = "complete"
    raw_data["summary"]["areaEnrichmentComplete"] = True
    dashboard = write_dashboard_files(raw_data, final=True)

    print(
        f"wrote {len(raw_data['pullRequests'])} merged pull requests to {FINAL_RAW_PATH}"
    )
    print(f"wrote dashboard to {FINAL_DASHBOARD_PATH}")
    print(
        "request summary: "
        f"graphql_pages={raw_data['summary']['graphqlPagesFetched']}, "
        f"rest_file_requests={rest_file_requests}, "
        f"closed_prs={closed_prs}, merged_prs={merged_prs}"
    )
    print(
        "top 5 engineers: "
        + ", ".join(
            f"{engineer['rank']}. {engineer['login']} ({engineer['impactScore']})"
            for engineer in dashboard["topEngineers"]
        )
    )


if __name__ == "__main__":
    main()
