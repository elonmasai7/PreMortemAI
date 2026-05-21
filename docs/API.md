# API Reference

All API routes are JSON unless explicitly marked otherwise.

## Base Conventions
- Content-Type for request bodies: `application/json`
- Validation failures: HTTP `422`
- Controlled business/integration failures: HTTP `400`
- Not found resources: HTTP `404`

## Error Response Shape
```json
{
  "detail": "Human-readable message",
  "next_step": "Actionable guidance"
}
```

---

## Health APIs

### GET `/api/health`
Returns full status snapshot for app, DB, Splunk, AI provider, MCP, and configuration completeness.

Response example:
```json
{
  "app": { "status": "ok", "detail": "Application running" },
  "database": { "status": "ok", "detail": "SQLite reachable" },
  "splunk": { "status": "ok", "detail": "Splunk API reachable" },
  "ai_provider": { "status": "disabled", "detail": "AI provider disabled by configuration." },
  "mcp": { "status": "disabled", "detail": "MCP integration disabled by configuration." },
  "configuration_complete": true
}
```

### GET `/api/health/readiness`
Readiness summary for orchestration/probe use.

Response example:
```json
{
  "ready": true,
  "components": { "app": { "status": "ok", "detail": "Application running" } }
}
```

### GET `/api/health/liveness`
Basic process liveness check.

Response example:
```json
{ "alive": true }
```

---

## Splunk APIs

### GET `/api/splunk/status`
Returns `setup_required` when mandatory Splunk config is missing, else tests API connectivity.

### POST `/api/splunk/search`
Run live SPL search via Splunk search jobs API.

Request:
```json
{
  "query": "search index=my_index service=checkout error",
  "max_count": 100
}
```

Response:
```json
{
  "job_id": "174...",
  "status": "done",
  "rows": [{ "_time": "...", "service": "checkout", "error_count": "5" }]
}
```

Possible errors:
- `400`: Splunk auth/connection/query failure
- `422`: invalid payload or query length constraints

### GET `/api/splunk/indexes`
List visible Splunk indexes for current credentials.

Response:
```json
{ "indexes": ["main", "platform", "payments"] }
```

### GET `/api/splunk/saved-searches`
List available saved searches.

Response:
```json
{ "saved_searches": ["error_rate_watch", "latency_p95_panel"] }
```

### POST `/api/splunk/validate-query`
Validates SPL through both local policy checks and Splunk parser endpoint.

Request:
```json
{ "query": "search index=main service=api | timechart count" }
```

Response:
```json
{ "valid": true, "details": { "messages": [] } }
```

---

## Investigation APIs

### GET `/api/investigations`
Returns all investigations sorted by creation date (descending).

### POST `/api/investigations`
Create a new investigation.

Request:
```json
{
  "title": "Checkout timeout risk",
  "service_name": "checkout"
}
```

Response (`201`):
```json
{
  "id": 1,
  "title": "Checkout timeout risk",
  "service_name": "checkout",
  "status": "new",
  "risk_score": 0.0,
  "risk_level": "low",
  "forecast_summary": null,
  "root_cause_summary": null,
  "blast_radius_summary": null,
  "created_at": "2026-05-21T08:00:00",
  "updated_at": "2026-05-21T08:00:00"
}
```

### GET `/api/investigations/{investigation_id}`
Fetch one investigation.

### POST `/api/investigations/{investigation_id}/run`
Run full coordinator workflow:
- Collect telemetry
- Forecast risk
- Rank root causes
- Estimate blast radius
- Create remediation recommendation
- Generate initial report

### POST `/api/investigations/{investigation_id}/refresh`
Alias to rerun workflow for existing investigation.

### DELETE `/api/investigations/{investigation_id}`
Deletes the investigation and related child records.

---

## AI APIs

These endpoints route through `AIProvider` abstraction. They work in disabled mode using deterministic fallback logic.

### Shared evidence payload
```json
{
  "evidence": [
    { "_time": "2026-05-21T07:55:00", "service": "checkout", "message": "timeout upstream" }
  ]
}
```

### POST `/api/ai/summarize`
Returns evidence summary + confidence metadata.

### POST `/api/ai/root-cause`
Returns ranked root-cause candidates.

### POST `/api/ai/remediation-plan`
Returns remediation proposal with risk-of-action and risk-of-inaction.

### POST `/api/ai/postmortem`
Request:
```json
{ "investigation": { "id": 1, "service_name": "checkout" } }
```

Response:
```json
{ "markdown": "# Post-Incident Report\n..." }
```

---

## Remediation APIs

### GET `/api/remediation/{investigation_id}`
Returns current recommendation plus decision history.

Response shape:
```json
{
  "recommendation": {
    "id": 7,
    "action_type": "investigate",
    "action_summary": "Review latest failing service logs...",
    "risk_of_action": "Low operational risk...",
    "risk_of_inaction": "Potential outage escalation...",
    "confidence": 0.45,
    "status": "pending"
  },
  "decisions": [
    { "decision": "approve", "note": "Looks safe", "decided_at": "2026-05-21T08:10:00" }
  ]
}
```

### POST `/api/remediation/{investigation_id}/approve`
Request:
```json
{ "note": "Proceed with mitigation plan" }
```

Response:
```json
{ "status": "approved", "recommendation_id": 7 }
```

### POST `/api/remediation/{investigation_id}/reject`
Request:
```json
{ "note": "Insufficient evidence; gather more data" }
```

Response:
```json
{ "status": "rejected", "recommendation_id": 7 }
```

---

## Report APIs

### GET `/api/reports`
Returns report list metadata.

### POST `/api/reports/{investigation_id}/generate`
Generate a new report for the target investigation.

Response:
```json
{ "id": 10, "investigation_id": 1, "title": "Postmortem #1" }
```

### GET `/api/reports/{report_id}`
Fetch full report object including markdown body.

### GET `/api/reports/{report_id}/markdown`
Returns markdown text (`text/plain` response).

---

## Notes for Integrators
- Health APIs should be used to gate automated workflows.
- Investigation run can take longer depending on Splunk response time.
- In disabled AI mode, expect deterministic summaries rather than model-generated prose.
- No endpoint performs destructive infrastructure changes.
