#!/usr/bin/env python3
import json
from pathlib import Path

from app.main import app


def main() -> None:
    schema = app.openapi()
    output_path = Path("docs/openapi.json")
    output_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    print(f"Exported OpenAPI schema to {output_path}")


if __name__ == "__main__":
    main()
