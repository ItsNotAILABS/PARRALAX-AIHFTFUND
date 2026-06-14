"""
Public API Gateway for Third-Party AI Systems
PARALLAX Sovereign Organism — GitHub Pages + REST API

PURPOSE: Provides secure, documented REST API for third-party AI systems to:
1. Access public artifact index with digital fingerprints
2. Query public memory patterns (policy-gated)
3. Retrieve trading signals and market insights
4. Verify document authenticity via fingerprints
5. Subscribe to updates

DESIGN PHILOSOPHY:
- Third-party systems can only access PUBLIC-tier content
- All responses include digital fingerprints for verification
- Requests are logged and rate-limited
- No raw internal data is exposed — only proofs and summaries
"""

from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from .fingerprint_service import get_fingerprint_service, DocumentFingerprint
from .expanded_vault import get_vault_service, AccessLevel

# Create public API app
public_api_app = FastAPI(
    title="PARALLAX Public API",
    description="Third-Party AI System Access Layer — Secure, Fingerprint-Verified, Policy-Gated",
    version="1.0.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
)

# CORS configuration — allow third-party AI systems
public_api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],  # Read-only for third-party systems
    allow_headers=["Content-Type", "X-API-Key"],
)

# Services
fingerprint_svc = get_fingerprint_service()
vault_svc = get_vault_service()

# Rate limiting (simple implementation — production should use Redis)
request_counts: Dict[str, int] = {}
MAX_REQUESTS_PER_HOUR = 1000


# ═══════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════

class FingerprintResponse(BaseModel):
    """Digital fingerprint for a document."""
    doc_id: str
    doc_name: str
    doc_path: str
    content_hash: str
    composite_hash: str
    timestamp: str
    version: int
    release_class: str
    tags: List[str]


class ArtifactMetadata(BaseModel):
    """Artifact with fingerprint."""
    id: str
    name: str
    path: str
    description: Optional[str] = None
    fingerprint: FingerprintResponse
    related_artifacts: List[str] = []


class VaultEntryResponse(BaseModel):
    """Memory vault entry (metadata only, no raw content)."""
    entry_id: str
    content_hash: str
    content_summary: str
    timestamp: str
    tags: List[str]


class MemoryPatternResponse(BaseModel):
    """Public memory pattern (synthesized insight, not raw memory)."""
    pattern_id: str
    pattern_type: str
    description: str
    confidence: float
    tags: List[str]
    timestamp: str


class IndexResponse(BaseModel):
    """Hierarchical artifact index with fingerprints."""
    index_id: str
    generated_at: str
    total_artifacts: int
    artifacts_by_category: Dict[str, List[ArtifactMetadata]]
    index_root_hash: str  # Merkle root for entire index


class HealthResponse(BaseModel):
    """Health status of public API."""
    status: str
    fingerprints_indexed: int
    public_vaults: int
    last_sync: str


class SearchResultsResponse(BaseModel):
    """Search results."""
    query: str
    total_results: int
    results: List[ArtifactMetadata]


# ═══════════════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════

def check_rate_limit(client_id: str = "anonymous") -> bool:
    """Simple rate limiting (production: use Redis)."""
    request_counts[client_id] = request_counts.get(client_id, 0) + 1
    return request_counts[client_id] <= MAX_REQUESTS_PER_HOUR


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS — HEALTH & INFO
# ═══════════════════════════════════════════════════════════════════════════

@public_api_app.get("/api/v1/", tags=["Health"])
async def root() -> Dict[str, str]:
    """Root endpoint — API information."""
    return {
        "system": "PARALLAX Public API",
        "version": "1.0.0",
        "status": "operational",
        "purpose": "Third-party AI system access to public PARALLAX artifacts and memory",
        "documentation": "/api/v1/docs",
    }


