from __future__ import annotations

from app.check_github import main as check_github
from app.fetch_pull_requests import main as fetch_pull_requests


def main() -> None:
    print("checking GitHub access")
    check_github()
    print("starting engineering impact pipeline")
    fetch_pull_requests()
    print("done")


if __name__ == "__main__":
    main()
