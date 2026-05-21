# Troubleshooting

## Splunk authentication failed
- Verify `SPLUNK_TOKEN` or `SPLUNK_USERNAME`/`SPLUNK_PASSWORD`.
- Re-check `/setup` for auth method status.

## SSL failure
- For local dev only, set `SPLUNK_VERIFY_SSL=false`.
- For production, install trusted certs and keep SSL verification enabled.

## No indexes found
- Validate account permissions in Splunk.
- Run `GET /api/splunk/indexes` to confirm visibility.

## Empty search results
- Confirm `SPLUNK_DEFAULT_INDEX` and service field naming.
- Adjust time range or SPL template constraints.

## AI provider error
- Check `AI_PROVIDER`, `AI_BASE_URL`, `AI_MODEL`, and `AI_API_KEY`.
- Set `AI_PROVIDER=disabled` to continue without model dependency.

## Database error
- Ensure process can write the SQLite path.
- Remove corrupted local db file and restart.

## Port already in use
- Change `APP_PORT` in environment or stop conflicting process.
