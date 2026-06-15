"""
Comprehensive test suite for Expanded Memory Vault Service.
Tests MetaVault tier, policy-gated access control, and audit logging.
"""

import pytest
from parralax.expanded_vault import (
    ExpandedMemoryVault,
    MemoryEntry,
    VaultSnapshot,
    AccessAuditLog,
    AccessLevel,
    VaultType,
)


class TestAccessLevel:
    """Test AccessLevel enum."""
    
    def test_access_level_values(self):
        """Test AccessLevel enum values."""
        assert AccessLevel.SOVEREIGN_PRIVATE.value == "SOVEREIGN_PRIVATE"
        assert AccessLevel.TRUNK.value == "TRUNK"
        assert AccessLevel.PUBLIC.value == "PUBLIC"


class TestVaultType:
    """Test VaultType enum."""
    
    def test_vault_type_values(self):
        """Test all vault types."""
        vault_types = [
            VaultType.COGNITIVE,
            VaultType.OPERATIONAL,
            VaultType.MARKET_MEMORY,
            VaultType.TRADING_ARCHIVE,
            VaultType.KNOWLEDGE_GRAPH,
            VaultType.META_VAULT,
        ]
        
        assert len(vault_types) == 6
        assert VaultType.META_VAULT.value == "meta_vault"


class TestMemoryEntry:
    """Test MemoryEntry dataclass."""
    
    def test_memory_entry_creation(self):
        """Test creating a MemoryEntry."""
        entry = MemoryEntry(
            entry_id="mem_001",
            content_hash="abc123",
            content_summary="Summary of content",
            vault_type=VaultType.COGNITIVE,
            timestamp="2024-01-01T12:00:00Z",
            access_level=AccessLevel.PUBLIC,
            tags=["test", "memory"],
        )
        
        assert entry.entry_id == "mem_001"
        assert entry.access_level == AccessLevel.PUBLIC
        assert entry.vault_type == VaultType.COGNITIVE
    
    def test_memory_entry_to_dict(self):
        """Test converting MemoryEntry to dict."""
        entry = MemoryEntry(
            entry_id="mem_001",
            content_hash="abc123",
            content_summary="Summary",
            vault_type=VaultType.COGNITIVE,
            timestamp="2024-01-01T12:00:00Z",
            access_level=AccessLevel.PUBLIC,
            tags=["test"],
        )
        
        result = entry.to_dict()
        assert isinstance(result, dict)
        assert result["entry_id"] == "mem_001"
        assert result["access_level"] == "PUBLIC"
        assert result["vault_type"] == "cognitive"
    
    def test_memory_entry_with_metadata(self):
        """Test MemoryEntry with metadata."""
        metadata = {"source": "trading", "confidence": 0.95}
        entry = MemoryEntry(
            entry_id="mem_002",
            content_hash="def456",
            content_summary="Trading summary",
            vault_type=VaultType.TRADING_ARCHIVE,
            timestamp="2024-01-01T12:00:00Z",
            access_level=AccessLevel.TRUNK,
            metadata=metadata,
        )
        
        assert entry.metadata == metadata
        result = entry.to_dict()
        assert result["metadata"] == metadata


class TestVaultSnapshot:
    """Test VaultSnapshot dataclass."""
    
    def test_vault_snapshot_creation(self):
        """Test creating a VaultSnapshot."""
        snapshot = VaultSnapshot(
            vault_id="vault_001",
            vault_type=VaultType.COGNITIVE,
            entry_count=100,
            merkle_root="abc123def456",
            last_updated="2024-01-01T12:00:00Z",
            access_level=AccessLevel.PUBLIC,
        )
        
        assert snapshot.vault_id == "vault_001"
        assert snapshot.entry_count == 100
        assert snapshot.access_level == AccessLevel.PUBLIC
    
    def test_vault_snapshot_to_dict(self):
        """Test converting VaultSnapshot to dict."""
        snapshot = VaultSnapshot(
            vault_id="vault_001",
            vault_type=VaultType.COGNITIVE,
            entry_count=100,
            merkle_root="abc123",
            last_updated="2024-01-01T12:00:00Z",
            access_level=AccessLevel.PUBLIC,
        )
        
        result = snapshot.to_dict()
        assert result["vault_id"] == "vault_001"
        assert result["entry_count"] == 100
        assert result["vault_type"] == "cognitive"


