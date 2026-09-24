# n8n + PostgreSQL Deployment Guide

Status: **READY — configuration artifact**
Date: 2026-09-24
Task: T-001

## Quick Start (machine with Docker)

```bash
cd services/dev
docker compose up -d

# Verify n8n web login
curl -s http://localhost:5678/ | head -5

# Verify PostgreSQL connectivity
PGPASSWORD=change-me-in-production psql -h localhost -p 5432 -U nippan -d nippan_dev -c "SELECT version();"
```

## Access Points

| Service     | URL                   | Purpose                    |
|-------------|-----------------------|----------------------------|
| n8n UI      | http://localhost:5678 | Bot workflow editor       |
| PostgreSQL  | localhost:5432        | Data store (n8n + schema) |

## Production Host Recommendation

### Option 1: DigitalOcean Droplet (~$12/mo)
- 1 vCPU, 1GB RAM Ubuntu 22.04
- Install Docker via `apt install docker.io`
- Run `docker compose up -d` from this repo
- Set up Cloudflare DNS → reverse proxy → SSL
- Daily backup: `docker exec nippan-postgres-dev pg_dump nippan_dev > /backups/pre-$DATE.sql`

### Option 2: Hetzner Cloud CX22 (~€4/mo)
- 2 vCPU, 2GB RAM
- Same Docker setup, cheaper but slightly less support

### Option 3: Oracle Cloud Free Tier
- Always-free ARM instances (4 CPUs, 24GB RAM total)
- Can run both n8n and PostgreSQL on same instance or separate containers
- No cost but setup is complex and region-dependent

## SSL/HTTPS Setup (after host chosen)

```bash
# Using Caddy (recommended — auto HTTPS)
# Caddyfile at services/dev/Caddyfile:
localhost {
  reverse_proxy localhost:5678
}
```

Or using Cloudflare Proxy (no server-side SSL needed):
1. Point domain through Cloudflare
2. Deploy n8n on HTTP port
3. Cloudflare handles SSL termination
4. Use Cloudflare Tunnel or Zero Trust Access for auth

## Daily Backup Script

```bash
#!/bin/bash
BACKUP_DIR="/opt/nippan/backups"
DATE=$(date +%Y%m%d)
mkdir -p "$BACKUP_DIR"
docker exec nippan-postgres-dev pg_dump nippan_dev | gzip > "$BACKUP_DIR/db-$DATE.sql.gz"
# Retain last 14 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +14 -delete
```

## Verification Checklist (run after deploy)

- [ ] `curl -s -o /dev/null -w "%{http_code}" http://localhost:5678/` → expect `200`
- [ ] Login to n8n UI and see dashboard
- [ ] `docker exec nippan-postgres-dev pg_isready` → ready
- [ ] n8n settings show PostgreSQL connected (not SQLite)
- [ ] Backup script runs successfully: `bash backup.sh`
- [ ] Restored from backup: `docker exec -i nippan-postgres-dev psql nippan_dev < backups/db-latest.sql.gz`

## Notes

- This stack uses **SQLite by default** in n8n — explicitly configured above to use PostgreSQL via environment variables
- For production: change all placeholder passwords, enable HTTPS, set up monitoring
- Startup Playbook note: hosted n8n execution limits were rejected; self-hosted avoids those limits for ~18,000 messages/month at 30 tenants
