from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterator

import httpx
from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_BACKEND_ROOT / ".env")
load_dotenv()


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None, timeout: float = 30.0) -> None:
        self._token = token if token is not None else os.environ.get("GITHUB_TOKEN")
        headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> GitHubClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> httpx.Response:
        response = self._client.request(method, path, params=params, json=json)
        response.raise_for_status()
        return response

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params).json()

    def get_viewer(self) -> dict[str, Any]:
        return self.get_json("/user")

    def get_rate_limit(self) -> dict[str, Any]:
        return self.get_json("/rate_limit")

    def iter_pull_requests(
        self, owner: str, repo: str, state: str = "closed"
    ) -> Iterator[dict[str, Any]]:
        path = f"/repos/{owner}/{repo}/pulls"
        for item in self.iter_pages(
            path, params={"state": state, "sort": "updated", "direction": "desc"}
        ):
            yield item

    def iter_merged_pull_requests_since(
        self, owner: str, repo: str, merged_since: str
    ) -> Iterator[dict[str, Any]]:
        path = "/search/issues"
        start = date.fromisoformat(merged_since)
        end = date.today()
        window = timedelta(days=30)

        def iter_range(range_start: date, range_end: date) -> Iterator[dict[str, Any]]:
            query = (
                f"repo:{owner}/{repo} is:pr is:merged "
                f"merged:{range_start.isoformat()}..{range_end.isoformat()}"
            )
            payload = self.get_json(
                path,
                params={
                    "q": query,
                    "sort": "updated",
                    "order": "desc",
                    "page": 1,
                    "per_page": 100,
                },
            )
            total_count = payload["total_count"]
            if total_count > 1000:
                assert range_start < range_end, (
                    "search range still exceeds 1000 results"
                )
                midpoint = range_start + (range_end - range_start) // 2
                yield from iter_range(midpoint + timedelta(days=1), range_end)
                yield from iter_range(range_start, midpoint)
                return

            items = payload["items"]
            for item in items:
                yield item
            if len(items) < 100:
                return

            page = 2
            while True:
                payload = self.get_json(
                    path,
                    params={
                        "q": query,
                        "sort": "updated",
                        "order": "desc",
                        "page": page,
                        "per_page": 100,
                    },
                )
                items = payload["items"]
                if not items:
                    break
                for item in items:
                    yield item
                if len(items) < 100:
                    break
                page += 1

        current_end = end
        while current_end >= start:
            current_start = max(start, current_end - window + timedelta(days=1))
            yield from iter_range(current_start, current_end)
            current_end = current_start - timedelta(days=1)

    def get_pull_request(self, owner: str, repo: str, number: int) -> dict[str, Any]:
        path = f"/repos/{owner}/{repo}/pulls/{number}"
        return self.get_json(path)

    def get_pull_request_files(
        self, owner: str, repo: str, number: int
    ) -> list[dict[str, Any]]:
        path = f"/repos/{owner}/{repo}/pulls/{number}/files"
        return list(self.iter_pages(path))

    def get_pull_request_reviews(
        self, owner: str, repo: str, number: int
    ) -> list[dict[str, Any]]:
        path = f"/repos/{owner}/{repo}/pulls/{number}/reviews"
        return list(self.iter_pages(path))

    def iter_pages(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        per_page: int = 100,
    ) -> Iterator[Any]:
        base: dict[str, Any] = dict(params or {})
        page = 1
        while True:
            chunk = self.get_json(
                path,
                params={**base, "page": page, "per_page": per_page},
            )
            if not chunk:
                break
            if isinstance(chunk, list):
                for item in chunk:
                    yield item
                if len(chunk) < per_page:
                    break
            else:
                yield chunk
                break
            page += 1
