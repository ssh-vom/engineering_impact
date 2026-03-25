from __future__ import annotations

import os
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
