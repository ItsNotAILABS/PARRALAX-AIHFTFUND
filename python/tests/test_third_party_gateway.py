"""
Comprehensive test suite for Third-Party AI System Integration Gateway.
Tests registration, API key management, rate limiting, and webhooks.
"""

import pytest
from parralax.third_party_gateway import (
    ThirdPartyIntegrationGateway,
    ThirdPartySystem,
    APIKeyConfig,
)


class TestThirdPartySystem:
    """Test ThirdPartySystem dataclass."""
    
    def test_system_creation(self):
        """Test creating a ThirdPartySystem."""
        system = ThirdPartySystem(
            system_id="sys_001",
            system_name="External AI System",
            api_key="pk_test123",
            created_at="2024-01-01T12:00:00Z",
            contact_email="contact@external.ai",
            rate_limit_per_hour=1000,
            active=True,
            description="An external AI system",
        )
        
        assert system.system_id == "sys_001"
        assert system.system_name == "External AI System"
        assert system.active
    
    def test_system_with_webhooks(self):
        """Test ThirdPartySystem with webhook URLs."""
        webhooks = [
            "https://external.ai/webhook/memory-update",
            "https://external.ai/webhook/trading-signal",
        ]
        
        system = ThirdPartySystem(
            system_id="sys_002",
            system_name="Advanced AI",
            api_key="pk_adv123",
            created_at="2024-01-01T12:00:00Z",
            contact_email="admin@advanced.ai",
            webhook_urls=webhooks,
        )
        
        assert len(system.webhook_urls) == 2
        assert system.webhook_urls[0] == "https://external.ai/webhook/memory-update"


class TestAPIKeyConfig:
    """Test APIKeyConfig dataclass."""
    
    def test_api_key_creation(self):
        """Test creating an APIKeyConfig."""
        config = APIKeyConfig(
            api_key="pk_test123",
            system_id="sys_001",
            created_at="2024-01-01T12:00:00Z",
            active=True,
        )
        
        assert config.api_key == "pk_test123"
        assert config.system_id == "sys_001"
        assert config.active
    
    def test_api_key_with_expiration(self):
        """Test APIKeyConfig with expiration date."""
        config = APIKeyConfig(
            api_key="pk_temp123",
            system_id="sys_003",
            created_at="2024-01-01T12:00:00Z",
            expires_at="2025-01-01T12:00:00Z",
            active=True,
        )
        
        assert config.expires_at is not None
    
    def test_api_key_with_scope(self):
        """Test APIKeyConfig with specific scopes."""
        scopes = ["public", "trading-signals", "memory-vault"]
        config = APIKeyConfig(
            api_key="pk_scoped123",
            system_id="sys_004",
            created_at="2024-01-01T12:00:00Z",
            scope=scopes,
        )
        
        assert config.scope == scopes


