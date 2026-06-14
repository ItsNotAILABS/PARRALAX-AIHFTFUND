# Public API System — Complete Integration Guide

## Overview

This document describes the complete third-party AI API system for PARALLAX:

1. **Digital Fingerprinting Service** — SHA-256 + Merkle tree for document verification
2. **Expanded Memory Vault** — Policy-gated access to memory with MetaVault tier
3. **Public API Gateway** — 15+ REST endpoints for third-party AI systems
4. **Third-Party Integration Gateway** — Registration, authentication, rate limiting
5. **GitHub Pages Deployment** — Automatic documentation publishing

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Third-Party AI Systems (External)                               │
└────────┬──────────────────────────────────────────────────────┬─┘
         │                                                        │
         └────────────────────────────────────────────────────────┤
                                                                   │
                    ┌──────────────────────────────────────────────┘
                    │
        ┌───────────▼─────────────┐
        │ Public API Gateway      │
        │ (public_api.py)        │
        │                         │
        │ • /api/v1/health       │
        │ • /api/v1/artifacts    │
        │ • /api/v1/index        │
        │ • /api/v1/memory/*     │
        │ • /api/v1/signals      │
        └──┬──────────────┬───────┘
           │              │
      ┌────▼────┐   ┌────▼────────────────┐
      │          │   │                     │
      │ Policy   │   │ Third-Party Gateway │
      │ Gating   │   │ (third_party...)    │
      │          │   │                     │
      └────┬─────┘   │ • Registration      │
           │         │ • API Keys          │
           │         │ • Rate Limiting     │
           │         │ • Webhooks          │
           │         └────┬────────────────┘
           │              │
      ┌────▼──────────────▼──────────┐
      │                              │
      │ Security Boundary            │
      │ (Release Classes)            │
      │                              │
      └────┬──────────────┬──────────┘
           │              │
    ┌──────▼──────┐  ┌───▼──────────────┐
    │ Fingerprint │  │ Memory Vault     │
    │ Service     │  │ (expanded_...)   │
    │             │  │                  │
    │ • SHA-256   │  │ • SOVEREIGN_PRIV │
    │ • Merkle    │  │ • TRUNK          │
    │ • Versions  │  │ • PUBLIC ◄──────┐│
    │ • Changes   │  │ • MetaVault      ││
    └─────────────┘  └──────────────────┘│
                                        │
                        ┌───────────────┘
                        │
            ┌───────────▼──────────┐
            │ Indexed Artifacts &  │
            │ Market Memory         │
            │                       │
            │ • Doctrine            │
            │ • Architecture        │
            │ • Market Patterns     │
            │ • Trading Data        │
            └───────────────────────┘
```

---

## System Components

### 1. Digital Fingerprinting Service
**File:** `python/parralax/fingerprint_service.py`

**Capabilities:**
- SHA-256 hashing of document content
- Metadata hashing and composite hashing
- Merkle tree construction for collections
- Version tracking and change detection
- Classification by release class (SOVEREIGN_PRIVATE/TRUNK/PUBLIC)

**Usage:**
```python
from parralax.fingerprint_service import get_fingerprint_service

fps = get_fingerprint_service()

# Create fingerprint
fp = fps.create_fingerprint(
    doc_id="doc_001",
    doc_path="FOUNDER_SPACE/INDEX.md",
    doc_name="Sovereign Declaration",
    content=open("...").read(),
    release_class="PUBLIC",
    tags=["founder_doctrine"],
)

# Verify
is_valid, msg = fps.verify_fingerprint("doc_001", new_content)
```

### 2. Expanded Memory Vault
**File:** `python/parralax/expanded_vault.py`

**Capabilities:**
- Multiple vault types (cognitive, market_memory, trading_archive, etc.)
- MetaVault tier for cross-vault insights
- Policy-gated access (3 levels)
- Access audit logging
- Query interface for third-party systems

**Usage:**
```python
from parralax.expanded_vault import get_vault_service, AccessLevel

vault = get_vault_service()

# Create vault
snapshot = vault.create_vault(
    vault_id="vault_001",
    vault_type=VaultType.MARKET_MEMORY,
    access_level=AccessLevel.PUBLIC,
)

# Add entry
entry = vault.add_entry(
    vault_id="vault_001",
    entry_id="entry_001",
    content_hash="a1b2c3...",
    content_summary="Market momentum pattern",
    access_level=AccessLevel.PUBLIC,
    tags=["momentum", "correlation"],
)

# Query public entries
public = vault.query_public_entries(tags=["momentum"])
```

### 3. Public API Gateway
**File:** `python/parralax/public_api.py`

**Endpoints (15+):**
- Health & Status
  - `GET /api/v1/`
  - `GET /api/v1/health`
  
- Artifacts & Fingerprints
  - `GET /api/v1/public/artifacts`
  - `GET /api/v1/public/artifacts/{doc_id}`
  - `GET /api/v1/public/fingerprints/{doc_id}/verify`
  
- Index & Search
  - `GET /api/v1/public/index`
  - `GET /api/v1/public/search?q=query`
  
- Memory Access
  - `GET /api/v1/public/memory/entries`
  - `GET /api/v1/public/memory/vaults`
  - `GET /api/v1/public/memory/meta-vault`
  
- Trading
  - `GET /api/v1/public/signals`
  
- Audit
  - `GET /api/v1/public/audit-log`

**Features:**
- CORS enabled for third-party systems
- Rate limiting (1,000 req/hour default)
- Policy-gated responses (PUBLIC tier only)
- Digital fingerprints on every artifact
- Search across all indexed content

### 4. Third-Party Integration Gateway
**File:** `python/parralax/third_party_gateway.py`

**Capabilities:**
- System registration and API key generation
- API key verification and expiration
- Rate limit checking and enforcement
- Webhook registration for event subscriptions
- Usage tracking and reporting
- System activation/deactivation

**Usage:**
```python
from parralax.third_party_gateway import get_integration_gateway

gateway = get_integration_gateway()

# Register system
system = gateway.register_system(
    system_name="Alpha Trading Bot",
    contact_email="bot@example.com",
    description="Automated trading system",
    rate_limit_per_hour=5000,
)

# Returns API key: system.api_key

# Verify key
valid, system = gateway.verify_api_key(api_key)

# Check rate limit
allowed, msg = gateway.check_rate_limit(api_key)

# Register webhook
gateway.register_webhook(api_key, "https://example.com/webhook")
```

---

## Security Boundaries

### Release Classes
All content is classified by access level:

| Class | Access | Exposed to |
|-------|--------|-----------|
| `SOVEREIGN_PRIVATE` | Internal only | Organism builders only |
| `TRUNK` | Internal | Approved contractors/teams |
| `PUBLIC` | External | Third-party AI systems |

### Third-Party Access
- Only PUBLIC-tier content is exposed via public API
- Access is policy-gated at every endpoint
- All requests require valid API key (or anonymous with lower limits)
- All access is logged with timestamps and request details
- Rate limiting prevents abuse

### Memory Protection
- Raw memory content is never exposed
- Only metadata, summaries, and hashes are returned
- Merkle roots verify collection integrity
- Access attempts (grant/deny) are logged

---

## Integration for Third-Party AI Systems

### Step 1: Register
Contact: `admin@parallax.example.com`

Request registration with:
- System name
- Contact email
- Description
- Desired rate limit

### Step 2: Get API Key
Upon approval, you receive an API key:
```
pk_7a8b9c0d1e2f3g4h_5i6j7k8l9m0n1o2p
```

### Step 3: Make Requests
```bash
curl -H "X-API-Key: pk_..." \
  https://ItsNotAILABS.github.io/PARRALAX-AIHFTFUND/api/v1/health
```

### Step 4: Subscribe to Webhooks
Register webhook URLs to receive event notifications:
- `memory.updated` — Memory vault entries added
- `signal.generated` — New trading signals
- `vault.indexed` — New public content indexed

```python
gateway.register_webhook(api_key, "https://your-system.com/webhook")
```

---

## GitHub Pages Deployment

**Workflow:** `.github/workflows/deploy-api-docs.yml`

**Triggers:**
- Push to main branch with changes to API files
- Manual workflow dispatch

**Actions:**
1. Generate OpenAPI specification
2. Create API documentation index
3. Upload to GitHub Pages
4. Deploy to: `https://ItsNotAILABS.github.io/PARRALAX-AIHFTFUND/api/`

**Documentation:**
- Full API reference at `docs/THIRD_PARTY_API.md`
- OpenAPI spec at `docs/api/openapi.json`
- Interactive explorer (Swagger UI) at `docs/api/`

---

## Configuration

### Environment Variables
```bash
# API Configuration
PARALLAX_API_PORT=8000
PARALLAX_API_HOST=0.0.0.0

# Rate Limiting
PARALLAX_DEFAULT_RATE_LIMIT=1000
PARALLAX_VIP_RATE_LIMIT=10000

# Memory Vault
PARALLAX_MAX_VAULTS=21
PARALLAX_MAX_ENTRIES_PER_VAULT=233

# Fingerprinting
PARALLAX_FINGERPRINT_HASH_ROUNDS=8
```

### API Configuration File (optional)
```yaml
# parralax_config.yaml
api:
  port: 8000
  host: "0.0.0.0"
  title: "PARALLAX Public API"

rate_limits:
  default: 1000
  authenticated: 10000

fingerprinting:
  hash_algorithm: "sha256"
  merkle_tree: true
  version_tracking: true

memory_vault:
  max_vaults: 21
  max_entries_per_vault: 233
  include_meta_vault: true
```

---

## Monitoring & Observability

### Metrics
- Total requests per endpoint
- Request success/failure rate
- Rate limit hits
- Third-party system usage
- Memory vault access patterns

### Logging
```python
# All access logged via vault_service
logs = vault_svc.get_access_log(limit=100)

# Shows:
# - Requester ID
# - Requested resource
# - Access level required
# - Grant/deny decision
# - Timestamp
```

### Health Checks
```bash
# Is API healthy?
curl /api/v1/health

# Response:
{
  "status": "healthy",
  "fingerprints_indexed": 245,
  "public_vaults": 8,
  "last_sync": "2026-06-14T03:00:24Z"
}
```

---

## Troubleshooting

### Rate Limit Exceeded
- Verify API key is configured correctly
- Check usage: `GET /api/v1/health`
- Contact admin for higher limits

### Fingerprint Mismatch
- Document content was modified
- Verify against composite_hash from API
- Use verification endpoint: `GET /api/v1/public/fingerprints/{doc_id}/verify`

### Access Denied
- Resource may not be PUBLIC-tier
- Verify API key is active
- Check access log for specific reason

### Memory Entry Not Found
- Entry may not be indexed yet (async process)
- Try searching with tags: `GET /api/v1/public/memory/entries?tags=...`
- Check vault summaries: `GET /api/v1/public/memory/vaults`

---

## Next Steps

1. **Testing:** Run integration tests against all endpoints
2. **Documentation:** Publish API docs to GitHub Pages via workflow
3. **Onboarding:** Register first third-party AI systems
4. **Monitoring:** Set up metrics collection and alerting
5. **Scaling:** Optimize rate limiting and caching strategies

---

## References

- API Documentation: `docs/THIRD_PARTY_API.md`
- Source Code: `python/parralax/`
- Deployment: `.github/workflows/deploy-api-docs.yml`
- Integration Examples: `docs/examples/`

---

*Third-Party AI API System • PARALLAX Sovereign Organism*  
*"Everything that exists inside PARALLAX was discovered, not invented."*
