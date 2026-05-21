# Security

## Threat Model
- Unauthorized access to Splunk credentials.
- Malicious or oversized query input.
- Unsafe automatic remediation execution.
- Sensitive incident telemetry leakage.

## Controls Implemented
- Environment-based secret configuration.
- `.gitignore` excludes `.env`, db files, logs, and local artifacts.
- Structured exception handling avoids secret leakage.
- SPL input length validation and basic disallowed operator checks.
- Request body size limit middleware.
- Human decision audit trail for remediation actions.
- Templates rely on Jinja2 autoescaping.

## Splunk Credential Handling
- Token auth preferred.
- Username/password supported if token is absent.
- Credentials are never persisted in database.

## AI Data Handling
- AI mode can be disabled.
- Operators should evaluate data-sharing policies before enabling hosted providers.
- Local model endpoint supported for tighter data control.

## Known Limitations
- Query safety filters are baseline and not a full SPL policy engine.
- No built-in authN/authZ layer (expected to be provided by deployment boundary for hackathon scope).

## Responsible Disclosure
Please report issues privately to project maintainers before public disclosure.
