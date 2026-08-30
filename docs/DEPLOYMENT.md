# Deployment

The local stack contains Nginx, FastAPI, PostgreSQL/PostGIS and Redis. Copy `.env.example` to `.env`, replace all placeholder secrets, then run `docker compose up --build`.

Production deployment must use managed persistence, automated backups, TLS certificates, non-default secrets, restricted network access, multiple backend workers, health/readiness probes, centralized JSON logs and migrations as a one-off release job.

Do not enable `PRESENTATION_MODE` or `AUTO_CREATE_SCHEMA` in production. `PARKING_PROVIDER=parkomatika` must remain unavailable until the official contract and credentials have been provided.
