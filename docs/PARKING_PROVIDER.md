# Parking provider contract

`ParkingProvider` isolates zone lookup, price calculation and session lifecycle operations. DTOs are provider-neutral and never expose database entities.

The mock implementation has deterministic Krasnodar fixtures, Haversine distance calculation, in-memory provider sessions, price rounding, mock payments and opt-in error simulation. The fixture data is test-only and is not an official description of municipal parking.

Provider exceptions are translated once into stable application error codes. HTTP routes do not depend on a concrete provider.
