# Troubleshooting

## Quick Diagnostic Sequence
1. Run `make check-env`.
2. Open `/setup` and inspect missing/failed statuses.
3. Check `GET /api/health` and `GET /api/splunk/status`.
4. Validate Splunk with `make validate-splunk`.

## Splunk Authentication Failed

Symptoms:
- `/setup` shows Splunk error
- `/api/splunk/status` returns auth failure

Checks:
- Ensure either:
  - `SPLUNK_TOKEN` is valid, or
  - both `SPLUNK_USERNAME` and `SPLUNK_PASSWORD` are valid
- Confirm `SPLUNK_BASE_URL` points to management API endpoint

Fix:
- Update credentials and restart app
- Prefer token auth for service accounts

## SSL Verification Failure

Symptoms:
- TLS/certificate errors when contacting Splunk

Checks:
- Is Splunk using self-signed cert in local lab?

Fix:
- Local only: set `SPLUNK_VERIFY_SSL=false`
- Production: keep SSL verification enabled and install trusted certificate chain

## No Indexes Found

Symptoms:
- `GET /api/splunk/indexes` returns empty

Checks:
- Splunk role permissions for target account
- Whether expected indexes actually exist

Fix:
- Grant read permissions to required indexes
- Set `SPLUNK_DEFAULT_INDEX` to a valid visible index

## Empty Search Results

Symptoms:
- Searches execute successfully but return zero rows

Checks:
- Verify index and field names in SPL
- Validate service name casing/format
- Confirm telemetry exists in selected time range

Fix:
- Adjust SPL filters/templates
- Start with broad query in `/splunk/search`, then tighten filters

## AI Provider Error

Symptoms:
- `/api/ai/*` routes return provider failure

Checks:
- `AI_PROVIDER` value (`disabled`, `local`, `openai_compatible`)
- `AI_BASE_URL`, `AI_MODEL`, and `AI_API_KEY` (if required)

Fix:
- Correct provider configuration
- Use `AI_PROVIDER=disabled` to keep investigation workflow operational without model dependency

## Database Error

Symptoms:
- startup failure or write error during investigation/report operations

Checks:
- `DATABASE_URL` correctness
- file write permissions on SQLite path

Fix:
- ensure process can create/write DB file
- if local DB is corrupted, back it up and recreate

## Port Already in Use

Symptoms:
- `make run` fails with bind error

Fix:
- change `APP_PORT` in `.env`
- stop process using current port

## API Returns 413 (Payload Too Large)

Symptoms:
- request rejected with `Request body too large`

Fix:
- reduce request size
- if required, increase `max_request_body_bytes` in app settings code with caution

## Investigation Run Fails

Symptoms:
- investigation status changes to `failed`

Checks:
- Splunk connectivity
- query validation constraints
- search timeout (`SPLUNK_TIMEOUT_SECONDS`)

Fix:
- run test query directly in `/splunk/search`
- increase timeout for slower environments
- inspect logs for route-level exception details
