# War Room — Dev-Time API Key Authentication Guide

## Overview

The War Room preview endpoint (`/war-room/...`) supports **three** authentication
methods, evaluated in priority order:

1. **Dev-time API key** (Bearer token) — configured via `NIPPAN_WAR_ROOM_DEV_API_KEY`
2. **Local access** (loopback) — fallback when remote access is disabled
3. **Cloudflare Access JWT** — production remote access path

This document covers method #1 — enabling dev-time remote access via API key.

---

## How It Works

When `NIPPAN_WAR_ROOM_DEV_API_KEY` is set:

1. Every request to `/war-room/...` is checked for an `Authorization` header
2. The header value is stripped of the `Bearer ` prefix (case-insensitive)
3. Both the configured key and the provided token are hashed with **SHA-256**
4. Hashes are compared using **`hmac.compare_digest()`** (constant-time comparison)
5. If hashes match → access granted
6. If no valid token → **HTTP 403 Forbidden** (fail-closed)

### Code reference

| Component | Location |
|-----------|----------|
| Auth logic | `services/core/app/war_room/remote_auth.py` line 222–252 |
| Request gate | `services/core/app/war_room/transport.py` line 336–388 |
| Settings | `services/core/app/settings.py` line 44–49 |

---

## How to Enable Remote Access

### Step 1: Generate a strong API key

Use a cryptographically secure random generator:

```bash
# Python one-liner (generate 64-char hex key)
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Or use any password manager / secret generator. Minimum recommendation: **64 characters**.

### Step 2: Set the environment variable

In your `.env` file (never commit `.env`):

```env
NIPPAN_WAR_ROOM_DEV_API_KEY=<your-generated-key>
```

### Step 3: Restart the service

The settings are cached via `@lru_cache()`. Restart the FastAPI process for
the new value to take effect.

### Step 4: Access from dev machine

Send requests with the `Authorization` header:

```bash
curl -H "Authorization: Bearer <your-key>" \
  http://localhost:8000/war-room/snapshot
```

Or use any HTTP client:

```javascript
fetch('http://localhost:8000/war-room/snapshot', {
  headers: { 'Authorization': 'Bearer <your-key>' }
});
```

Both `Bearer` and `bearer` prefixes are accepted.

---

## Fail-Closed Behavior

If `NIPPAN_WAR_ROOM_DEV_API_KEY` is **not set**:

- The API key auth path is **disabled entirely**
- Requests fall through to the next auth check (local access or Cloudflare JWT)
- If neither is available → **HTTP 403**

This ensures that even misconfigurations cannot bypass authentication.

## Security Properties

| Property | Implementation |
|----------|----------------|
| Constant-time comparison | `hmac.compare_digest()` prevents timing attacks |
| No plain-text storage | Keys are hashed with SHA-256 before comparison |
| Fail-closed | Missing config = auth disabled, not permissive |
| No logging of keys | API key never logged (header value checked, not stored) |
| Independent of Cloudflare | Dev key works without Cloudflare Access setup |

## Rotation

To rotate the key:

1. Generate a new key using Step 1 above
2. Set `NIPPAN_WAR_ROOM_DEV_API_KEY` to the new value in `.env`
3. Restart the service
4. Update all clients with the new key
5. Revoke old key (it's just a value in `.env`, no state to clean up)

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 403 on every request | Key not set or restarted after setting | Verify `.env` has the key; restart service |
| 403 after setting key | Wrong key sent or stale cache | Double-check key matches; restart (LRU cache invalidated) |
| Header rejected | Malformed Authorization header | Ensure format is exactly `Bearer <key>` (no extra spaces) |
