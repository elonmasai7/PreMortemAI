# Internal Agents

PreMortem AI uses plain Python classes (no external agent framework required).

## Coordinator Agent
- Orchestrates full investigation workflow.
- Persists outputs to database.

## Telemetry Agent
- Executes SPL templates against Splunk.
- Returns normalized evidence rows.

## Forecast Agent
- Computes transparent risk forecast from telemetry trends.
- Labels method used.

## Root Cause Agent
- Correlates evidence and ranks likely causes with confidence.

## Blast Radius Agent
- Estimates affected services and transaction scope.
- Never invents revenue impact.

## Remediation Agent
- Produces safe recommendation plan.
- Requires human approval.

## Report Agent
- Generates final markdown report for incident record.

## Evidence Grounding
- AI outputs include evidence references and assumptions.
- Disabled AI mode still produces deterministic summaries.
