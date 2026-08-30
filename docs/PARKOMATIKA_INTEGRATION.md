# Future Parkomatika integration

ParkGo currently uses `MockParkingProvider`. No undocumented or private Parkomatika endpoint is called, and no official endpoint, parameter or commercial condition is assumed.

## Capabilities required from an authorized API

- list/search parking zones and retrieve current tariffs and schedules;
- create, retrieve, extend and stop a parking session;
- calculate authoritative estimates and final amounts;
- initiate or confirm payments and retrieve payment state;
- expose idempotency, error and availability semantics.

## Credential placement

The API key or client credential belongs in a backend secret store and is injected through environment configuration. It must never be embedded in the iOS app, source repository, logs or analytics.

## Adapter implementation

After an official contract is available, implement the existing `ParkomatikaProvider` methods with `httpx.AsyncClient`, explicit timeouts, retry only for safe/idempotent operations, mapped errors, request IDs and contract tests. The app and parking services remain unchanged.

## Questions for Parkomatika

1. What environments, authentication mechanism, scopes and credential rotation process are available?
2. What are the documented zone, tariff, session, extension, stop and payment contracts?
3. Which operation is the authoritative source of final price and payment state?
4. Are idempotency keys, webhooks and request correlation supported?
5. What are rate limits, timeout targets, maintenance windows and retry recommendations?
6. Which session state transitions and error codes are possible?
7. How are time zones, grace periods, minimum billing units and schedule exceptions represented?
8. What personal data is processed, retained or required, and what compliance terms apply?
9. Is sandbox/test data provided and what is the production certification process?
10. What support and incident-escalation channels apply?
