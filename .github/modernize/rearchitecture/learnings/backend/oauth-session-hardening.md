# OAuth and Session Hardening

GitHub OAuth and cookie sessions require server-side state, expiry, and revocation even when the MVP store is in memory.

## What Happened
For NextHire auth-hardening-20261026, GitHub authorization was constrained to
`read:user user:email`; callback state is one-time and expires after ten minutes,
provider tokens remain server-side, and revocation calls GitHub's application
token endpoint. Session expiry and revocation are checked on every request.

## Takeaway
Keep OAuth state and provider tokens out of client responses, invalidate all
sessions after logout/password reset, and preserve environment-only provider
credentials. Durable persistence remains a follow-up migration.

## History
- 2026-10-26 (NextHire/auth-hardening-20261026): initial
