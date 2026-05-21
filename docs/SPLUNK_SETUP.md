# Splunk Setup

## Supported Targets
- Splunk Enterprise (local/dev)
- Splunk Cloud (with management endpoint access)

## Required Configuration
Set environment variables (see `.env.example`):
- `SPLUNK_BASE_URL` (example: `https://localhost:8089`)
- Either `SPLUNK_TOKEN` or `SPLUNK_USERNAME` + `SPLUNK_PASSWORD`
- `SPLUNK_DEFAULT_INDEX`
- `SPLUNK_VERIFY_SSL` and timeout values

Token auth is preferred when both auth methods are present.

## Index Requirements
Application queries run against configured indexes. Ensure data exists for services under investigation (logs/metrics/deploy events).

## Validate Connection
Run:
```bash
make validate-splunk
```

Or open `/setup` and verify Splunk status.

## Query Templates
SPL templates are in `app/services/splunk_search_service.py` and are editable.
