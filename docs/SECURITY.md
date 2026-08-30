# Security

- TLS terminates at Nginx in deployed environments; plain HTTP is local-only.
- Passwords are hashed with Argon2 and are never logged.
- JWT access tokens are short-lived. Refresh tokens rotate and server-side records prevent reuse.
- Authentication endpoints are rate-limited through Redis with a safe development fallback.
- Pydantic validates input, SQLAlchemy parameterizes database access, and CORS is allow-listed.
- Secrets come from environment variables. The repository and iOS bundle contain no provider API keys.
- Request logs are structured and redact authorization, password, token and payment material.
- Future parking-provider credentials and calls remain backend-only.
- Sentry wiring is optional and disabled unless a DSN is explicitly configured.

Before production, use managed secrets, enable HTTPS/HSTS, narrow trusted proxies and CORS, run dependency/container scanning, configure APNs credentials, and complete a threat model and provider-specific security review.