class TestAccessAuditLog:
    """Test AccessAuditLog dataclass."""
    
    def test_audit_log_granted(self):
        """Test audit log for granted access."""
        log = AccessAuditLog(
            request_id="req_001",
            timestamp="2024-01-01T12:00:00Z",
            requester_id="sys_external",
            requested_vault="vault_001",
            requested_entry="mem_001",
            access_level_required=AccessLevel.PUBLIC,
            granted=True,
            reason="Access level matches PUBLIC tier",
        )
        
        assert log.granted
        assert log.requester_id == "sys_external"
    
    def test_audit_log_denied(self):
        """Test audit log for denied access."""
        log = AccessAuditLog(
            request_id="req_002",
            timestamp="2024-01-01T12:00:00Z",
            requester_id="sys_external",
            requested_vault="vault_001",
            requested_entry="mem_001",
            access_level_required=AccessLevel.SOVEREIGN_PRIVATE,
            granted=False,
            reason="SOVEREIGN_PRIVATE content not exposed to external systems",
        )
        
        assert not log.granted


class TestExpandedMemoryVault:
    """Test ExpandedMemoryVault service."""
    
    @pytest.fixture
    def vault_service(self):
        """Create a fresh vault service."""
        return ExpandedMemoryVault()
    
    def test_vault_initialization(self, vault_service):
        """Test vault service initialization."""
        assert vault_service is not None
        assert hasattr(vault_service, 'vaults')
        assert hasattr(vault_service, 'access_log')
    
    def test_create_vault(self, vault_service):
        """Test creating a vault."""
        vault_id = vault_service.create_vault(
            vault_id="vault_001",
            vault_type=VaultType.COGNITIVE,
            access_level=AccessLevel.TRUNK,
        )
        
        assert vault_id is not None
    
    def test_store_memory_entry(self, vault_service):
        """Test storing a memory entry in vault."""
        # Create vault
        vault_id = vault_service.create_vault(
            vault_id="vault_002",
            vault_type=VaultType.MARKET_MEMORY,
            access_level=AccessLevel.PUBLIC,
        ).vault_id
        
        # Store entry
        entry = vault_service.add_entry(
            vault_id=vault_id,
            entry_id="mem_001",
            content_hash="abc123",
            content_summary="Market memory summary",
            tags=["market", "data"],
        )
        
        assert entry is not None
        assert entry.entry_id == "mem_001"
    
    def test_query_vault_public_access(self, vault_service):
        """Test querying a PUBLIC vault."""
        # Create PUBLIC vault
        vault_snapshot = vault_service.create_vault(
            vault_id="vault_public",
            vault_type=VaultType.MARKET_MEMORY,
            access_level=AccessLevel.PUBLIC,
        )
        vault_id = vault_snapshot.vault_id
        
        # Store public entry
        vault_service.add_entry(
            vault_id=vault_id,
            entry_id="mem_public",
            content_hash="public123",
            content_summary="Public market data",
            tags=["public"],
        )
        
        # Query public entries
        results = vault_service.query_public_entries(tags=["public"])
        
        assert results is not None
    
    def test_query_vault_access_denied_sovereign_private(self, vault_service):
        """Test that EXTERNAL systems cannot access SOVEREIGN_PRIVATE."""
        # Create SOVEREIGN_PRIVATE vault
        vault_snapshot = vault_service.create_vault(
            vault_id="vault_private",
            vault_type=VaultType.COGNITIVE,
            access_level=AccessLevel.SOVEREIGN_PRIVATE,
        )
        vault_id = vault_snapshot.vault_id
        
        # Store private entry
        vault_service.add_entry(
            vault_id=vault_id,
            entry_id="mem_private",
            content_hash="private123",
            content_summary="Sovereign private data",
            tags=["private"],
            access_level=AccessLevel.SOVEREIGN_PRIVATE,
        )
        
        # Query as external system (should fail)
        # Use the actual API method
        _, entry, reason = vault_service.request_entry(
            vault_id=vault_id,
            entry_id="mem_private",
            requester_id="external_sys",
            requested_access_level=AccessLevel.PUBLIC,
        )
        
        # External systems should be denied SOVEREIGN_PRIVATE
        assert entry is None
    
    def test_query_vault_internal_access(self, vault_service):
        """Test that INTERNAL systems can access TRUNK tier."""
        # Create TRUNK vault
        vault_snapshot = vault_service.create_vault(
            vault_id="vault_trunk",
            vault_type=VaultType.OPERATIONAL,
            access_level=AccessLevel.TRUNK,
        )
        vault_id = vault_snapshot.vault_id
        
        # Store trunk entry
        vault_service.add_entry(
            vault_id=vault_id,
            entry_id="mem_trunk",
            content_hash="trunk123",
            content_summary="Internal trunk data",
            tags=["internal"],
            access_level=AccessLevel.TRUNK,
        )
        
        # Query as internal system (TRUNK level access)
        granted, entry, reason = vault_service.request_entry(
            vault_id=vault_id,
            entry_id="mem_trunk",
            requester_id="internal_sys",
            requested_access_level=AccessLevel.TRUNK,
        )
        
        # Internal system with TRUNK clearance can access TRUNK content
        assert entry is not None
    
    def test_get_vault_snapshot(self, vault_service):
        """Test getting a vault snapshot."""
        # Create vault
        snapshot = vault_service.create_vault(
            vault_id="vault_snapshot",
            vault_type=VaultType.KNOWLEDGE_GRAPH,
            access_level=AccessLevel.PUBLIC,
        )
        vault_id = snapshot.vault_id
        
        # Add entries
        vault_service.add_entry(
            vault_id=vault_id,
            entry_id="mem_1",
            content_hash="hash1",
            content_summary="Summary 1",
        )
        vault_service.add_entry(
            vault_id=vault_id,
            entry_id="mem_2",
            content_hash="hash2",
            content_summary="Summary 2",
        )
        
        # Get snapshot
        retrieved_snapshot = vault_service.get_vault_snapshot(vault_id)
        
        assert retrieved_snapshot is not None
        assert retrieved_snapshot.vault_id == vault_id
        assert retrieved_snapshot.entry_count == 2
    
    def test_meta_vault_aggregation(self, vault_service):
        """Test MetaVault tier for cross-vault insights."""
        # Create multiple vaults
        vault1_snap = vault_service.create_vault(
            vault_id="vault_a",
            vault_type=VaultType.MARKET_MEMORY,
            access_level=AccessLevel.PUBLIC,
        )
        vault1 = vault1_snap.vault_id
        
        vault2_snap = vault_service.create_vault(
            vault_id="vault_b",
            vault_type=VaultType.TRADING_ARCHIVE,
            access_level=AccessLevel.PUBLIC,
        )
        vault2 = vault2_snap.vault_id
        
        # Store entries
        vault_service.add_entry(
            vault_id=vault1,
            entry_id="mem_market",
            content_hash="market123",
            content_summary="Market data",
        )
        
        vault_service.add_entry(
            vault_id=vault2,
            entry_id="mem_trading",
            content_hash="trading123",
            content_summary="Trading history",
        )
        
        # Add meta vault insights
        vault_service.add_meta_vault_insight(
            insight_id="insight_1",
            insight_name="correlation",
            description="Correlation between vaults",
            source_vaults=["vault_a", "vault_b"],
            insight_data={"correlation": 0.85},
            access_level=AccessLevel.PUBLIC,
        )
        
        # Query MetaVault
        meta_results = vault_service.query_meta_vault(AccessLevel.PUBLIC)
        
        assert meta_results is not None


