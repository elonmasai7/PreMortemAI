# Architecture

## System Overview
PreMortem AI is a server-rendered, API-first incident prevention platform with clear separation between:
- Web/API presentation
- Service integration (Splunk, AI, validation)
- Internal multi-agent orchestration
- Persistent investigation and audit state

The design goal is operational trust: every recommendation must tie back to evidence, every decision must be auditable, and missing configuration must be explicit.

## High-Level Components

### 1) Application Layer (`app/main.py`)
- Initializes FastAPI app and static/template infrastructure.
- Registers UI routes and JSON API routers.
- Applies request size middleware and centralized exception handling.
- Initializes database schema at startup.

### 2) API + Page Routes (`app/api/`)
- **Health routes**: liveness/readiness/full status.
- **Splunk routes**: query execution, validation, indexes/saved searches.
- **Investigation routes**: CRUD and workflow execution.
- **AI routes**: summarize/root-cause/remediation/postmortem abstractions.
- **Remediation routes**: approval/rejection lifecycle and audit retrieval.
- **Report routes**: generate/list/fetch markdown reports.
- **Dashboard/Setup pages**: operator UX for risk posture and environment state.

### 3) Service Layer (`app/services/`)
- `splunk_client.py`: low-level Splunk REST/search job interactions.
- `splunk_search_service.py`: template rendering + execution wrapper.
- `validation_service.py`: SPL safety checks and query length limits.
- `ai_client.py`: provider interface and implementations.
- `forecast_service.py`, `root_cause_service.py`, `blast_radius_service.py`: deterministic analysis helpers.
- `remediation_service.py`, `report_service.py`: recommendation decision wiring and report assembly.
- `mcp_client.py`: optional MCP connectivity status check.

### 4) Internal Agent Layer (`app/agents/`)
- Plain Python classes with explicit responsibility boundaries.
- Coordinator orchestrates specialist agents and persists outputs.
- No external JS/Node-based agent framework dependency.

### 5) Data Layer (`app/models.py`, `app/database.py`)
- SQLAlchemy models for investigations, evidence, root-cause candidates, remediation recommendations, human decisions, reports, app settings.
- SQLite as local persistence for hackathon scope.
- Splunk remains telemetry source of truth.

### 6) Presentation Layer (`app/templates/`, `app/static/`)
- Jinja2 server-rendered pages.
- Professional, lightweight CSS theme for enterprise operators.
- Minimal vanilla JS for non-critical UX actions.

## Request and Workflow Lifecycle

### Investigation Flow
1. Engineer creates investigation (`POST /api/investigations`).
2. Coordinator Agent runs (`POST /api/investigations/{id}/run`).
3. Telemetry Agent executes SPL templates against configured index.
4. Evidence is persisted in `Evidence` table.
5. Forecast Agent computes risk score and risk level.
6. Root Cause Agent ranks candidate causes with confidence and summaries.
7. Blast Radius Agent estimates affected services/transactions.
8. Remediation Agent produces recommendation requiring human approval.
9. Report Agent builds markdown output and stores `Report`.
10. Human approves/rejects via remediation routes; decision gets audited.

### Health and Setup Flow
- Setup page and health APIs evaluate DB, Splunk, AI, MCP, and configuration completeness.
- Missing credentials/config are reported as setup-required, not masked.

## Splunk Integration Architecture
- Auth strategy:
  - Prefer bearer token (`SPLUNK_TOKEN`) when available.
  - Fallback to username/password if token is absent.
- Search strategy:
  - Create search job (`/services/search/jobs`)
  - Poll status until done/failure/timeout
  - Fetch results (`/services/search/jobs/{sid}/results`)
- Auxiliary endpoints:
  - Index list
  - Saved searches
  - SPL parser validation
- Safety:
  - Query length cap
  - Disallowed risky operators in validation service

## AI Integration Architecture

### Provider Interface
`AIProvider` defines:
- `summarize_evidence`
- `rank_root_causes`
- `create_remediation_plan`
- `generate_postmortem`

### Implementations
- `OpenAICompatibleProvider`: OpenAI-style `/chat/completions` endpoint.
- `LocalModelProvider`: same protocol for self-hosted model endpoints.
- `DisabledAIProvider`: deterministic fallback preserving product usability.

### Grounding Rules
- AI outputs must include evidence references and confidence.
- No invented services, incidents, or impact numbers.
- Human approval remains mandatory for remediation state change.

## Data Model Intent
- **Investigation**: central state for risk and analysis summaries.
- **Evidence**: normalized snippets and query references from Splunk.
- **RootCauseCandidate**: ranked hypotheses with confidence and rationale.
- **RemediationRecommendation**: non-destructive action guidance.
- **HumanDecision**: immutable audit record of operator intent.
- **Report**: portable markdown artifact for handoff and review.
- **AppSetting**: storage for configurable user-defined query templates.

## Reliability and Operational Safeguards
- Controlled error responses with next-step guidance.
- No silent fallback to dummy runtime data.
- Request payload limit middleware.
- Clear setup-required states for incomplete configuration.

## Diagrams
- Logical topology: `diagrams/architecture.mmd`
- Data movement: `diagrams/data-flow.mmd`
- Agent orchestration sequence: `diagrams/agent-flow.mmd`
