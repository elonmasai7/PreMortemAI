# Internal Agents

PreMortem AI uses internal, plain-Python agent classes with explicit boundaries and deterministic orchestration. This keeps the system transparent, testable, and independent of external JS/Node agent runtimes.

## Why Agentize This Workflow
- Incident prevention is a multi-step reasoning problem.
- Different concerns require different logic (telemetry retrieval vs forecasting vs action planning).
- Agent separation creates cleaner auditability and easier evolution.

## Agent Topology

### Coordinator Agent (`app/agents/coordinator_agent.py`)
Responsibilities:
- Entry point for investigation run workflow.
- Invokes specialist agents in sequence.
- Persists evidence, summaries, recommendations, and generated reports.
- Updates investigation status (`new` -> `analyzed` or `failed`).

Inputs:
- `Investigation` record
- DB session
- Instantiated specialist agents

Outputs:
- Updated investigation
- Linked evidence/cause/recommendation/report records

### Telemetry Agent (`app/agents/telemetry_agent.py`)
Responsibilities:
- Execute SPL templates for a target service.
- Gather real telemetry rows from Splunk.
- Attach metadata (`__spl_query`, template name) for traceability.

Outputs:
- normalized evidence rows used by downstream analysis agents

### Forecast Agent (`app/agents/forecast_agent.py`)
Responsibilities:
- Produce risk score and risk level from telemetry trends.
- Label method used (`transparent_fallback` currently).

Outputs:
- `risk_score`, `risk_level`, human-readable forecast summary

### Root Cause Agent (`app/agents/root_cause_agent.py`)
Responsibilities:
- Correlate evidence patterns (timeouts, deploy markers, dependencies).
- Rank likely causes with confidence and explanation.

Outputs:
- ordered candidate list for `RootCauseCandidate` persistence

### Blast Radius Agent (`app/agents/blast_radius_agent.py`)
Responsibilities:
- Estimate potentially affected services and transaction scope.
- Include affected user estimate only if telemetry exists.
- Never invent revenue impact values.

Outputs:
- blast radius summary payload

### Remediation Agent (`app/agents/remediation_agent.py`)
Responsibilities:
- Request safe remediation plan from configured AI provider abstraction.
- Ensure recommendation remains human-approval gated.

Outputs:
- recommendation payload with action, risks, confidence, assumptions

### Report Agent (`app/agents/report_agent.py`)
Responsibilities:
- Generate markdown report from investigation state.
- Use AI provider when enabled.
- Use deterministic report builder in disabled mode.

Outputs:
- markdown report body persisted in `Report`

## Agent Execution Sequence
1. Coordinator starts run.
2. Telemetry Agent collects Splunk evidence.
3. Forecast Agent computes risk.
4. Root Cause Agent ranks causes.
5. Blast Radius Agent estimates impact.
6. Remediation Agent drafts action plan.
7. Report Agent generates initial incident report.
8. Coordinator commits all outputs to DB.

## Evidence Grounding Rules
- Agent outputs must map to actual evidence rows.
- AI responses are constrained to evidence context.
- Confidence values are explicit.
- Missing data and assumptions are surfaced.
- Human approval is mandatory for remediation state transitions.

## Failure Handling
- Splunk/API/validation exceptions are surfaced through controlled API errors.
- Investigation can move to `failed` state when run-time analysis errors occur.
- No silent failures and no synthetic fallback incident records.

## Extensibility Guidance
To add a new agent:
1. Define a clear responsibility and data contract.
2. Implement class under `app/agents/`.
3. Wire invocation from Coordinator Agent.
4. Persist output with explicit schema/model support.
5. Add route/tests/docs updates for observable behavior.
