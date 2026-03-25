from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.schema import PullRequestRecord, RawPullRequestData
from app.utils import hours_between, median_or_none, min_max_scores, round_score

WEIGHTS = {
    "mergedPrs": 0.35,
    "meaningfulPrs": 0.45,
    "reviewsGiven": 0.20,
}

IMPACT_DEFINITION = "Impact combines shipping volume, substantial merged work, and review support over the last 90 days."

MEANINGFUL_PR_DEFINITION = "A merged PR is meaningful when it hits at least 2 of 3 depth signals: 5+ changed files, 2+ top-level areas, or 2+ reviews."

REVIEW_STATES = {"APPROVED", "CHANGES_REQUESTED"}


def is_meaningful_pr(pull_request: PullRequestRecord) -> bool:
    score = 0
    if pull_request["changed_files_count"] >= 5:
        score += 1
    if len(pull_request["top_level_areas"]) >= 2:
        score += 1
    if len(pull_request["reviews"]) >= 2:
        score += 1
    return score >= 2


def representative_pr_score(pull_request: PullRequestRecord) -> tuple[int, int, int]:
    return (
        pull_request["changed_files_count"],
        len(pull_request["top_level_areas"]),
        len(pull_request["reviews"]),
    )


def why_pr_matters(pull_request: PullRequestRecord) -> str:
    area_count = len(pull_request["top_level_areas"])
    review_count = len(pull_request["reviews"])
    changed_files = pull_request["changed_files_count"]
    if area_count >= 2:
        return f"Touched {area_count} top-level areas, which makes it a strong example of cross-system delivery."
    if review_count >= 2:
        return f"Drew {review_count} reviews, showing it was substantive enough to need broader engineering input."
    return f"Changed {changed_files} files, making it one of this engineer's larger merged contributions in the window."


def build_headline(stats: dict[str, Any]) -> str:
    parts: list[str] = []
    if stats["meaningfulPrs"] >= stats["mergedPrs"] * 0.5:
        parts.append("Consistently lands substantial PRs")
    if stats["reviewsGiven"] >= 10:
        parts.append("supports teammates heavily in review")
    if stats["uniqueAreasTouched"] >= 3:
        parts.append("works across multiple product areas")
    if not parts:
        parts.append("Ships steadily and contributes meaningful merged work")
    return "; ".join(parts) + "."


