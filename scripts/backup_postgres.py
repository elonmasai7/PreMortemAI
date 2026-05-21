#!/usr/bin/env python3
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from app.config import get_settings


def main() -> None:
    settings = get_settings()
    if not settings.database_url.startswith("postgresql"):
        raise RuntimeError("Backup script only supports PostgreSQL DATABASE_URL.")
    output_dir = Path("backups")
    output_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_file = output_dir / f"premortem_{stamp}.sqlc"
    command = f'pg_dump --format=custom --file={shlex.quote(str(backup_file))} "{settings.database_url}"'
    subprocess.run(command, shell=True, check=True)
    print(f"Backup created: {backup_file}")


if __name__ == "__main__":
    main()
