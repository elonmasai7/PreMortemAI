#!/usr/bin/env python3
from app.config import get_settings
from app.services.splunk_client import SplunkClient


def main() -> None:
    settings = get_settings()
    client = SplunkClient(settings)
    result = client.test_connection()
    print(result)


if __name__ == "__main__":
    main()
