# Hackathon Submission

## Project Name
PreMortem AI: Agentic Incident Prevention Commander for Splunk

## One-Line Pitch
PreMortem AI transforms live Splunk telemetry into proactive, evidence-grounded incident prevention decisions with human-approved remediation and auditable reporting.

## Problem We Solve
Ops teams often discover incidents too late. By the time alerts fire, user impact has already started and engineers still need to manually correlate logs, metrics, deploy events, and dependencies across multiple views.

## Solution Summary
PreMortem AI provides an end-to-end prevention workflow:
1. Detect risk trends from Splunk telemetry.
2. Build investigation context with evidence and root-cause ranking.
3. Estimate blast radius across services and transactions.
4. Recommend safe, human-approved remediation.
5. Generate post-incident report artifacts for learning and detection improvement.

## Core Capabilities
- Real Splunk search execution (no runtime mock incidents).
- Investigation orchestration via internal Python multi-agent system.
- AI provider abstraction with hosted/local/disabled modes.
- Human decision audit log for approval/rejection actions.
- Markdown report generation for post-incident communication.

## AI Usage Details
- AI is used for summarization, root-cause reasoning support, remediation drafting, and report generation.
- Outputs include confidence and are grounded in available evidence.
- Disabled AI mode keeps workflow functional with deterministic logic.

## Splunk Usage Details
- Splunk REST API integration for:
  - connection test
  - index listing
  - saved search listing
  - SPL parser validation
- Splunk search jobs API for live query execution and polling.

## Why This Matters
- Reduces reaction lag by shifting from alert response to risk prevention.
- Improves operator trust by making evidence and assumptions visible.
- Preserves human control over any remediation decision.

## Track Fit
This project is purpose-built for the Splunk Agentic Ops Hackathon:
- Agentic workflow
- Splunk-native telemetry analysis
- Real-world operations relevance
- Explainability and governance focus

## Demo Highlights
- Setup truth page (`/setup`) with explicit config health.
- Live search workbench (`/splunk/search`) with saved templates.
- Investigation detail (`/investigations/{id}`) with evidence timeline and root-cause ranking.
- Remediation approval (`/remediation/{id}`) with audit trail.
- Report exports (`/reports`).

## Future Roadmap
- Enterprise authN/authZ (SSO + RBAC)
- Service topology graph enrichment
- Policy-driven remediation guardrails
- Enhanced forecasting models and historical trend backtesting