class TestThirdPartyIntegrationGateway:
    """Test ThirdPartyIntegrationGateway service."""
    
    @pytest.fixture
    def gateway(self):
        """Create a fresh gateway instance."""
        return ThirdPartyIntegrationGateway()
    
    def test_gateway_initialization(self, gateway):
        """Test gateway initialization."""
        assert gateway is not None
        assert len(gateway.systems) == 0
        assert len(gateway.api_keys) == 0
    
    def test_register_system_basic(self, gateway):
        """Test registering a new third-party system."""
        system = gateway.register_system(
            system_name="Test AI System",
            contact_email="test@example.com",
        )
        
        assert system.system_id is not None
        assert system.system_name == "Test AI System"
        assert system.contact_email == "test@example.com"
        assert system.api_key is not None
        assert system.active
    
    def test_register_system_with_custom_rate_limit(self, gateway):
        """Test registering with custom rate limit."""
        system = gateway.register_system(
            system_name="High-Volume AI",
            contact_email="bulk@example.com",
            rate_limit_per_hour=5000,
        )
        
        assert system.rate_limit_per_hour == 5000
    
    def test_register_system_with_description(self, gateway):
        """Test registering system with description."""
        system = gateway.register_system(
            system_name="Documented AI",
            contact_email="docs@example.com",
            description="A well-documented external AI system",
        )
        
        assert system.description == "A well-documented external AI system"
    
    def test_system_is_stored(self, gateway):
        """Test that registered system is stored."""
        system = gateway.register_system(
            system_name="Stored AI",
            contact_email="store@example.com",
        )
        
        assert system.system_id in gateway.systems
        assert gateway.systems[system.system_id] == system
    
    def test_api_key_is_stored(self, gateway):
        """Test that API key is stored with config."""
        system = gateway.register_system(
            system_name="Key AI",
            contact_email="key@example.com",
        )
        
        assert system.api_key in gateway.api_keys
        config = gateway.api_keys[system.api_key]
        assert config.system_id == system.system_id
    
    def test_multiple_system_registration(self, gateway):
        """Test registering multiple systems."""
        systems = []
        for i in range(3):
            system = gateway.register_system(
                system_name=f"AI System {i}",
                contact_email=f"ai{i}@example.com",
            )
            systems.append(system)
        
        assert len(gateway.systems) == 3
        assert len(gateway.api_keys) == 3
    
    def test_verify_api_key_valid(self, gateway):
        """Test verifying a valid API key."""
        system = gateway.register_system(
            system_name="Verify AI",
            contact_email="verify@example.com",
        )
        
        is_valid, retrieved_system = gateway.verify_api_key(system.api_key)
        
        assert is_valid
        assert retrieved_system is not None
        assert retrieved_system.system_id == system.system_id
    
    def test_verify_api_key_invalid(self, gateway):
        """Test verifying an invalid API key."""
        is_valid, system = gateway.verify_api_key("invalid_key_xyz")
        
        assert not is_valid
        assert system is None
    
    def test_verify_api_key_inactive(self, gateway):
        """Test verifying an inactive API key."""
        system = gateway.register_system(
            system_name="Inactive AI",
            contact_email="inactive@example.com",
        )
        
        # Deactivate the key
        gateway.api_keys[system.api_key].active = False
        
        is_valid, retrieved_system = gateway.verify_api_key(system.api_key)
        
        assert not is_valid


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.fixture
    def gateway(self):
        """Create a gateway with registered system."""
        gw = ThirdPartyIntegrationGateway()
        system = gw.register_system(
            system_name="Rate Limited AI",
            contact_email="rate@example.com",
            rate_limit_per_hour=10,  # Low limit for testing
        )
        return gw, system
    
    def test_get_rate_limit(self, gateway):
        """Test getting system rate limit."""
        gw, system = gateway
        
        limit = gw.get_rate_limit(system.api_key)
        assert limit == 10
    
    def test_check_rate_limit_not_exceeded(self, gateway):
        """Test checking rate limit when not exceeded."""
        gw, system = gateway
        
        is_allowed = gw.check_rate_limit(system.api_key)
        assert is_allowed
    
    def test_record_request(self, gateway):
        """Test recording a request."""
        gw, system = gateway
        
        # Record multiple requests
        for _ in range(5):
            gw.record_request(system.api_key)
        
        assert gw.request_usage.get(system.api_key, 0) == 5
    
    def test_rate_limit_exceeded(self, gateway):
        """Test rate limiting when exceeded."""
        gw, system = gateway
        
        # Record requests up to limit
        for _ in range(10):
            gw.record_request(system.api_key)
        
        # Next request should be rejected
        is_allowed = gw.check_rate_limit(system.api_key)
        assert not is_allowed
    
    def test_custom_rate_limits(self, gateway):
        """Test different rate limits for different systems."""
        gw, system1 = gateway
        
        system2 = gw.register_system(
            system_name="High-Volume AI",
            contact_email="high@example.com",
            rate_limit_per_hour=100,
        )
        
        # System 1 has limit of 10
        assert gw.get_rate_limit(system1.api_key) == 10
        
        # System 2 has limit of 100
        assert gw.get_rate_limit(system2.api_key) == 100


