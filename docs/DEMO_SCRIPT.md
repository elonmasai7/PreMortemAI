# 3-Minute Demo Script

## Demo Goal
Show judges that PreMortem AI is an evidence-first, operator-safe incident prevention tool using real Splunk data and human-governed action decisions.

## 0:00 - 0:25 | Context and Pain
What to click:
- Open `/`

What to say:
- "Most operations teams are reactive. Alerts arrive after impact starts."
- "PreMortem AI predicts likely incidents from Splunk telemetry before outage conditions escalate."

## 0:25 - 0:55 | Trust and Setup Transparency
What to click:
- Open `/setup`

What to say:
- "This page proves configuration truth: Splunk status, auth method, AI mode, MCP status, and DB readiness."
- "If anything is missing, we show setup-required state explicitly. No fake success states, no mock fallback."

## 0:55 - 1:25 | Live Splunk Search Workbench
What to click:
- Open `/splunk/search`
- Run a live SPL query for a real service
- Optionally save template name

What to say:
- "Engineers can inspect raw telemetry directly and save useful SPL templates for investigations."
- "Everything here is real Splunk API execution."

## 1:25 - 2:15 | Investigation Workflow
What to click:
- Open `/investigations`
- Create a new investigation
- Open `/investigations/{id}`
- Click Run Investigation

What to say:
- "Coordinator agent orchestrates telemetry, forecast, root-cause ranking, blast-radius estimation, remediation planning, and report generation."
- "You can see evidence timeline, SPL queries executed, confidence-ranked causes, and operator-ready context."

## 2:15 - 2:40 | Human-Governed Remediation
What to click:
- Open `/remediation/{id}`
- Approve or reject with note

What to say:
- "The system never auto-executes destructive actions."
- "Every decision is human-approved and audit-logged for accountability."

## 2:40 - 3:00 | Report and Operational Value
What to click:
- Open `/reports`
- Open markdown report output

What to say:
- "Each incident ends with a reusable report: summary, timeline, root cause, impact, decision history, and follow-up detection guidance."
- "PreMortem AI helps teams move from reactive firefighting to proactive reliability."

## Optional Backup Talking Points
- AI can run in hosted, local, or disabled mode.
- Disabled mode still provides deterministic analysis.
- System is Python-only, no Node.js/frontend framework dependency.
