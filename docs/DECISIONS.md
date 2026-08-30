# Architecture decisions

## ADR-001 — Provider boundary is backend-only

**Status:** accepted. The iOS app speaks only to ParkGo's REST API. `ParkingProvider` is an async backend protocol selected by configuration. Provider credentials and proprietary behavior therefore never ship to a device.

## ADR-002 — Backend is the session and price authority

**Status:** accepted. The client may render an estimate between syncs, but foregrounding and all state-changing operations reconcile through the backend. Monetary values use `Decimal`/`NUMERIC`; client DTOs transport them as strings.

## ADR-003 — PostGIS for production, deterministic fallback for unit tests

**Status:** accepted. Production nearby search uses `ST_DWithin`, `ST_Distance`, and a GiST index. Fast unit tests use SQLite and the same Haversine ordering in Python. PostgreSQL integration tests are enabled through a separate test database URL.

## ADR-004 — No Celery in the MVP

**Status:** accepted. Current operations are request/response or local-notification tasks. Redis supports rate limiting and future coordination. Celery is deferred until an actual durable background workload exists.

## ADR-005 — Presentation mode is explicit and non-production

**Status:** accepted. Presentation fixtures are gated by backend settings and Debug iOS configuration. The UI always displays `TEST MODE`; production session controls are unavailable while the provider is mock.

## ADR-006 — Lightweight dependency injection

**Status:** accepted. FastAPI dependencies and a small iOS `AppContainer` provide composition roots. No third-party DI container is introduced.

## ADR-007 — iOS deployment target and local tool limitation

**Status:** accepted. The project targets iOS 18 and Swift 6. The current automation host exposes Swift Command Line Tools but not full Xcode, so backend checks and portable Swift package tests run locally; simulator, WidgetKit, and UI tests require Xcode 16+.

## ADR-008 — Demo zone data is non-official

**Status:** accepted. Coordinates and zone numbers are presentation fixtures around central Krasnodar. They must never be represented as current municipal parking data.

## ADR-009 — Presentation-only offline fallback

**Status:** accepted. Debug Presentation Mode first exercises the local FastAPI backend. If initial demo authentication cannot reach it, a process-local repository supplies the same clearly labelled test flow so a partner presentation is not blocked by venue networking. The switch happens only during bootstrap; a live session never migrates between repositories. Standard and Release modes never silently fall back.

## ADR-010 — Mock billing unit

**Status:** accepted. The mock tariff is charged per started minute with a one-minute minimum and rounded to kopecks. This is presentation behavior only; a real adapter must use provider-authoritative tariff and final-price rules.

## ADR-011 — Payment failure after provider stop

**Status:** accepted. Stopping the provider session is irreversible. If mock payment then fails, the parking session is persisted as completed with `payment_status=failed` and the API returns `PAYMENT_FAILED` including the session ID. The client reconciles current/history instead of incorrectly presenting an active parking session.
