# API Reference

All responses are JSON unless otherwise noted.

## Health
- `GET /api/health`: full component status.
- `GET /api/health/readiness`: readiness boolean + components.
- `GET /api/health/liveness`: `{ "alive": true }`.

## Splunk
- `GET /api/splunk/status`: connection/setup state.
- `POST /api/splunk/search`
  - body: `{ "query": "search ...", "max_count": 100 }`
  - response: `{ "job_id": "...", "status": "done", "rows": [...] }`
- `GET /api/splunk/indexes`: list index names.
- `GET /api/splunk/saved-searches`: list saved searches.
- `POST /api/splunk/validate-query`
  - body: `{ "query": "search ..." }`

## Investigations
- `GET /api/investigations`: list investigations.
- `POST /api/investigations`
  - body: `{ "title": "...", "service_name": "..." }`
- `GET /api/investigations/{investigation_id}`
- `POST /api/investigations/{investigation_id}/run`
- `POST /api/investigations/{investigation_id}/refresh`
- `DELETE /api/investigations/{investigation_id}`

## AI
- `POST /api/ai/summarize`
- `POST /api/ai/root-cause`
- `POST /api/ai/remediation-plan`
- `POST /api/ai/postmortem`

Evidence body format:
```json
{ "evidence": [{"key":"value"}] }
```

## Remediation
- `GET /api/remediation/{investigation_id}`
- `POST /api/remediation/{investigation_id}/approve`
  - body: `{ "note": "reason" }`
- `POST /api/remediation/{investigation_id}/reject`
  - body: `{ "note": "reason" }`

## Reports
- `GET /api/reports`
- `POST /api/reports/{investigation_id}/generate`
- `GET /api/reports/{report_id}`
- `GET /api/reports/{report_id}/markdown` (text/markdown)

## Error Pattern
Application errors return:
```json
{
  "detail": "Human-readable message",
  "next_step": "Guidance"
}
```