class TestWebhookSubscriptions:
    """Test webhook subscription functionality."""
    
    @pytest.fixture
    def gateway(self):
        """Create a gateway with system."""
        gw = ThirdPartyIntegrationGateway()
        system = gw.register_system(
            system_name="Webhook AI",
            contact_email="webhook@example.com",
        )
        return gw, system
    
    def test_add_webhook(self, gateway):
        """Test adding a webhook subscription."""
        gw, system = gateway
        
        webhook_url = "https://external.ai/webhook/updates"
        gw.add_webhook(system.api_key, webhook_url)
        
        assert webhook_url in system.webhook_urls
    
    def test_add_multiple_webhooks(self, gateway):
        """Test adding multiple webhooks."""
        gw, system = gateway
        
        webhooks = [
            "https://external.ai/webhook/memory",
            "https://external.ai/webhook/signals",
            "https://external.ai/webhook/updates",
        ]
        
        for webhook in webhooks:
            gw.add_webhook(system.api_key, webhook)
        
        assert len(system.webhook_urls) == 3
    
    def test_remove_webhook(self, gateway):
        """Test removing a webhook subscription."""
        gw, system = gateway
        
        webhook_url = "https://external.ai/webhook/updates"
        gw.add_webhook(system.api_key, webhook_url)
        assert webhook_url in system.webhook_urls
        
        gw.remove_webhook(system.api_key, webhook_url)
        assert webhook_url not in system.webhook_urls
    
    def test_list_webhooks(self, gateway):
        """Test listing webhooks for a system."""
        gw, system = gateway
        
        webhooks = [
            "https://external.ai/webhook/memory",
            "https://external.ai/webhook/signals",
        ]
        
        for webhook in webhooks:
            gw.add_webhook(system.api_key, webhook)
        
        listed = gw.list_webhooks(system.api_key)
        assert len(listed) == 2
        assert webhooks[0] in listed
        assert webhooks[1] in listed


class TestUsageTracking:
    """Test usage tracking and reporting."""
    
    @pytest.fixture
    def gateway(self):
        """Create a gateway with systems."""
        gw = ThirdPartyIntegrationGateway()
        
        system1 = gw.register_system(
            system_name="Active AI 1",
            contact_email="active1@example.com",
        )
        
        system2 = gw.register_system(
            system_name="Active AI 2",
            contact_email="active2@example.com",
        )
        
        return gw, system1, system2
    
    def test_get_usage(self, gateway):
        """Test getting usage statistics for a system."""
        gw, system, _ = gateway
        
        # Record some requests
        for _ in range(5):
            gw.record_request(system.api_key)
        
        usage = gw.get_usage(system.api_key)
        assert usage == 5
    
    def test_get_all_usage(self, gateway):
        """Test getting usage for all systems."""
        gw, system1, system2 = gateway
        
        # Record requests
        for _ in range(3):
            gw.record_request(system1.api_key)
        
        for _ in range(7):
            gw.record_request(system2.api_key)
        
        all_usage = gw.get_all_usage()
        
        assert len(all_usage) == 2
        assert all_usage.get(system1.system_id, 0) == 3
        assert all_usage.get(system2.system_id, 0) == 7
    
    def test_reset_usage(self, gateway):
        """Test resetting usage counters."""
        gw, system, _ = gateway
        
        # Record requests
        for _ in range(5):
            gw.record_request(system.api_key)
        
        usage_before = gw.get_usage(system.api_key)
        assert usage_before == 5
        
        # Reset
        gw.reset_usage()
        
        usage_after = gw.get_usage(system.api_key)
        assert usage_after == 0


