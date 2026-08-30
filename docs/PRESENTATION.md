# Presentation mode

Presentation Mode is a deterministic partner-demo configuration, not a live payment product.

It supplies a demo account, Toyota RAV4, historical sessions, a fixed central-Krasnodar position, nearby mock zones, low latency and disabled fault injection. The iOS Debug build displays `TEST MODE` throughout the flow.

The Debug app first signs into `demo@parkgo.local` with the local presentation credential seeded by the backend. If that initial request cannot reach the local API, Presentation Mode switches to the process-local demo repository. Pass `--offline-demo` to force that repository for UI tests; pass `--standard-mode` to show the normal authentication/onboarding path.

Suggested script:

1. Launch into the Home tab and point out automatic zone selection.
2. Open Map to show nearby demo fixtures.
3. Start parking and show the active timer and Live Activity.
4. Stop the session and show mock payment success.
5. Open History/Stats.
6. Show `ParkingProvider` and explain that the authorized Parkomatika adapter is the only future integration point.
