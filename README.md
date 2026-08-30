# ParkGo

ParkGo is a production-oriented MVP for starting and stopping city parking in one or two actions. The demo is configured for Krasnodar and deliberately uses non-official test zones through `MockParkingProvider`.

> **TEST MODE:** no real parking session or payment is created. Production start/payment controls remain disabled until an authorized parking provider is configured.

## Product

The iPhone client finds the closest paid parking zone, displays the rate and selected vehicle, starts a session, keeps the active session in sync, and records the completed session in history.

## Key features

- Automatic nearby-zone discovery and a native MapKit map
- Multiple vehicles with a default-vehicle workflow
- Active-session timer, estimated amount, geofence reminders, and Live Activity
- History and monthly statistics
- Stable Demo and Presentation modes
- Replaceable server-side parking-provider boundary

## Architecture

```text
iPhone (SwiftUI)
      |
      | HTTPS + JWT
      v
FastAPI application
      |
      +--> PostgreSQL + PostGIS
      +--> Redis
      |
      v
ParkingProvider
      +-- MockParkingProvider (current, test data)
      `-- ParkomatikaProvider (contract-only placeholder)
```

Business rules live in backend services. Route handlers validate HTTP input, repositories own persistence, and provider adapters own external parking operations. The backend is the source of truth for the active session and monetary amount.

## Tech stack

- iOS 18+, Swift 6, SwiftUI, Observation, MapKit, CoreLocation, ActivityKit, WidgetKit
- Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2 async, Alembic
- PostgreSQL/PostGIS, Redis, Docker Compose, Nginx
- pytest, Ruff, mypy, GitHub Actions

## Local setup

1. Copy the example environment file: `cp .env.example .env`.
2. Set development-only secrets in `.env`.
3. Run `make up`.
4. Open <http://localhost:8000/docs> or call `GET /api/v1/health`.

The database is migrated automatically by the backend container. Demo zones are seeded at startup when `PARKING_PROVIDER=mock`.

## Backend

```bash
make backend-install
make backend-test
make backend-run
```

API details are in [docs/API.md](docs/API.md).

## iOS

Open `ios/ParkGo.xcodeproj` with Xcode 16 or newer, select the `ParkGo` scheme and an iOS 18 simulator, then run. For a local backend, use the Debug API base URL documented in `ios/README.md`.

## Demo mode

Debug builds show a visible **TEST MODE** banner. Demo mode uses a fixed position in central Krasnodar, non-official zones, a Toyota RAV4, mock biometric approval, working session timers, mock payment, and local history. Presentation Mode first uses FastAPI and falls back only during initial bootstrap to a process-local demo repository if the venue cannot reach the development API.

## Tests

```bash
make lint
make test
make ios-check
```

Backend tests use an isolated database configuration. iOS unit and UI test targets cover networking, state, formatting, vehicle selection, and the start-to-history happy path.

## Security

Passwords are Argon2-hashed, short-lived access tokens are paired with rotating refresh tokens, secrets stay in environment variables, and provider credentials never enter the mobile app. See [docs/SECURITY.md](docs/SECURITY.md).

## Future Parkomatika integration

Only the backend will implement `ParkomatikaProvider`, after a documented and authorized API contract is supplied. No private endpoints or reverse engineering are used. See [docs/PARKOMATIKA_INTEGRATION.md](docs/PARKOMATIKA_INTEGRATION.md).

## Screenshots

Screenshots will be captured from the final Presentation Mode build on an iPhone simulator.