class TestAccessControl:
    """Test access control policy enforcement."""
    
    @pytest.fixture
    def vault_service(self):
        """Create a vault service with test data."""
        service = ExpandedMemoryVault()
        
        # Create vaults with different access levels
        for level in [AccessLevel.SOVEREIGN_PRIVATE, AccessLevel.TRUNK, AccessLevel.PUBLIC]:
            service.create_vault(
                vault_id=f"vault_{level.value}",
                vault_type=VaultType.COGNITIVE,
                access_level=level,
            )
        
        return service
    
    def test_policy_gating_public_to_external(self, vault_service):
        """Test PUBLIC content is accessible to EXTERNAL systems."""
        vault_id = f"vault_{AccessLevel.PUBLIC.value}"
        
        # Add PUBLIC entry
        vault_service.add_entry(
            vault_id=vault_id,
            entry_id="mem_public",
            content_hash="hash_pub",
            content_summary="Public data",
            access_level=AccessLevel.PUBLIC,
        )
        
        # External system with PUBLIC clearance can access PUBLIC content
        granted, entry, reason = vault_service.request_entry(
            vault_id=vault_id,
            entry_id="mem_public",
            requester_id="external_sys",
            requested_access_level=AccessLevel.PUBLIC,
        )
        
        assert entry is not None
    
    def test_policy_gating_trunk_from_external_denied(self, vault_service):
        """Test TRUNK content is NOT accessible to EXTERNAL systems."""
        vault_id = f"vault_{AccessLevel.TRUNK.value}"
        
        # Add TRUNK entry
        vault_service.add_entry(
            vault_id=vault_id,
            entry_id="mem_trunk",
            content_hash="hash_trunk",
            content_summary="Internal trunk data",
            access_level=AccessLevel.TRUNK,
        )
        
        # External system with PUBLIC clearance cannot access TRUNK content
        granted, entry, reason = vault_service.request_entry(
            vault_id=vault_id,
            entry_id="mem_trunk",
            requester_id="external_sys",
            requested_access_level=AccessLevel.PUBLIC,
        )
        
        # Should be denied
        assert entry is None
    
    def test_policy_gating_sovereign_from_external_denied(self, vault_service):
        """Test SOVEREIGN_PRIVATE never exposed to external."""
        vault_id = f"vault_{AccessLevel.SOVEREIGN_PRIVATE.value}"
        
        # Add SOVEREIGN_PRIVATE entry
        vault_service.add_entry(
            vault_id=vault_id,
            entry_id="mem_private",
            content_hash="hash_priv",
            content_summary="Sovereign private",
            access_level=AccessLevel.SOVEREIGN_PRIVATE,
        )
        
        # External system cannot access SOVEREIGN_PRIVATE
        granted, entry, reason = vault_service.request_entry(
            vault_id=vault_id,
            entry_id="mem_private",
            requester_id="external_sys",
            requested_access_level=AccessLevel.PUBLIC,
        )
        
        # Should definitely be denied
        assert entry is None