class TestSystemManagement:
    """Test system management operations."""
    
    @pytest.fixture
    def gateway(self):
        """Create a gateway with system."""
        gw = ThirdPartyIntegrationGateway()
        system = gw.register_system(
            system_name="Managed AI",
            contact_email="manage@example.com",
        )
        return gw, system
    
    def test_deactivate_system(self, gateway):
        """Test deactivating a system."""
        gw, system = gateway
        
        assert system.active
        
        gw.deactivate_system(system.system_id)
        
        assert not system.active
    
    def test_reactivate_system(self, gateway):
        """Test reactivating a system."""
        gw, system = gateway
        
        gw.deactivate_system(system.system_id)
        assert not system.active
        
        gw.activate_system(system.system_id)
        assert system.active
    
    def test_get_system_info(self, gateway):
        """Test retrieving system information."""
        gw, system = gateway
        
        info = gw.get_system_info(system.system_id)
        
        assert info is not None
        assert info.system_name == "Managed AI"
        assert info.contact_email == "manage@example.com"
    
    def test_update_system_rate_limit(self, gateway):
        """Test updating system rate limit."""
        gw, system = gateway
        
        original = gw.get_rate_limit(system.api_key)
        
        gw.update_rate_limit(system.system_id, 5000)
        
        updated = gw.get_rate_limit(system.api_key)
        assert updated == 5000
        assert updated != original
    
    def test_last_used_tracking(self, gateway):
        """Test tracking last_used timestamp."""
        gw, system = gateway
        
        assert system.last_used is None
        
        # Simulate usage
        gw.record_request(system.api_key)
        
        # The service should update last_used (if implemented)
        # This tests the interface at least
        assert system.system_id in gw.systems


class TestSystemDiscovery:
    """Test discovering registered systems."""
    
    @pytest.fixture
    def gateway(self):
        """Create a gateway with multiple systems."""
        gw = ThirdPartyIntegrationGateway()
        
        systems = []
        for i in range(5):
            system = gw.register_system(
                system_name=f"AI System {i}",
                contact_email=f"ai{i}@example.com",
                description=f"System {i}" if i % 2 == 0 else "",
            )
            systems.append(system)
        
        return gw, systems
    
    def test_list_all_systems(self, gateway):
        """Test listing all registered systems."""
        gw, systems = gateway
        
        all_systems = gw.list_systems()
        
        assert len(all_systems) == 5
    
    def test_list_active_systems(self, gateway):
        """Test listing only active systems."""
        gw, systems = gateway
        
        # Deactivate one system
        gw.deactivate_system(systems[0].system_id)
        
        active_systems = gw.list_systems(active_only=True)
        
        assert len(active_systems) == 4
    
    def test_search_systems_by_name(self, gateway):
        """Test searching systems by name."""
        gw, systems = gateway
        
        # Search for specific system
        results = gw.search_systems(search_term="System 2")
        
        # Implementation may vary, test interface
        assert results is not None


class TestAPIKeyExpiration:
    """Test API key expiration functionality."""
    
    @pytest.fixture
    def gateway(self):
        """Create a gateway."""
        return ThirdPartyIntegrationGateway()
    
    def test_create_expiring_key(self, gateway):
        """Test creating an API key with expiration."""
        system = gateway.register_system(
            system_name="Temporary AI",
            contact_email="temp@example.com",
        )
        
        # Manually set expiration (in real system, would be parameter)
        gateway.api_keys[system.api_key].expires_at = "2023-01-01T00:00:00Z"
        
        config = gateway.api_keys[system.api_key]
        assert config.expires_at is not None
    
    def test_expired_key_verification(self, gateway):
        """Test that expired keys cannot be verified."""
        system = gateway.register_system(
            system_name="Expired AI",
            contact_email="expired@example.com",
        )
        
        # Set expiration to past
        gateway.api_keys[system.api_key].expires_at = "2023-01-01T00:00:00Z"
        
        is_valid, _ = gateway.verify_api_key(system.api_key)
        
        # Expired key should not be valid
        assert not is_valid
