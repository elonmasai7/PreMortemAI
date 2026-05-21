# Deployment

## Local
1. Create virtualenv.
2. `make install`
3. Copy `.env.example` to `.env` and configure Splunk/AI.
4. `make run`

## Production Notes
- Run behind a reverse proxy with TLS.
- Set `APP_ENV=production`.
- Store environment variables in a secure secret manager.
- Persist SQLite file on durable storage or migrate to managed DB for scale.

## OpenAPI Export
```bash
make export-openapi
```
