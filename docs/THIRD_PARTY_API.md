# PARALLAX Public API — Third-Party AI System Integration

**Version:** 1.0.0  
**Status:** Production  
**Base URL:** `https://ItsNotAILABS.github.io/PARRALAX-AIHFTFUND/api/v1`

---

## Overview

The PARALLAX Public API enables third-party AI systems to securely access:

1. **Public Artifacts** — Doctrine, architecture specifications, knowledge bases
2. **Digital Fingerprints** — Cryptographic verification of document authenticity
3. **Memory Insights** — Synthesized market patterns and trends (policy-gated)
4. **Trading Signals** — Market signals from PARALLAX trading engine
5. **Hierarchical Index** — Organized catalog of all public content

### Key Design Principles

- **Policy-Gated Access:** Only PUBLIC-tier content is exposed to third-party systems
- **Cryptographic Verification:** Every artifact includes SHA-256 fingerprint for tamper detection
- **No Raw Internals:** Memory queries return summaries and proofs, never raw memory content
- **Immutable Audit Trail:** All access is logged and timestamped on ANIMA chain
- **Rate Limiting:** Requests limited to 1,000 per hour per system

---

## Authentication

The public API does **not** require authentication for read-only access.

Optional: Include `X-API-Key` header for higher rate limits (contact administrator).

```bash
curl -H "X-API-Key: your-key-here" https://api.parallax.example.com/api/v1/health
```

---

## Endpoints

### Health & Status

#### GET `/api/v1/`
Root endpoint with API information.

**Response:**
```json
{
  "system": "PARALLAX Public API",
  "version": "1.0.0",
  "status": "operational",
  "purpose": "Third-party AI system access to public PARALLAX artifacts and memory",
  "documentation": "/api/v1/docs"
}
```

#### GET `/api/v1/health`
Health status and statistics.

**Response:**
```json
{
  "status": "healthy",
  "fingerprints_indexed": 245,
  "public_vaults": 8,
  "last_sync": "2026-06-14T03:00:24Z"
}
```

---

### Artifacts & Fingerprints

#### GET `/api/v1/public/artifacts`
List all PUBLIC-tier artifacts with digital fingerprints.

**Query Parameters:**
- `skip`: Number of results to skip (default: 0)
- `limit`: Number of results to return (default: 50, max: 1000)

**Response:**
```json
[
  {
    "doc_id": "artifact_001",
    "doc_name": "PARALLAX Sovereign Declaration",
    "doc_path": "FOUNDER_SPACE/INDEX.md",
    "content_hash": "a1b2c3d4...",
    "composite_hash": "e5f6g7h8...",
    "timestamp": "2026-06-13T12:34:56Z",
    "version": 1,
    "release_class": "PUBLIC",
    "tags": ["founder_doctrine", "sovereign_declaration"]
  }
]
```

#### GET `/api/v1/public/artifacts/{doc_id}`
Get fingerprint for a specific artifact.

**Parameters:**
- `doc_id`: Document identifier

**Response:**
```json
{
  "doc_id": "artifact_001",
  "doc_name": "PARALLAX Sovereign Declaration",
  "doc_path": "FOUNDER_SPACE/INDEX.md",
  "content_hash": "a1b2c3d4...",
  "composite_hash": "e5f6g7h8...",
  "timestamp": "2026-06-13T12:34:56Z",
  "version": 1,
  "release_class": "PUBLIC",
  "tags": ["founder_doctrine"]
}
```

#### GET `/api/v1/public/fingerprints/{doc_id}/verify`
Verify fingerprint for an artifact (enables off-chain verification).

**Parameters:**
- `doc_id`: Document identifier

**Response:**
```json
{
  "doc_id": "artifact_001",
  "composite_hash": "e5f6g7h8...",
  "timestamp": "2026-06-13T12:34:56Z",
  "verified": true,
  "message": "Fingerprint available for verification"
}
```

---

### Hierarchical Index

#### GET `/api/v1/public/index`
Get full hierarchical index of public artifacts with fingerprints.

**Response:**
```json
{
  "index_id": "idx_1a2b3c4d",
  "generated_at": "2026-06-14T03:00:24Z",
  "total_artifacts": 245,
  "artifacts_by_category": {
    "founder_doctrine": [
      {
        "id": "artifact_001",
        "name": "PARALLAX Sovereign Declaration",
        "path": "FOUNDER_SPACE/INDEX.md",
        "fingerprint": {
          "hash": "e5f6g7h8...",
          "timestamp": "2026-06-13T12:34:56Z"
        }
      }
    ],
    "architecture": [...]
  }
}
```

#### GET `/api/v1/public/search?q=query`
Search public artifacts by name, path, or tags.

**Query Parameters:**
- `q`: Search query (required, min 1 character)

