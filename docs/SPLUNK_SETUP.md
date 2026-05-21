# Splunk Setup

## Overview
PreMortem AI requires live Splunk telemetry for runtime analysis. It does not use fake incident data when Splunk is unavailable. If configuration is missing or invalid, `/setup` and `/api/health` explicitly report setup-required/error states.

## Supported Splunk Targets
- Splunk Enterprise (local lab or self-managed)
- Splunk Cloud (management endpoint/API access required)

## Required Environment Configuration
Set values in `.env` (from `.env.example`):

- `SPLUNK_BASE_URL`
  - Example: `https://localhost:8089`
  - Must point to Splunk management API endpoint.
- Authentication (one of):
  - `SPLUNK_TOKEN` (preferred)
  - `SPLUNK_USERNAME` and `SPLUNK_PASSWORD`
- `SPLUNK_DEFAULT_INDEX`
  - Default index used by query templates.
- `SPLUNK_VERIFY_SSL`
  - `true` in secure/prod environments.
  - `false` only for local test systems with self-signed certs.
- `SPLUNK_TIMEOUT_SECONDS`
  - Timeout budget for API and search polling.

## Authentication Modes

### Token Auth (Preferred)
Use:
```env
SPLUNK_TOKEN=<token>
```

Advantages:
- Easier secret rotation
- Avoids storing user password in app runtime

### Username/Password Auth
Use:
```env
SPLUNK_USERNAME=<username>
SPLUNK_PASSWORD=<password>
```

If both token and username/password are provided, PreMortem AI uses token auth first.

## Creating a Splunk Token (General Guidance)
1. Open Splunk management UI.
2. Create or identify a service account with index search permissions.
3. Create an auth token for API usage.
4. Store token in `SPLUNK_TOKEN`.

Exact UI steps vary across Splunk Enterprise and Splunk Cloud versions.

## Index and Field Requirements
The platform expects your index(es) to contain operational telemetry fields commonly used in SPL, such as:
- `service`
- `message`
- latency fields (`latency_ms`)
- deployment markers (`deployment`, `release`, `version`)
- dependency markers (`upstream`, `downstream`, `timeout`)

If your field names differ, adjust SPL templates in `app/services/splunk_search_service.py`.

## Connection Validation

### Command line
```bash
make validate-splunk
```

### UI
Open `/setup` and verify:
- Splunk base URL
- Auth method presence
- Connection status/details

### API
Call:
```bash
curl -s http://127.0.0.1:8000/api/splunk/status
```

## How Search Execution Works
1. App submits search to `/services/search/jobs`.
2. App polls job status until done/failed/timeout.
3. App fetches results from `/services/search/jobs/{sid}/results`.
4. Results are normalized and returned to route callers.

## Query Template Management
- Built-in templates are defined in `app/services/splunk_search_service.py`.
- Users can run custom SPL from `/splunk/search`.
- Query templates can be saved from UI and stored in `AppSetting` records.

## Common Setup Failures
- `SPLUNK_BASE_URL` missing or wrong port
- invalid token or account without search/index permissions
- SSL trust failure when `SPLUNK_VERIFY_SSL=true` in local self-signed setups
- default index not set or empty index

See `docs/TROUBLESHOOTING.md` for quick fixes.