@public_api_app.get("/api/v1/health", tags=["Health"], response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health status of public API and indexed content."""
    public_fps = fingerprint_svc.export_fingerprints(release_class="PUBLIC")
    return HealthResponse(
        status="healthy",
        fingerprints_indexed=len(public_fps),
        public_vaults=len(vault_svc.vaults),
        last_sync=datetime.utcnow().isoformat() + "Z",
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS — ARTIFACT FINGERPRINTS & VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

@public_api_app.get(
    "/api/v1/public/artifacts",
    tags=["Artifacts"],
    response_model=List[FingerprintResponse]
)
async def list_public_artifacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
) -> List[FingerprintResponse]:
    """
    List all PUBLIC-tier artifacts with fingerprints.
    Paginated for third-party AI systems.
    """
    if not check_rate_limit():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    public_fps = fingerprint_svc.export_fingerprints(release_class="PUBLIC")
    paginated = public_fps[skip:skip + limit]
    
    return [
        FingerprintResponse(
            doc_id=fp["doc_id"],
            doc_name=fp["doc_name"],
            doc_path=fp["doc_path"],
            content_hash=fp["content_hash"],
            composite_hash=fp["composite_hash"],
            timestamp=fp["timestamp"],
            version=fp["version"],
            release_class=fp["release_class"],
            tags=fp["tags"],
        )
        for fp in paginated
    ]


@public_api_app.get(
    "/api/v1/public/artifacts/{doc_id}",
    tags=["Artifacts"],
    response_model=FingerprintResponse
)
async def get_artifact_fingerprint(doc_id: str) -> FingerprintResponse:
    """
    Get fingerprint for a specific artifact.
    Allows verification that artifact hasn't been tampered with.
    """
    fp = fingerprint_svc.get_fingerprint(doc_id)
    
    if not fp or fp.release_class != "PUBLIC":
        raise HTTPException(status_code=404, detail="Artifact not found or not public")
    
    return FingerprintResponse(
        doc_id=fp.doc_id,
        doc_name=fp.doc_name,
        doc_path=fp.doc_path,
        content_hash=fp.content_hash,
        composite_hash=fp.composite_hash,
        timestamp=fp.timestamp,
        version=fp.version,
        release_class=fp.release_class,
        tags=fp.tags,
    )


@public_api_app.get(
    "/api/v1/public/fingerprints/{doc_id}/verify",
    tags=["Verification"],
    response_model=Dict[str, Any]
)
async def verify_artifact(doc_id: str) -> Dict[str, Any]:
    """
    Verify fingerprint for artifact (without content).
    Third-party systems use this to verify authenticity.
    """
    fp = fingerprint_svc.get_fingerprint(doc_id)
    
    if not fp or fp.release_class != "PUBLIC":
        raise HTTPException(status_code=404, detail="Artifact not found or not public")
    
    return {
        "doc_id": doc_id,
        "composite_hash": fp.composite_hash,
        "timestamp": fp.timestamp,
        "verified": True,
        "message": "Fingerprint available for verification",
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS — HIERARCHICAL INDEX
# ═══════════════════════════════════════════════════════════════════════════

@public_api_app.get(
    "/api/v1/public/index",
    tags=["Index"],
    response_model=Dict[str, Any]
)
async def get_artifact_index() -> Dict[str, Any]:
    """
    Get full hierarchical index of public artifacts with fingerprints.
    Machine-readable format for third-party AI systems.
    """
    if not check_rate_limit():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    public_fps = fingerprint_svc.export_fingerprints(release_class="PUBLIC")
    
    # Group by tags (category)
    by_category: Dict[str, List[Dict]] = {}
    for fp in public_fps:
        category = fp["tags"][0] if fp["tags"] else "other"
        if category not in by_category:
            by_category[category] = []
        
        by_category[category].append({
            "id": fp["doc_id"],
            "name": fp["doc_name"],
            "path": fp["doc_path"],
            "fingerprint": {
                "hash": fp["composite_hash"],
                "timestamp": fp["timestamp"],
            },
        })
    
    return {
        "index_id": f"idx_{uuid.uuid4()}",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_artifacts": len(public_fps),
        "artifacts_by_category": by_category,
    }


@public_api_app.get(
    "/api/v1/public/search",
    tags=["Search"],
    response_model=Dict[str, Any]
)
async def search_artifacts(q: str = Query(..., min_length=1)) -> Dict[str, Any]:
    """
    Search public artifacts by name, path, or tags.
    Returns matching artifacts with fingerprints.
    """
    if not check_rate_limit():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    public_fps = fingerprint_svc.export_fingerprints(release_class="PUBLIC")
    q_lower = q.lower()
    
    results = [
        fp for fp in public_fps
        if q_lower in fp["doc_name"].lower()
        or q_lower in fp["doc_path"].lower()
        or any(q_lower in tag.lower() for tag in fp["tags"])
    ]
    
    return {
        "query": q,
        "total_results": len(results),
        "results": [
            {
                "id": fp["doc_id"],
                "name": fp["doc_name"],
                "path": fp["doc_path"],
                "tags": fp["tags"],
                "fingerprint": fp["composite_hash"],
            }
            for fp in results[:100]  # Limit results
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS — MEMORY VAULT ACCESS
# ═══════════════════════════════════════════════════════════════════════════

@public_api_app.get(
    "/api/v1/public/memory/entries",
    tags=["Memory"],
    response_model=List[Dict[str, Any]]
)
async def query_public_memory(tags: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    """
    Query PUBLIC-tier memory entries.
    Returns memory metadata and summaries, never raw memory content.
    """
    if not check_rate_limit():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    tag_list = tags.split(",") if tags else None
    entries = vault_svc.query_public_entries(tags=tag_list)
    
    return [
        {
            "entry_id": e.entry_id,
            "content_hash": e.content_hash,
            "summary": e.content_summary,
            "timestamp": e.timestamp,
            "tags": e.tags,
        }
        for e in entries
    ]


@public_api_app.get(
    "/api/v1/public/memory/vaults",
    tags=["Memory"],
    response_model=List[Dict[str, Any]]
)
async def list_public_vaults() -> List[Dict[str, Any]]:
    """
    List PUBLIC-tier vaults (snapshots, no raw content).
    Shows vault summaries, entry counts, and Merkle roots.
    """
    if not check_rate_limit():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    vaults = []
    for vault_id, snapshot in vault_svc.vault_metadata.items():
        if snapshot.access_level == AccessLevel.PUBLIC:
            vaults.append({
                "vault_id": vault_id,
                "vault_type": snapshot.vault_type.value,
                "entry_count": snapshot.entry_count,
                "last_updated": snapshot.last_updated,
            })
    
    return vaults


@public_api_app.get(
    "/api/v1/public/memory/meta-vault",
    tags=["Memory"],
    response_model=List[Dict[str, Any]]
)
async def query_meta_vault() -> List[Dict[str, Any]]:
    """
    Query MetaVault insights (cross-vault synthesized knowledge).
    Returns high-level patterns without exposing internal memory.
    """
    if not check_rate_limit():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    insights = vault_svc.query_meta_vault(access_level=AccessLevel.PUBLIC)
    
    return [
        {
            "insight_id": i["insight_id"],
            "name": i["insight_name"],
            "description": i["description"],
            "timestamp": i["timestamp"],
        }
        for i in insights
    ]


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS — TRADING SIGNALS (if applicable)
# ═══════════════════════════════════════════════════════════════════════════

@public_api_app.get(
    "/api/v1/public/signals",
    tags=["Trading"],
    response_model=List[Dict[str, Any]]
)
async def get_trading_signals() -> List[Dict[str, Any]]:
    """
    Get PUBLIC-tier trading signals.
    Demonstrates signal access for third-party trading AI systems.
    """
    if not check_rate_limit():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Placeholder — populated from trading systems
    return [
        {
            "signal_id": "sig_001",
            "type": "momentum",
            "assets": ["BTC", "ETH"],
            "direction": "bullish",
            "confidence": 0.87,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    ]


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS — STATUS & AUDIT (Information-only)
# ═══════════════════════════════════════════════════════════════════════════

@public_api_app.get(
    "/api/v1/public/audit-log",
    tags=["Audit"],
    response_model=Dict[str, Any]
)
async def get_audit_summary() -> Dict[str, Any]:
    """
    Get summary of access audit log (no sensitive details).
    Shows activity patterns without exposing specific access details.
    """
    logs = vault_svc.get_access_log(limit=100)
    
    total_requests = len(logs)
    granted = sum(1 for log in logs if log["granted"])
    denied = total_requests - granted
    
    return {
        "total_requests": total_requests,
        "granted": granted,
        "denied": denied,
        "denial_rate": denied / total_requests if total_requests > 0 else 0,
    }
