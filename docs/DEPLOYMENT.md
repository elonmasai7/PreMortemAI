# Deployment

## Deployment Targets
- Local developer machine
- Single-node VM/container for hackathon demos
- Internal lab environment behind reverse proxy

## Local Development Deployment
1. Create environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   make install
   ```
2. Create configuration:
   ```bash
   cp .env.example .env
   ```
3. Configure Splunk and optional AI values.
4. Validate environment:
   ```bash
   make check-env
   make validate-splunk
   ```
5. Run app:
   ```bash
   make run
   ```

## Production-Oriented Guidance

### Runtime
- Set `APP_ENV=production`.
- Disable auto-reload (production Uvicorn/Gunicorn settings).
- Run app as non-root user.

### Networking
- Put behind reverse proxy (Nginx/Traefik/ALB) with TLS.
- Restrict ingress to trusted operator networks.
- Restrict egress to Splunk and optional AI endpoints.

### Secrets
- Do not store credentials in repo.
- Inject env vars from secure secret manager.
- Rotate Splunk/API credentials regularly.

### Persistence
- SQLite is acceptable for hackathon/local usage.
- For shared/high-availability deployment, migrate to managed relational DB.

## Health and Readiness
Use:
- `GET /api/health/liveness` for process checks
- `GET /api/health/readiness` for dependency readiness checks

## Build and Verification Commands
```bash
make lint
make test
make export-openapi
```

## OpenAPI Export
```bash
make export-openapi
```
Output file: `docs/openapi.json`
