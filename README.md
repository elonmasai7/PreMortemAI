# PreMortem AI

PreMortem AI is an agentic incident prevention commander for Splunk. It helps SRE, DevOps, ITOps, SecOps, and platform teams identify what is likely to fail, why it is likely to fail, what could be impacted, and what action should be approved by a human before escalation becomes an outage.

## 1) Project Title
PreMortem AI: Agentic Incident Prevention Commander for Splunk

## 2) Short Description
An enterprise-focused FastAPI application that turns live Splunk telemetry into evidence-grounded investigations, remediation recommendations, and post-incident reports with human decision auditability.

## 3) Problem Statement
Most operations workflows are reactive. Teams receive alerts after user impact has started, then spend critical minutes correlating logs, metrics, deployments, and dependency behavior across tools. This delay increases MTTR, business impact, and operator fatigue.

## 4) Solution Overview
PreMortem AI continuously analyzes Splunk operational telemetry and provides:
- A risk-first executive dashboard for rapid understanding.
- An investigation workspace with evidence timeline, query transparency, root-cause ranking, and blast radius.
- A remediation approval workflow where actions are recommended but never destructively auto-executed.
- A report generator for post-incident documentation and follow-up detection improvements.

## 5) Key Features
- Live Splunk REST/search job integration with no runtime mock fallback.
- Internal Python multi-agent orchestration (no external JS agent frameworks).
- Configurable AI provider abstraction (`openai_compatible`, `local`, `disabled`).
- Evidence-grounded reasoning with confidence, assumptions, and missing data.
- Human approval/rejection with note and audit trail.
- Structured setup and health pages showing configuration completeness.

## 6) Architecture Diagram
- `diagrams/architecture.mmd`
- `diagrams/data-flow.mmd`
- `diagrams/agent-flow.mmd`

To render a PNG/SVG from Mermaid diagrams, use your preferred Mermaid CLI/renderer and export from the files above.

## 6.1) Application Architecture (In README)

### Layered Architecture
```text
┌────────────────────────────────────────────────────────────────────┐
│                        Operator / Engineer UI                     │
│   Dashboard | Setup | Splunk Search | Investigations | Reports    │
└───────────────────────────────┬────────────────────────────────────┘
                                │ HTTP
┌───────────────────────────────▼────────────────────────────────────┐
│                         FastAPI + Jinja2                          │
│      API Routes + Page Routes + Validation + Error Handling       │
└───────────────────────────────┬────────────────────────────────────┘
                                │ invokes
┌───────────────────────────────▼────────────────────────────────────┐
│                        Internal Agent System                      │
│ Coordinator -> Telemetry -> Forecast -> Root Cause -> Blast Radius│
│                         -> Remediation -> Report                  │
└───────────────────────┬───────────────────────────────┬────────────┘
                        │                               │
          ┌─────────────▼─────────────┐   ┌────────────▼────────────┐
          │      Splunk Services      │   │      AI Abstraction     │
          │ REST + Search Jobs + SPL  │   │ openai/local/disabled   │
          └─────────────┬─────────────┘   └────────────┬────────────┘
                        │                               │
                        └──────────────┬────────────────┘
                                       │ persists
                         ┌─────────────▼──────────────┐
                         │       SQLite (State)       │
                         │ investigations/evidence/...│
                         └────────────────────────────┘
```

### Runtime Flow
1. User creates an investigation for a target service.
2. Coordinator Agent executes SPL templates via Splunk APIs.
3. Evidence is normalized and stored.
4. Forecast/root-cause/blast-radius analysis updates investigation risk context.
5. Remediation recommendation is generated and marked human-approval-required.
6. Human approves/rejects with note; decision is audit logged.
7. Report Agent generates a markdown post-incident artifact.

### Design Principles
- Evidence-first outputs (no invented incidents or fake telemetry).
- Human-controlled remediation decisions.
- Explicit setup/health transparency when config is incomplete.
- No Node.js and no JS framework dependency.

## 7) Screenshots Section
Capture and include screenshots for:
- Dashboard (`/`)
- Setup (`/setup`)
- Splunk Search Workbench (`/splunk/search`)
- Investigations List (`/investigations`)
- Investigation Detail (`/investigations/{id}`)
- Remediation Approval (`/remediation/{id}`)
- Reports (`/reports`)

## 8) Tech Stack
- Python 3.11+
- FastAPI
- Jinja2 server-rendered templates
- SQLAlchemy + SQLite
- httpx
- Pydantic Settings
- Uvicorn
- Pytest

## 9) Prerequisites
- Python 3.11 or newer
- A Splunk Enterprise or Splunk Cloud management endpoint
- Credentials for Splunk API access (token preferred)

## 10) Splunk Setup
Detailed guidance: `docs/SPLUNK_SETUP.md`

## 11) Environment Variables
Copy `.env.example` to `.env` and configure:

```env
APP_NAME=PreMortem AI
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
DATABASE_URL=sqlite:///./premortem.db

SPLUNK_BASE_URL=https://localhost:8089
SPLUNK_USERNAME=
SPLUNK_PASSWORD=
SPLUNK_TOKEN=
SPLUNK_VERIFY_SSL=false
SPLUNK_DEFAULT_INDEX=
SPLUNK_TIMEOUT_SECONDS=60

MCP_SERVER_URL=
MCP_ENABLED=false

AI_PROVIDER=disabled
AI_BASE_URL=
AI_API_KEY=
AI_MODEL=

LOG_LEVEL=INFO
```

## 12) Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
```

## 13) Running Locally
```bash
make run
```

Then open `http://127.0.0.1:8000`.

## 14) Running Tests
```bash
make test
```

Optional checks:
```bash
make lint
make export-openapi
```

## 15) API Routes
Full route documentation with request/response examples: `docs/API.md`

Quick groups:
- Health: `/api/health*`
- Splunk: `/api/splunk*`
- Investigations: `/api/investigations*`
- AI: `/api/ai*`
- Remediation: `/api/remediation*`
- Reports: `/api/reports*`

## 16) Agent Architecture
Detailed responsibilities and workflow: `docs/AGENTS.md`

Core agents:
- Coordinator Agent
- Telemetry Agent
- Forecast Agent
- Root Cause Agent
- Blast Radius Agent
- Remediation Agent
- Report Agent

## 17) No Dummy Data Policy
- Production/runtime code does not generate fake incidents.
- If Splunk config is missing, the UI/API explicitly show setup-required state.
- Test fixtures are used only in `tests/`.

## 18) Security Notes
Detailed threat model and controls: `docs/SECURITY.md`

Highlights:
- Secret-by-environment configuration
- Request body size limit
- SPL query safety checks
- Jinja autoescape templating
- Remediation decision audit logs

## 19) Troubleshooting
See `docs/TROUBLESHOOTING.md` for common operational issues and fixes.

## 20) Hackathon Submission Notes
- `docs/HACKATHON_SUBMISSION.md`
- `docs/DEMO_SCRIPT.md`

## 21) License
MIT (`LICENSE`)
