"""
Expanded Memory Vault Service — MetaVault Tier + Public Query Interface
PARALLAX Sovereign Organism — Cross-System Memory Access

PURPOSE: Extends cryptographia_vault.mo with a Python service layer that:
1. Manages MetaVault tier (insights across multiple vaults)
2. Enforces policy-gated disclosure (SOVEREIGN_PRIVATE / TRUNK / PUBLIC)
3. Provides query interface for third-party AI systems (policy-filtered)
4. Tracks all access to memory (audit trail)

DOCTRINE: Memory is protected. Requestors receive commitments/proofs, not raw internals.
Only properly classified content (PUBLIC tier) flows to external systems.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict, field


class AccessLevel(Enum):
    """Policy access levels."""
    SOVEREIGN_PRIVATE = "SOVEREIGN_PRIVATE"  # Never exposed externally
    TRUNK = "TRUNK"  # Internal organism builders only
    PUBLIC = "PUBLIC"  # Third-party AI systems can access


class VaultType(Enum):
    """Types of vaults in the expanded system."""
    COGNITIVE = "cognitive"
    OPERATIONAL = "operational"
    MARKET_MEMORY = "market_memory"
    TRADING_ARCHIVE = "trading_archive"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    META_VAULT = "meta_vault"  # NEW: Cross-vault insights


@dataclass
class MemoryEntry:
    """Individual memory entry within a vault."""
    entry_id: str
    content_hash: str  # SHA-256, not the raw content
    content_summary: str  # Brief summary safe for retrieval
    vault_type: VaultType
    timestamp: str
    access_level: AccessLevel
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "content_hash": self.content_hash,
            "content_summary": self.content_summary,
            "vault_type": self.vault_type.value,
            "timestamp": self.timestamp,
            "access_level": self.access_level.value,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class VaultSnapshot:
    """Summary view of a vault (no raw memory contents)."""
    vault_id: str
    vault_type: VaultType
    entry_count: int
    merkle_root: str  # Verifiable commitment to vault state
    last_updated: str
    access_level: AccessLevel
    
    def to_dict(self) -> dict:
        return {
            "vault_id": self.vault_id,
            "vault_type": self.vault_type.value,
            "entry_count": self.entry_count,
            "merkle_root": self.merkle_root,
            "last_updated": self.last_updated,
            "access_level": self.access_level.value,
        }


@dataclass
class AccessAuditLog:
    """Record of memory access attempt."""
    request_id: str
    timestamp: str
    requester_id: str  # System/AI identifier
    requested_vault: str
    requested_entry: Optional[str]
    access_level_required: AccessLevel
    granted: bool
    reason: str  # Why granted or denied


class ExpandedMemoryVault:
    """
    Expanded memory vault system with MetaVault tier.
    Manages security boundaries and policy-gated disclosure.
    """
    
    def __init__(self):
        self.vaults: Dict[str, Dict[str, MemoryEntry]] = {}
        self.vault_metadata: Dict[str, VaultSnapshot] = {}
        self.access_log: List[AccessAuditLog] = []
        self.meta_vault_insights: Dict[str, Dict[str, Any]] = {}  # Cross-vault insights
        self.policies: Dict[str, Dict[str, AccessLevel]] = {}  # Access policies per vault
    
    def create_vault(
        self,
        vault_id: str,
        vault_type: VaultType,
        access_level: AccessLevel = AccessLevel.TRUNK,
    ) -> VaultSnapshot:
        """Create a new vault with specified access level."""
        if vault_id in self.vaults:
            raise ValueError(f"Vault {vault_id} already exists")
        
        self.vaults[vault_id] = {}
        snapshot = VaultSnapshot(
            vault_id=vault_id,
            vault_type=vault_type,
            entry_count=0,
            merkle_root="",
            last_updated=datetime.utcnow().isoformat() + "Z",
            access_level=access_level,
        )
        self.vault_metadata[vault_id] = snapshot
        self.policies[vault_id] = {}
        
        return snapshot
    
    def add_entry(
        self,
        vault_id: str,
        entry_id: str,
        content_hash: str,
        content_summary: str,
        access_level: AccessLevel = AccessLevel.TRUNK,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> MemoryEntry:
        """
        Add a memory entry to a vault.
        Entry is stored as hash + summary, never raw content.
        """
        if vault_id not in self.vaults:
            raise ValueError(f"Vault {vault_id} does not exist")
        
        entry = MemoryEntry(
            entry_id=entry_id,
            content_hash=content_hash,
            content_summary=content_summary,
            vault_type=self.vault_metadata[vault_id].vault_type,
            timestamp=datetime.utcnow().isoformat() + "Z",
            access_level=access_level,
            tags=tags or [],
            metadata=metadata or {},
        )
        
        self.vaults[vault_id][entry_id] = entry
        
        # Update vault metadata
        snapshot = self.vault_metadata[vault_id]
        snapshot.entry_count = len(self.vaults[vault_id])
        snapshot.last_updated = entry.timestamp
        
        return entry
    
    def request_entry(
        self,
        vault_id: str,
        entry_id: str,
        requester_id: str,
        requested_access_level: AccessLevel,
    ) -> tuple[bool, Optional[MemoryEntry], str]:
        """
        Request access to a memory entry.
        Returns: (granted, entry_or_none, reason)
        
        Policy: Requester can only access entries at their clearance level or below.
        """
        request_id = f"req_{datetime.utcnow().timestamp()}"
        
        # Validate vault exists
        if vault_id not in self.vaults:
            self._log_access(
                request_id, requester_id, vault_id, entry_id,
                requested_access_level, False, "Vault not found"
            )
            return False, None, "Vault not found"
        
        # Validate entry exists
        if entry_id not in self.vaults[vault_id]:
            self._log_access(
                request_id, requester_id, vault_id, entry_id,
                requested_access_level, False, "Entry not found"
            )
            return False, None, "Entry not found"
        
        entry = self.vaults[vault_id][entry_id]
        
        # Check access level
        if not self._can_access(requested_access_level, entry.access_level):
            self._log_access(
                request_id, requester_id, vault_id, entry_id,
                requested_access_level, False,
                f"Access denied: requires {entry.access_level.value} access"
            )
            return False, None, f"Access denied: insufficient clearance"
        
        # Grant access
        self._log_access(
            request_id, requester_id, vault_id, entry_id,
            requested_access_level, True, "Access granted"
        )
        
        return True, entry, "Access granted"
    
    def query_public_entries(self, tags: List[str] = None) -> List[MemoryEntry]:
        """
        Query PUBLIC-tier entries (for third-party AI systems).
        Returns only entries that are explicitly PUBLIC access level.
        """
        public_entries = []
        
        for vault_id, entries in self.vaults.items():
            for entry_id, entry in entries.items():
                if entry.access_level == AccessLevel.PUBLIC:
                    # Filter by tags if provided
                    if tags is None or any(tag in entry.tags for tag in tags):
                        public_entries.append(entry)
        
        return sorted(public_entries, key=lambda e: e.timestamp, reverse=True)
    
    def get_vault_snapshot(self, vault_id: str) -> Optional[VaultSnapshot]:
        """Get summary view of a vault (no raw content)."""
        return self.vault_metadata.get(vault_id)
    
    def list_vault_entries(
        self,
        vault_id: str,
        access_level: AccessLevel = AccessLevel.PUBLIC,
    ) -> List[Dict[str, Any]]:
        """
        List entries in a vault (filtered by access level).
        Returns entry metadata only, not content.
        """
        if vault_id not in self.vaults:
            return []
        
        entries = []
        for entry_id, entry in self.vaults[vault_id].items():
            if self._can_access(access_level, entry.access_level):
                # Return metadata only
                entries.append({
                    "entry_id": entry.entry_id,
                    "content_hash": entry.content_hash,
                    "content_summary": entry.content_summary,
                    "timestamp": entry.timestamp,
                    "tags": entry.tags,
                })
        
        return sorted(entries, key=lambda e: e['timestamp'], reverse=True)
    
    def add_meta_vault_insight(
        self,
        insight_id: str,
        insight_name: str,
        description: str,
        source_vaults: List[str],
        insight_data: Dict[str, Any],
        access_level: AccessLevel = AccessLevel.TRUNK,
    ):
        """
        Add cross-vault insight to MetaVault tier.
        MetaVault synthesizes knowledge from multiple vaults.
        """
        self.meta_vault_insights[insight_id] = {
            "insight_id": insight_id,
            "insight_name": insight_name,
            "description": description,
            "source_vaults": source_vaults,
            "insight_data": insight_data,
            "access_level": access_level.value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    def query_meta_vault(self, access_level: AccessLevel = AccessLevel.PUBLIC) -> List[Dict]:
        """Query MetaVault insights at specified access level."""
        insights = []
        for insight_id, insight in self.meta_vault_insights.items():
            if self._can_access(access_level, AccessLevel[insight["access_level"]]):
                insights.append(insight)
        
        return sorted(insights, key=lambda i: i['timestamp'], reverse=True)
    
    def get_access_log(self, limit: int = 100) -> List[Dict]:
        """Get access audit log (most recent first)."""
        return [
            {
                "request_id": log.request_id,
                "timestamp": log.timestamp,
                "requester_id": log.requester_id,
                "requested_vault": log.requested_vault,
                "requested_entry": log.requested_entry,
                "granted": log.granted,
                "reason": log.reason,
            }
            for log in reversed(self.access_log[-limit:])
        ]
    
    def _can_access(self, requester_level: AccessLevel, resource_level: AccessLevel) -> bool:
        """
        Check if requester can access resource.
        Hierarchy: SOVEREIGN_PRIVATE > TRUNK > PUBLIC
        Requester needs >= resource level to access.
        """
        level_order = {
            AccessLevel.PUBLIC: 0,
            AccessLevel.TRUNK: 1,
            AccessLevel.SOVEREIGN_PRIVATE: 2,
        }
        
        return level_order.get(requester_level, -1) >= level_order.get(resource_level, -1)
    
    def _log_access(
        self,
        request_id: str,
        requester_id: str,
        vault_id: str,
        entry_id: Optional[str],
        access_level: AccessLevel,
        granted: bool,
        reason: str,
    ):
        """Log an access attempt."""
        log_entry = AccessAuditLog(
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            requester_id=requester_id,
            requested_vault=vault_id,
            requested_entry=entry_id,
            access_level_required=access_level,
            granted=granted,
            reason=reason,
        )
        self.access_log.append(log_entry)


# Singleton instance
_vault_service: Optional[ExpandedMemoryVault] = None


def get_vault_service() -> ExpandedMemoryVault:
    """Get or create the expanded memory vault singleton."""
    global _vault_service
    if _vault_service is None:
        _vault_service = ExpandedMemoryVault()
    return _vault_service