class TestAuditTrail:
    """Test access audit logging."""
    
    @pytest.fixture
    def vault_service(self):
        """Create a vault service with audit logging."""
        service = ExpandedMemoryVault()
        
        # Create a PUBLIC vault
        service.create_vault(
            vault_id="vault_audit",
            vault_type=VaultType.MARKET_MEMORY,
            access_level=AccessLevel.PUBLIC,
        )
        
        return service
    
    def test_audit_log_on_access(self, vault_service):
        """Test that access is logged in audit trail."""
        vault_id = "vault_audit"
        
        # Add entry
        vault_service.add_entry(
            vault_id=vault_id,
            entry_id="mem_001",
            content_hash="hash123",
            content_summary="Data",
            access_level=AccessLevel.PUBLIC,
        )
        
        # Perform access
        vault_service.request_entry(
            vault_id=vault_id,
            entry_id="mem_001",
            requester_id="external_sys",
            requested_access_level=AccessLevel.PUBLIC,
        )
        
        # Check audit logs
        audit_logs = vault_service.access_log
        assert len(audit_logs) > 0
    
    def test_audit_log_contains_requester(self, vault_service):
        """Test that audit logs contain requester information."""
        vault_id = "vault_audit"
        
        vault_service.add_entry(
            vault_id=vault_id,
            entry_id="mem_001",
            content_hash="hash123",
            content_summary="Data",
            access_level=AccessLevel.PUBLIC,
        )
        
        vault_service.request_entry(
            vault_id=vault_id,
            entry_id="mem_001",
            requester_id="specific_external",
            requested_access_level=AccessLevel.PUBLIC,
        )
        
        logs = vault_service.access_log
        if logs:
            latest_log = logs[-1]
            if isinstance(latest_log, AccessAuditLog):
                assert latest_log.requester_id is not None
            else:
                assert "requester" in latest_log


class TestMemoryHash:
    """Test that raw memory is never exposed."""
    
    @pytest.fixture
    def vault_service(self):
        """Create a vault service."""
        return ExpandedMemoryVault()
    
    def test_memory_entry_no_raw_content(self):
        """Test that MemoryEntry stores hash, not raw content."""
        entry = MemoryEntry(
            entry_id="mem_001",
            content_hash="abc123",  # Hash, not raw content
            content_summary="Summary only",  # Summary for safety
            vault_type=VaultType.COGNITIVE,
            timestamp="2024-01-01T12:00:00Z",
            access_level=AccessLevel.PUBLIC,
        )
        
        # Verify no raw content attribute
        assert not hasattr(entry, 'raw_content')
        # Verify hash is stored
        assert entry.content_hash == "abc123"
    
    def test_snapshot_no_raw_content(self):
        """Test that VaultSnapshot doesn't expose raw memory."""
        snapshot = VaultSnapshot(
            vault_id="vault_001",
            vault_type=VaultType.COGNITIVE,
            entry_count=100,
            merkle_root="root123",
            last_updated="2024-01-01T12:00:00Z",
            access_level=AccessLevel.PUBLIC,
        )
        
        # Verify no raw content in snapshot
        assert not hasattr(snapshot, 'entries')
        # Only metadata is exposed
        assert hasattr(snapshot, 'merkle_root')
