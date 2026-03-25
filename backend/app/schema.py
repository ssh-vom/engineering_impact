from __future__ import annotations

from typing import NotRequired, TypedDict


class ReviewRecord(TypedDict):
    reviewer_login: str
    review_state: str
    submitted_at: str


class PullRequestRecord(TypedDict):
    number: int
    title: str
    url: str
    author_login: str
    author_avatar: str
    created_at: str
    merged_at: str
    merged: bool
    changed_files_count: int
    top_level_areas: list[str]
    reviews: list[ReviewRecord]


class RawPullRequestSummary(TypedDict):
    repo: str
    windowDays: int
    generatedAt: str
    closedPrs: int
    mergedPrs: int
    graphqlPagesFetched: int
    restFileRequests: int
    phase: NotRequired[str]
    topCandidateLogins: NotRequired[list[str]]
    areaEnrichmentComplete: NotRequired[bool]


class RawPullRequestData(TypedDict):
    summary: RawPullRequestSummary
    pullRequests: list[PullRequestRecord]
