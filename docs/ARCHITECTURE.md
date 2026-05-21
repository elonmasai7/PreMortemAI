# Architecture

## Overview
PreMortem AI is a server-rendered FastAPI application with an internal Python agent workflow that consumes live Splunk telemetry, stores investigation state in SQLite, and generates human-approved remediation records and post-incident reports.

## Components
- FastAPI app: route handlers for UI and JSON APIs.
- Service layer: Splunk client, AI client abstraction, validation, forecasting, root cause, remediation, report generation.
- Agent layer: Coordinator + six specialist agents (telemetry, forecast, root cause, blast radius, remediation, report).
- Persistence: SQLite via SQLAlchemy for investigations, evidence, recommendations, decisions, and reports.
- Templates/static: Jinja2 + plain CSS + minimal vanilla JS.

## Data Flow
1. Operator creates an investigation.
2. Coordinator Agent triggers Telemetry Agent to execute SPL templates against configured Splunk indexes.
3. Forecast, root cause, and blast radius agents process returned evidence.
4. Remediation Agent creates a recommendation that always requires human approval.
5. Human decision is audited.
6. Report Agent generates a markdown report.

## Splunk Integration
- Uses Splunk REST endpoints and search jobs API.
- Auth supports token or username/password (token preferred).
- Query validation enforces max length and disallows high-risk operators.
- No runtime dummy data fallback.

## AI Integration
- `AIProvider` interface with implementations:
  - `OpenAICompatibleProvider`
  - `LocalModelProvider`
  - `DisabledAIProvider`
- Disabled mode preserves workflow using deterministic summaries.

## Database Use
- SQLite stores application state only.
- Splunk remains source of truth for telemetry.
- Schema includes full auditability for remediation decisions.
