# Security

## Security Posture Summary
PreMortem AI is designed to minimize operational risk while handling sensitive telemetry and incident analysis workflows. It enforces explicit configuration, avoids hidden fallback behavior, and records critical human decisions.

## Threat Model

### Assets
- Splunk API credentials (token or username/password)
- Operational telemetry and incident evidence
- Remediation decision history
- Generated post-incident reports

### Primary Threats
- Credential leakage via source control/logging/error responses
- Query abuse through unsafe SPL patterns
- Excessive payload attacks against API endpoints
- Unapproved destructive remediation execution
- Data leakage to external AI providers without operator awareness

## Security Controls Implemented

### Secrets Handling
- Secrets are environment-driven (`.env` for local only).
- `.gitignore` excludes `.env`, DB files, and log artifacts.
- Credentials are not written to SQLite application tables.

### Input Validation and Request Guardrails
- Pydantic schema validation on request models.
- SPL query max-length enforcement (`max_spl_query_length`).
- Baseline disallow list for risky SPL operators.
- Request body size limit middleware (413 for oversized payloads).

### Authentication and Authorization
- Bearer token auth support with signed access tokens.
- API key auth support for service-to-service usage.
- Role-based access control (`viewer`, `analyst`, `admin`, `owner`).
- Tenant-scoped authorization checks on investigation, remediation, and reports APIs.

### Multi-Tenant Boundary Controls
- Tenant-aware schema columns (`tenant_id`) on operational state tables.
- API routes filter by tenant scope and reject cross-tenant lookups.
- Tenant-specific app settings and API keys.

### Error Handling and Data Exposure Controls
- Controlled exception handlers provide actionable messages.
- No stack trace/secret dump behavior in API response payloads.
- Setup and health routes report missing config explicitly instead of failing silently.

### Remediation Safety
- No endpoint executes destructive infra actions.
- Remediation remains recommendation-only for hackathon scope.
- Approve/reject actions are recorded in `HumanDecision` audit records.

### Queue and Rate Limit Controls
- Redis-backed rate limiting for expensive endpoints when Redis is configured.
- Queue-backed investigation execution support to isolate long-running analysis from request path.

### Template and UI Safety
- Jinja2 autoescaping protects against HTML injection in rendered views.
- No arbitrary shell execution paths in route handlers.

## Splunk Credential Handling
- Auth precedence: token first, then username/password fallback.
- Splunk creds are only used for outbound API requests.
- Never log raw secrets.

## AI Provider Data Handling
- `AI_PROVIDER=disabled` offers no-model mode for strict environments.
- `AI_PROVIDER=local` supports internal model endpoints.
- `AI_PROVIDER=openai_compatible` requires explicit endpoint and key configuration.
- Operators are responsible for confirming data residency/compliance for hosted providers.

## Operational Security Recommendations
- Run behind reverse proxy with TLS termination.
- Restrict network egress to approved Splunk/AI endpoints.
- Use dedicated least-privilege Splunk service account/token.
- Rotate tokens regularly.
- Restrict file permissions for local SQLite file.
- Enforce `AUTH_REQUIRED=true` outside local development.

## Security Automation
- CI security workflow includes dependency audit (`pip-audit`).
- Secrets scanning via GitHub Actions (`gitleaks`).

## Known Limitations
- SPL validation is policy-baseline, not full SPL sandboxing.
- No built-in user authentication/authorization layer in current hackathon scope.
- SQLite is suitable for local/small-scale use; production should migrate to hardened managed DB.

## Responsible Disclosure
If you identify a vulnerability, report it privately to maintainers with:
- affected version/commit
- reproduction steps
- impact assessment
- suggested remediation

Please avoid public disclosure until maintainers acknowledge and patch.
