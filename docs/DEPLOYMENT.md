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

6. Run worker (optional when `QUEUE_ENABLED=true`):
   ```bash
   make worker
   ```

7. Apply migrations:
   ```bash
   make migrate
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
- PostgreSQL is the default production target.
- Use Alembic migrations for schema changes.
- Use periodic backups with `make backup-db` and tested restore drills using `make restore-db`.

### Queue and Cache
- Configure Redis (`REDIS_URL`) for queue and cache/rate-limiting features.
- Enable investigation worker queue with `QUEUE_ENABLED=true`.

## Container Profiles
- Development profile: `docker-compose.dev.yml`
- Production profile: `docker-compose.prod.yml`
- Kubernetes manifests: `deploy/k8s/`

## Health and Readiness
Use:
- `GET /api/health/liveness` for process checks
- `GET /api/health/readiness` for dependency readiness checks

## Build and Verification Commands
```bash
make lint
make test
make export-openapi
make migrate
```

## OpenAPI Export
```bash
make export-openapi
```
Output file: `docs/openapi.json`
