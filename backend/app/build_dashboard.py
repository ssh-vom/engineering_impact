from __future__ import annotations

import json

from app.config import BACKEND_ROOT
from app.scoring import build_dashboard


def main() -> None:
    input_path = BACKEND_ROOT / "data" / "pull_requests.json"
    output_path = BACKEND_ROOT / "data" / "dashboard.json"

    raw_data = json.loads(input_path.read_text(encoding="utf-8"))
    dashboard = build_dashboard(raw_data)

    output_path.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")
    print(f"wrote dashboard to {output_path}")


if __name__ == "__main__":
    main()
