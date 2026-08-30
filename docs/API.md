# API

The versioned base path is `/api/v1`. JSON dates use ISO 8601 UTC. UUIDs are strings and decimal amounts are JSON strings.

## Authentication

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /auth/me`

Bearer access tokens are short-lived. Refresh rotates both access and refresh tokens.

## Vehicles

- `GET|POST /vehicles`
- `GET|PATCH|DELETE /vehicles/{vehicle_id}`
- `POST /vehicles/{vehicle_id}/default`

## Parking

- `GET /parking/nearby?latitude=&longitude=&radius=`
- `GET /parking/zones/{zone_id}`
- `POST /parking/sessions`
- `GET /parking/sessions/current`
- `GET /parking/sessions/{session_id}`
- `POST /parking/sessions/{session_id}/stop`
- `POST /parking/sessions/{session_id}/extend`
- `GET /parking/history`
- `GET /parking/stats`

## Operations

- `GET /health`

Errors use one envelope:

```json
{
  "error": {
    "code": "SESSION_ALREADY_ACTIVE",
    "message": "У вас уже есть активная парковка.",
    "details": {}
  }
}
```

Unknown failures return a safe generic message and a request ID, never a traceback.
