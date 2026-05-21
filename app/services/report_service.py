from app.models import Investigation


def generate_markdown_report(
    investigation: Investigation,
    root_cause_summary: str,
    blast_radius_summary: str,
    decision_history: list[str],
) -> str:
    decisions = "\n".join(f"- {line}" for line in decision_history) or "- No decisions recorded"
    return f"""# {investigation.title}

## Incident Summary
- Investigation ID: {investigation.id}
- Service: {investigation.service_name}
- Risk Score: {investigation.risk_score}
- Risk Level: {investigation.risk_level}

## Timeline
- Created: {investigation.created_at}
- Last Updated: {investigation.updated_at}

## Root Cause
{root_cause_summary or 'No root cause summary available.'}

## Impact
{blast_radius_summary or 'No blast radius summary available.'}

## Decision History
{decisions}

## Follow-up Tasks
- Tune SPL query thresholds for early warning.
- Add service-level runbook links to remediation records.

## Suggested Splunk Alert Rule
Create alert on sustained error_count increase over 3 consecutive 5m intervals.

## Suggested Dashboard Panel
Service error_count and p95 latency trend by service over last 60 minutes.
"""
