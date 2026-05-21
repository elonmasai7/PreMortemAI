# PreMortem AI

PreMortem AI is an evidence-first incident prevention platform for SRE, DevOps, ITOps, SecOps, and platform engineering teams using Splunk. It helps teams answer six operational questions before outages happen:

1. What is likely to break soon?
2. Why is it likely to break?
3. What services and users could be affected?
4. What evidence supports the conclusion?
5. What should an engineer do next?
6. What should be documented after the decision?

## 1) Project Title
PreMortem AI: Agentic Incident Prevention Commander for Splunk

## 2) Product Description
PreMortem AI converts live Splunk telemetry into structured investigations, confidence-ranked root-cause hypotheses, blast-radius estimates, and human-approved remediation decisions. It is intentionally designed for operational trust: no hidden mock data, no silent errors, and no destructive auto-actions.

## 3) Problem Statement
Most incident workflows are reactive. Teams are alerted after customer impact begins, then manually correlate logs, metrics, deployment events, and dependency behavior under pressure. This increases MTTR, causes context switching, and creates inconsistent post-incident learning.

## 4) Solution Overview
PreMortem AI provides a full prevention workflow:
- Risk-first dashboard for executive and on-call visibility
- Evidence-centric investigation views for engineers
- Human approval gate for remediation outcomes
- Auditable decision history and report generation

## 5) Primary Users
- Site Reliability Engineers
- DevOps Engineers
- ITOps Engineers
- Platform Engineers
- Security Operations Analysts
- Engineering Managers

## 6) Product Outcomes
- Faster operational understanding during risk escalation
- Evidence-backed decision making across teams
- Reduced guesswork in root-cause analysis
- Better handoff quality via standardized report output

## 7) Current Capabilities
- Live Splunk API integration (no runtime fake data fallback)
- Internal Python multi-agent orchestration
- AI provider abstraction (`openai_compatible`, `local`, `disabled`)
- Human approval/rejection with note and audit trail
- Setup and health transparency pages
- Markdown report generation

## 8) Architecture Diagrams
- `diagrams/architecture.mmd`
- `diagrams/data-flow.mmd`
- `diagrams/agent-flow.mmd`

Render diagrams as PNG/SVG with your preferred Mermaid renderer.

## 9) Application Architecture (Current Implementation)

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
4. Forecast, root-cause, and blast-radius analysis update risk context.
5. Remediation recommendation is generated as approval-required.
6. Human approves or rejects with a note; action is audit logged.
7. Report Agent generates a markdown post-incident artifact.

## 10) Startup-Scale Product Architecture (Target Evolution)
The current implementation is optimized for local and small-team deployment. The following is a practical scale plan for startup product growth.

### Phase A: Team Adoption (Current + Near Term)
- Single FastAPI instance
- SQLite for application state
- Splunk as telemetry source of truth
- Manual operator workflows

### Phase B: Multi-Team SaaS Readiness
- Replace SQLite with managed Postgres
- Split web/API process from background workers
- Introduce queue-backed investigation execution
- Add user accounts, RBAC, and SSO (OIDC/SAML)
- Add tenant-aware data model boundaries

### Phase C: Scale and Reliability
- Horizontal API scaling behind load balancer
- Worker autoscaling by queue depth and job latency
- Per-tenant rate limits and usage quotas
- Caching layer for repeated health/index metadata reads
- High-availability database and backup restore automation

### Phase D: Enterprise Maturity
- Fine-grained policy engine for remediation governance
- Private networking options and region placement controls
- Compliance controls (audit export, retention policy, key management)
- Full observability: traces, metrics, logs, SLOs, error budgets

## 11) Productization Priorities
- Stable onboarding: guided setup validation and first successful search
- Trust UX: show evidence, assumptions, confidence, and missing data
- Workflow quality: reduce click depth from detection to decision
- Admin controls: tenant settings, integrations, user permissions
- Platform reliability: predictable run times and transparent failures

## 12) Screenshots to Include
- Dashboard (`/`)
- Setup (`/setup`)
- Splunk Search (`/splunk/search`)
- Investigations (`/investigations`)
- Investigation Detail (`/investigations/{id}`)
- Remediation Approval (`/remediation/{id}`)
- Reports (`/reports`)

## 13) Tech Stack
- Python 3.11+
- FastAPI
- Jinja2 server-rendered templates
- SQLAlchemy + SQLite
- httpx
- Pydantic Settings
- Uvicorn
- Pytest

## 14) Prerequisites
- Python 3.11+
- Splunk Enterprise or Splunk Cloud management endpoint access
- Splunk credentials (token preferred)

## 15) Splunk Setup
See detailed setup and validation guidance in `docs/SPLUNK_SETUP.md`.

## 16) Environment Variables
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

## 17) Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
```

## 18) Run Locally
```bash
make run
```
Open `http://127.0.0.1:8000`.

## 19) Tests and Quality Checks
```bash
make test
make lint
make export-openapi
```

## 20) API Summary
Full request/response examples: `docs/API.md`

Route groups:
- Health: `/api/health*`
- Splunk: `/api/splunk*`
- Investigations: `/api/investigations*`
- AI: `/api/ai*`
- Remediation: `/api/remediation*`
- Reports: `/api/reports*`

## 21) Internal Agent System
Detailed responsibilities and execution model: `docs/AGENTS.md`

Core agents:
- Coordinator Agent
- Telemetry Agent
- Forecast Agent
- Root Cause Agent
- Blast Radius Agent
- Remediation Agent
- Report Agent

## 22) No-Dummy-Data Policy
- Runtime behavior never injects fake incidents or synthetic Splunk rows.
- Missing configuration is displayed as setup-required.
- Test fixtures are restricted to `tests/`.

## 23) Security and Trust
See full security documentation: `docs/SECURITY.md`

Implemented controls include:
- Environment-based secret management
- Request size limiting
- SPL query safety checks
- Jinja autoescaping
- Decision audit logging

## 24) Operations and Troubleshooting
- Troubleshooting guide: `docs/TROUBLESHOOTING.md`
- Deployment guide: `docs/DEPLOYMENT.md`
- Architecture details: `docs/ARCHITECTURE.md`

## 25) Product Roadmap (Practical Next Steps)
1. Authentication and tenant RBAC
2. Queue-backed async investigation runs
3. Managed Postgres migration
4. Alert subscriptions and notification channels
5. Integration catalog (ticketing, chatops, incident platforms)
6. SLA reporting and team-level analytics

## 26) License
MIT (`LICENSE`)
