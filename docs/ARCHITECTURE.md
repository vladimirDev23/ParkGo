# Architecture

ParkGo uses a modular monolith for the MVP. It keeps transactions and business invariants simple while preserving explicit boundaries that can later be extracted if scale requires it.

```text
SwiftUI Views -> ViewModels -> Repositories -> APIClient
                                          |
                                          v
FastAPI routes -> Services -> Repositories -> PostgreSQL/PostGIS
                       |
                       `-> ParkingProvider -> Mock / future Parkomatika
```

## Backend modules

- `api/v1`: transport concerns and dependency wiring
- `services`: application use cases and transaction boundaries
- `repositories`: database queries only
- `providers/parking`: authorized external-system boundary
- `models` and `schemas`: persistence entities and transport contracts
- `core`, `security`, `exceptions`: cross-cutting configuration, tokens, logging and errors

The database prevents more than one active session per user with a partial unique index. Services repeat the check for a useful domain error and lock relevant rows during changes.

## iOS modules

- `App`: composition root and global session store
- `Core`, `Networking`: reusable errors, API transport and Keychain tokens
- `Features`: screens grouped by user capability
- `Services`: location, notifications, geofencing, biometrics and activities
- `DesignSystem`: restrained native tokens/components
- `LiveActivity`, `Widgets`: shared ActivityKit attributes and widget extension UI

`ParkingSessionStore` is the only app-level active-session state. It reconciles `GET /sessions/current` on foreground, and Live Activity updates consume that same store snapshot.

## Data flow for stopping parking

1. iOS posts the session identifier.
2. The service loads and locks the active session and verifies ownership.
3. The provider calculates and stops the external session.
4. Mock payment is recorded.
5. The database session is finalized atomically.
6. The response becomes the iOS and Live Activity state.