def build_why_ranked(stats: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if stats["meaningfulPrs"]:
        reasons.append(
            f"Delivered {stats['meaningfulPrs']} meaningful merged PRs, which is the highest-weighted part of the score."
        )
    if stats["reviewsGiven"]:
        reasons.append(
            f"Provided {stats['reviewsGiven']} high-signal reviews, indicating visible support for other engineers' work."
        )
    if stats["uniqueAreasTouched"]:
        reasons.append(
            f"Touched {stats['uniqueAreasTouched']} distinct top-level areas, suggesting broad context across the codebase."
        )
    return reasons[:3]


def build_dashboard(raw_data: RawPullRequestData) -> dict[str, Any]:
    pull_requests = raw_data["pullRequests"]
    by_engineer: dict[str, dict[str, Any]] = {}
    reviews_by_engineer: dict[str, int] = defaultdict(int)
    authors_reviewed_by_engineer: dict[str, set[str]] = defaultdict(set)

    for pull_request in pull_requests:
        author_login = pull_request["author_login"]
        engineer = by_engineer.setdefault(
            author_login,
            {
                "login": author_login,
                "displayName": author_login,
                "avatarUrl": pull_request["author_avatar"],
                "pullRequests": [],
                "areas": set(),
                "mergeHours": [],
            },
        )
        engineer["pullRequests"].append(pull_request)
        engineer["areas"].update(pull_request["top_level_areas"])

        merge_hours = hours_between(
            pull_request["created_at"], pull_request["merged_at"]
        )
        if merge_hours is not None:
            engineer["mergeHours"].append(merge_hours)

        for review in pull_request["reviews"]:
            reviewer_login = review["reviewer_login"]
            if reviewer_login == author_login:
                continue
            if review["review_state"] not in REVIEW_STATES:
                continue
            reviews_by_engineer[reviewer_login] += 1
            authors_reviewed_by_engineer[reviewer_login].add(author_login)

    assert by_engineer, "No merged pull requests found to score."

    engineer_stats: dict[str, dict[str, Any]] = {}
    for login, engineer in by_engineer.items():
        authored_prs: list[PullRequestRecord] = engineer["pullRequests"]
        meaningful_prs = [
            pull_request
            for pull_request in authored_prs
            if is_meaningful_pr(pull_request)
        ]
        stats = {
            "mergedPrs": len(authored_prs),
            "meaningfulPrs": len(meaningful_prs),
            "reviewsGiven": reviews_by_engineer.get(login, 0),
            "uniqueAreasTouched": len(engineer["areas"]),
            "uniqueAuthorsReviewed": len(
                authors_reviewed_by_engineer.get(login, set())
            ),
            "medianTimeToMergeHours": median_or_none(engineer["mergeHours"]),
        }
        engineer_stats[login] = {
            "login": login,
            "displayName": engineer["displayName"],
            "avatarUrl": engineer["avatarUrl"],
            "stats": stats,
            "pullRequests": authored_prs,
        }

    merged_scores = min_max_scores(
        {
            login: values["stats"]["mergedPrs"]
            for login, values in engineer_stats.items()
        }
    )
    meaningful_scores = min_max_scores(
        {
            login: values["stats"]["meaningfulPrs"]
            for login, values in engineer_stats.items()
        }
    )
    review_scores = min_max_scores(
        {
            login: values["stats"]["reviewsGiven"]
            for login, values in engineer_stats.items()
        }
    )

    ranked: list[dict[str, Any]] = []
    for login, values in engineer_stats.items():
        total_score = (
            merged_scores[login] * WEIGHTS["mergedPrs"]
            + meaningful_scores[login] * WEIGHTS["meaningfulPrs"]
            + review_scores[login] * WEIGHTS["reviewsGiven"]
        )
        stats = values["stats"]
        ranked.append(
            {
                "login": login,
                "displayName": values["displayName"],
                "avatarUrl": values["avatarUrl"],
                "impactScore": round_score(total_score),
                "headline": build_headline(stats),
                "stats": stats,
                "scoreBreakdown": {
                    "mergedPrsScore": round_score(merged_scores[login]),
                    "meaningfulPrsScore": round_score(meaningful_scores[login]),
                    "reviewsGivenScore": round_score(review_scores[login]),
                },
                "pullRequests": values["pullRequests"],
            }
        )

    ranked.sort(
        key=lambda engineer: (
            engineer["impactScore"],
            engineer["stats"]["meaningfulPrs"],
            engineer["stats"]["mergedPrs"],
        ),
        reverse=True,
    )

    top_five = ranked[:5]
    top_engineers: list[dict[str, Any]] = []
    engineer_details: dict[str, dict[str, Any]] = {}

    for rank, engineer in enumerate(top_five, start=1):
        engineer["rank"] = rank
        top_engineers.append(
            {
                "login": engineer["login"],
                "displayName": engineer["displayName"],
                "avatarUrl": engineer["avatarUrl"],
                "rank": rank,
                "impactScore": engineer["impactScore"],
                "headline": engineer["headline"],
                "stats": engineer["stats"],
            }
        )

        representative_prs = sorted(
            engineer["pullRequests"],
            key=representative_pr_score,
            reverse=True,
        )[:3]

        engineer_details[engineer["login"]] = {
            "login": engineer["login"],
            "displayName": engineer["displayName"],
            "avatarUrl": engineer["avatarUrl"],
            "rank": rank,
            "impactScore": engineer["impactScore"],
            "headline": engineer["headline"],
            "whyThisPersonRanksHighly": build_why_ranked(engineer["stats"]),
            "scoreBreakdown": engineer["scoreBreakdown"],
            "stats": engineer["stats"],
            "representativePrs": [
                {
                    "number": pull_request["number"],
                    "title": pull_request["title"],
                    "url": pull_request["url"],
                    "mergedAt": pull_request["merged_at"],
                    "changedFiles": pull_request["changed_files_count"],
                    "areas": pull_request["top_level_areas"],
                    "reviewCount": len(pull_request["reviews"]),
                    "isMeaningful": is_meaningful_pr(pull_request),
                    "whyItMatters": why_pr_matters(pull_request),
                }
                for pull_request in representative_prs
            ],
        }

    merge_hours = [
        hours_between(pull_request["created_at"], pull_request["merged_at"])
        for pull_request in pull_requests
    ]
    overall_merge_hours = [value for value in merge_hours if value is not None]
    summary = raw_data["summary"]
    merged_pr_rate = (
        round(summary["mergedPrs"] / summary["closedPrs"], 4)
        if summary["closedPrs"]
        else 0.0
    )

    return {
        "summary": {
            "repo": summary["repo"],
            "windowDays": summary["windowDays"],
            "generatedAt": summary["generatedAt"],
            "prsAnalyzed": len(pull_requests),
            "engineersAnalyzed": len(engineer_stats),
            "mergedPrRate": merged_pr_rate,
            "medianTimeToMergeHours": median_or_none(overall_merge_hours),
            "impactDefinition": IMPACT_DEFINITION,
        },
        "topEngineers": top_engineers,
        "engineerDetails": engineer_details,
        "methodology": {
            "definition": IMPACT_DEFINITION,
            "weights": WEIGHTS,
            "meaningfulPrDefinition": MEANINGFUL_PR_DEFINITION,
            "notes": [
                "Scores use min-max normalization across engineers for merged PRs, meaningful merged PRs, and reviews given.",
                "Raw stats are shown directly for explainability and are not normalized in the UI.",
                "Merge rate is based on pull requests closed in the last 90 days, with merged pull requests as the numerator.",
                "Review counts include APPROVED and CHANGES_REQUESTED states and exclude self-reviews.",
            ],
        },
    }
