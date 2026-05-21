# Hackathon Submission

## Project
PreMortem AI: Agentic Incident Prevention Commander for Splunk.

## What It Does
- Predicts likely incidents from live Splunk telemetry.
- Builds evidence-grounded root-cause hypotheses.
- Estimates blast radius.
- Produces human-approved remediation recommendations.
- Generates post-incident markdown reports.

## AI Usage
- AI provider abstraction with hosted, local, and disabled modes.
- Outputs are grounded in evidence with confidence and assumptions.

## Splunk Usage
- Splunk REST API
- Search jobs API
- Index and saved search listing
- SPL validation and execution workflows

## Impact
- Helps SRE/DevOps teams move from reactive alerts to proactive prevention.
- Adds auditable human decision control before any remediation action.

## Track Fit
- Built specifically for Splunk Agentic Ops Hackathon requirements.

## Future Roadmap
- Add RBAC and SSO.
- Add richer topology-aware dependency graph.
- Add policy-driven remediation guardrails.
