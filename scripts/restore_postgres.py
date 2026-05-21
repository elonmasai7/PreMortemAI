#!/usr/bin/env python3
import shlex
import subprocess
import sys

from app.config import get_settings


def main() -> None:
    settings = get_settings()
    if not settings.database_url.startswith("postgresql"):
        raise RuntimeError("Restore script only supports PostgreSQL DATABASE_URL.")
    if len(sys.argv) != 2:
        raise RuntimeError("Usage: python scripts/restore_postgres.py <backup_file.sqlc>")
    backup_file = sys.argv[1]
    command = f'pg_restore --clean --if-exists --dbname="{settings.database_url}" {shlex.quote(backup_file)}'
    subprocess.run(command, shell=True, check=True)
    print(f"Restore completed from {backup_file}")


if __name__ == "__main__":
    main()
