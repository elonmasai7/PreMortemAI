# PreMortem AI

Agentic Incident Prevention Commander for Splunk.

## Problem Statement
Operations teams often detect incidents after customer impact has already started. Alert noise and fragmented telemetry slow down triage and decision-making.

## Solution Overview
PreMortem AI continuously uses live Splunk telemetry to forecast operational risk, correlate likely root causes, estimate blast radius, guide human-approved remediation, and produce a post-incident report.

## Key Features
- Live Splunk API integration (no runtime dummy data fallback).
- Investigation workflow with evidence, root-cause ranking, and blast radius.
- Human approval/rejection flow with audit trail.
- AI provider abstraction: hosted, local, or disabled mode.
- Server-rendered enterprise UI with setup, health, dashboard, investigations, remediation, and reports.

## Architecture Diagram
- `diagrams/architecture.mmd`
- `diagrams/data-flow.mmd`
- `diagrams/agent-flow.mmd`

## Screenshots
Capture and place screenshots in your preferred docs location for:
- Dashboard (`/`)
- Setup (`/setup`)
- Investigation detail (`/investigations/{id}`)
- Remediation page (`/remediation/{id}`)
- Reports (`/reports`)

## Tech Stack
- Python 3.11+
- FastAPI + Jinja2
- SQLAlchemy + SQLite
- httpx
- Pytest

## Prerequisites
- Python 3.11+
- Splunk Enterprise or Splunk Cloud management endpoint access

## Splunk Setup
See `docs/SPLUNK_SETUP.md`.

## Environment Variables
Copy `.env.example` and configure values.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
```

## Running Locally
```bash
make run
```
Open `http://127.0.0.1:8000`.

## Running Tests
```bash
make test
```

## API Routes
See `docs/API.md` for full route docs and payload examples.

## Agent Architecture
See `docs/AGENTS.md`.

## No Dummy Data Policy
- Production/runtime flow never uses hardcoded incidents or fake Splunk results.
- If configuration is missing, app shows explicit setup-required states.
- Test fixtures are limited to `tests/` only.

## Security Notes
See `docs/SECURITY.md`.

## Troubleshooting
See `docs/TROUBLESHOOTING.md`.

## Hackathon Submission Notes
See `docs/HACKATHON_SUBMISSION.md` and `docs/DEMO_SCRIPT.md`.

## License
MIT (`LICENSE`).