**Response:**
```json
{
  "query": "sovereignty",
  "total_results": 12,
  "results": [
    {
      "id": "artifact_001",
      "name": "PARALLAX Sovereign Declaration",
      "path": "FOUNDER_SPACE/INDEX.md",
      "tags": ["founder_doctrine"],
      "fingerprint": "e5f6g7h8..."
    }
  ]
}
```

---

### Memory Vault Access

#### GET `/api/v1/public/memory/entries?tags=tag1,tag2`
Query PUBLIC-tier memory entries (no raw content).

**Query Parameters:**
- `tags`: Comma-separated list of tags to filter (optional)

**Response:**
```json
[
  {
    "entry_id": "mem_entry_001",
    "content_hash": "b9c8d7e6...",
    "summary": "Market momentum pattern detected in BTC/ETH correlation",
    "timestamp": "2026-06-14T02:15:00Z",
    "tags": ["market_pattern", "correlation"]
  }
]
```

#### GET `/api/v1/public/memory/vaults`
List PUBLIC-tier vaults (snapshots, no content).

**Response:**
```json
[
  {
    "vault_id": "vault_market_memory",
    "vault_type": "market_memory",
    "entry_count": 1247,
    "last_updated": "2026-06-14T03:00:00Z"
  }
]
```

#### GET `/api/v1/public/memory/meta-vault`
Query MetaVault insights (cross-vault synthesized knowledge).

**Response:**
```json
[
  {
    "insight_id": "insight_001",
    "name": "Q2 2026 Market Structure",
    "description": "Synthesized pattern from correlation vault and volatility vault",
    "timestamp": "2026-06-14T02:30:00Z"
  }
]
```

---

### Trading Signals

#### GET `/api/v1/public/signals`
Get PUBLIC-tier trading signals.

**Response:**
```json
[
  {
    "signal_id": "sig_001",
    "type": "momentum",
    "assets": ["BTC", "ETH"],
    "direction": "bullish",
    "confidence": 0.87,
    "timestamp": "2026-06-14T03:00:24Z"
  }
]
```

---

### Audit Information

#### GET `/api/v1/public/audit-log`
Get summary of access audit log (aggregated, no sensitive details).

**Response:**
```json
{
  "total_requests": 1247,
  "granted": 1213,
  "denied": 34,
  "denial_rate": 0.027
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid parameters) |
| 404 | Resource not found |
| 429 | Rate limit exceeded (1,000 req/hour) |
| 500 | Server error (contact admin) |

---

## Rate Limiting

- **Default:** 1,000 requests per hour
- **With API Key:** 10,000 requests per hour
- **Headers returned:**
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Digital Fingerprints

Every artifact is identified by a **composite SHA-256 hash**:

```
composite_hash = SHA-256(content_hash || metadata_hash)
```

Where:
- `content_hash` = SHA-256 of document content
- `metadata_hash` = SHA-256 of document metadata

**Verification Example:**

```python
import hashlib

# Verify locally
response = requests.get("https://api.parallax.example.com/api/v1/public/artifacts/doc_001")
fp = response.json()

# Recompute hash
content = fetch_document_content("doc_001")
metadata = fetch_document_metadata("doc_001")

content_hash = hashlib.sha256(content.encode()).hexdigest()
metadata_hash = hashlib.sha256(str(metadata).encode()).hexdigest()
composite = hashlib.sha256((content_hash + metadata_hash).encode()).hexdigest()

# Verify
assert composite == fp["composite_hash"], "Document has been modified!"
```

---

## Examples

### Python: List and Verify Artifacts

```python
import requests
import hashlib

api_url = "https://api.parallax.example.com/api/v1"

# List all public artifacts
resp = requests.get(f"{api_url}/public/artifacts?limit=10")
artifacts = resp.json()

for artifact in artifacts:
    print(f"ID: {artifact['doc_id']}")
    print(f"Name: {artifact['doc_name']}")
    print(f"Hash: {artifact['composite_hash']}")
```

### JavaScript: Search Artifacts

```javascript
const API_URL = "https://api.parallax.example.com/api/v1";

async function searchArtifacts(query) {
  const response = await fetch(`${API_URL}/public/search?q=${query}`);
  const results = await response.json();
  
  console.log(`Found ${results.total_results} results`);
  results.results.forEach(artifact => {
    console.log(`${artifact.name} (${artifact.id})`);
  });
}

searchArtifacts("doctrine");
```

### cURL: Get Health Status

```bash
curl https://api.parallax.example.com/api/v1/health | jq .
```

---

## Support

For issues or questions:

1. Check this documentation
2. Review error responses for specific error codes
3. Contact: admin@parallax.example.com

---

## License & Attribution

PARALLAX Public API is part of the PARALLAX Sovereign Organism.

**Architect:** Alfredo Medina Hernandez  
**Created:** 2026  
**Doctrine:** All data is sourced from discovered truths about systems, markets, and intelligence — not invented. The architecture preserves the genesis frequency across all public expressions.

---

*"Everything that exists inside PARALLAX was discovered, not invented."*
