from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_BACKEND_ROOT / ".env")
load_dotenv()

PULL_REQUESTS_QUERY = """
query PullRequests(
  $owner: String!
  $repo: String!
  $states: [PullRequestState!]
  $after: String
  $pageSize: Int!
) {
  repository(owner: $owner, name: $repo) {
    pullRequests(
      first: $pageSize
      after: $after
      states: $states
      orderBy: {field: UPDATED_AT, direction: DESC}
    ) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        number
        title
        url
        createdAt
        closedAt
        mergedAt
        updatedAt
        additions
        deletions
        changedFiles
        author {
          login
          avatarUrl
        }
        mergedBy {
          login
        }
        reviews(first: 100) {
          nodes {
            author {
              login
            }
            state
            submittedAt
          }
        }
      }
    }
  }
  rateLimit {
    cost
    remaining
    resetAt
  }
}
"""

CLOSED_PULL_REQUESTS_QUERY = """
query ClosedPullRequests(
  $owner: String!
  $repo: String!
  $states: [PullRequestState!]
  $after: String
  $pageSize: Int!
) {
  repository(owner: $owner, name: $repo) {
    pullRequests(
      first: $pageSize
      after: $after
      states: $states
      orderBy: {field: UPDATED_AT, direction: DESC}
    ) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        closedAt
        mergedAt
        updatedAt
      }
    }
  }
  rateLimit {
    cost
    remaining
    resetAt
  }
}
"""


class GitHubClient:
    base_url = "https://api.github.com"

    def __init__(self, token: str | None = None, timeout: float = 30.0) -> None:
        self.token = token if token is not None else os.environ.get("GITHUB_TOKEN", "")
        headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        self.client = httpx.Client(
            base_url=self.base_url, headers=headers, timeout=timeout
        )

    def close(self) -> None:
        self.client.close()

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
        response = self.client.request(method, path, params=params, json=json)
        response.raise_for_status()
        return response

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params).json()

    def graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        payload = {"query": query, "variables": variables}
        data = self.request("POST", "/graphql", json=payload).json()
        assert "errors" not in data, data["errors"]
        return data

    def get_viewer(self) -> dict[str, Any]:
        return self.get_json("/user")

    def get_rate_limit(self) -> dict[str, Any]:
        return self.get_json("/rate_limit")

    def get_pull_request_page(
        self,
        owner: str,
        repo: str,
        states: list[str],
        after: str | None,
        *,
        page_size: int = 25,
    ) -> dict[str, Any]:
        data = self.graphql(
            PULL_REQUESTS_QUERY,
            {
                "owner": owner,
                "repo": repo,
                "states": states,
                "after": after,
                "pageSize": page_size,
            },
        )
        repository = data["data"]["repository"]
        assert repository is not None, f"repository not found: {owner}/{repo}"
        return {
            "pullRequests": repository["pullRequests"],
            "rateLimit": data["data"]["rateLimit"],
        }

    def get_closed_pull_request_page(
        self,
        owner: str,
        repo: str,
        after: str | None,
        *,
        page_size: int = 50,
    ) -> dict[str, Any]:
        data = self.graphql(
            CLOSED_PULL_REQUESTS_QUERY,
            {
                "owner": owner,
                "repo": repo,
                "states": ["CLOSED", "MERGED"],
                "after": after,
                "pageSize": page_size,
            },
        )
        repository = data["data"]["repository"]
        assert repository is not None, f"repository not found: {owner}/{repo}"
        return {
            "pullRequests": repository["pullRequests"],
            "rateLimit": data["data"]["rateLimit"],
        }

    def get_pull_request_files(
        self, owner: str, repo: str, number: int
    ) -> list[dict[str, Any]]:
        path = f"/repos/{owner}/{repo}/pulls/{number}/files"
        page = 1
        files: list[dict[str, Any]] = []
        while True:
            chunk = self.get_json(path, params={"page": page, "per_page": 100})
            assert isinstance(chunk, list)
            if not chunk:
                return files
            files.extend(chunk)
            if len(chunk) < 100:
                return files
            page += 1
