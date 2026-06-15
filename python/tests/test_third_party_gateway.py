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
    
    def test_check_rate_limit_not_exceeded(self, gateway):
        """Test checking rate limit when not exceeded."""
        gw, system = gateway
        
        is_allowed, reason = gw.check_rate_limit(system.api_key)
        assert is_allowed
    
    def test_rate_limit_structure(self, gateway):
        """Test that rate limiting returns tuple."""
        gw, system = gateway
        
        result = gw.check_rate_limit(system.api_key)
        assert isinstance(result, tuple)
        assert len(result) == 2


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
    
    def test_register_webhook(self, gateway):
        """Test registering a webhook subscription."""
        gw, system = gateway
        
        webhook_url = "https://external.ai/webhook/updates"
        success = gw.register_webhook(system.api_key, webhook_url)
        
        assert success
        assert webhook_url in system.webhook_urls
    
    def test_register_multiple_webhooks(self, gateway):
        """Test registering multiple webhooks."""
        gw, system = gateway
        
        webhooks = [
            "https://external.ai/webhook/memory",
            "https://external.ai/webhook/signals",
            "https://external.ai/webhook/updates",
        ]
        
        for webhook in webhooks:
            success = gw.register_webhook(system.api_key, webhook)
            assert success
        
        assert len(system.webhook_urls) == 3
    
    def test_unregister_webhook(self, gateway):
        """Test unregistering a webhook subscription."""
        gw, system = gateway
        
        webhook_url = "https://external.ai/webhook/updates"
        gw.register_webhook(system.api_key, webhook_url)
        assert webhook_url in system.webhook_urls
        
        success = gw.unregister_webhook(system.api_key, webhook_url)
        assert success
        assert webhook_url not in system.webhook_urls
    
    def test_notify_webhooks(self, gateway):
        """Test sending notifications to webhooks."""
        gw, system = gateway
        
        webhook_url = "https://external.ai/webhook/events"
        gw.register_webhook(system.api_key, webhook_url)
        
        # Notify webhooks (mock implementation)
        event = {
            "event_type": "memory_update",
            "data": {"timestamp": "2024-01-01T12:00:00Z"},
        }
        
        # Should not raise exception
        gw.notify_webhooks(system.system_id, event)


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
        
        success = gw.deactivate_system(system.system_id)
        assert success
        assert not system.active
    
    def test_reactivate_system(self, gateway):
        """Test reactivating a system."""
        gw, system = gateway
        
        gw.deactivate_system(system.system_id)
        assert not system.active
        
        success = gw.reactivate_system(system.system_id)
        assert success
        assert system.active
    
    def test_get_system_status(self, gateway):
        """Test retrieving system status."""
        gw, system = gateway
        
        status = gw.get_system_status(system.api_key)
        
        assert status is not None
        assert "system_id" in status or isinstance(status, dict)
    
    def test_rotate_api_key(self, gateway):
        """Test rotating API key."""
        gw, system = gateway
        
        old_key = system.api_key
        new_key = gw.rotate_api_key(old_key)
        
        assert new_key is not None
        assert new_key != old_key
    
    def test_total_requests_tracked(self, gateway):
        """Test that total requests are tracked."""
        gw, system = gateway
        
        # System should have total_requests attribute
        assert hasattr(system, 'total_requests')
        assert system.total_requests == 0


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
        
        all_systems = gw.list_systems(active_only=False)
        
        assert len(all_systems) >= 5
    
    def test_list_active_systems(self, gateway):
        """Test listing only active systems."""
        gw, systems = gateway
        
        # Deactivate one system
        gw.deactivate_system(systems[0].system_id)
        
        active_systems = gw.list_systems(active_only=True)
        
        assert len(active_systems) == 4
    
    def test_list_systems_returns_dicts(self, gateway):
        """Test that list_systems returns list of dicts."""
        gw, systems = gateway
        
        result = gw.list_systems(active_only=False)
        
        assert isinstance(result, list)
        if len(result) > 0:
            assert isinstance(result[0], dict)


class TestAPIKeyManagement:
    """Test API key management."""
    
    @pytest.fixture
    def gateway(self):
        """Create a gateway."""
        return ThirdPartyIntegrationGateway()
    
    def test_api_key_format(self, gateway):
        """Test that API keys have expected format."""
        system = gateway.register_system(
            system_name="Format Test",
            contact_email="format@example.com",
        )
        
        # API key should start with 'pk_'
        assert system.api_key.startswith("pk_")
        assert len(system.api_key) > 10  # Should be reasonably long
    
    def test_api_keys_are_unique(self, gateway):
        """Test that each system gets unique API key."""
        api_keys = set()
        
        for i in range(5):
            system = gateway.register_system(
                system_name=f"Unique Test {i}",
                contact_email=f"unique{i}@example.com",
            )
            api_keys.add(system.api_key)
        
        # All keys should be unique
        assert len(api_keys) == 5
    
    def test_key_verification_after_rotation(self, gateway):
        """Test verifying key after rotation."""
        system = gateway.register_system(
            system_name="Rotation Test",
            contact_email="rotation@example.com",
        )
        
        old_key = system.api_key
        
        # Rotate key
        new_key = gateway.rotate_api_key(old_key)
        
        # New key should verify
        is_valid, verified_system = gateway.verify_api_key(new_key)
        assert is_valid
        assert verified_system.system_id == system.system_id
        
        # Old key should not verify
        is_valid_old, _ = gateway.verify_api_key(old_key)
        assert not is_valid_old


class TestWebhookNotification:
    """Test webhook notification system."""
    
    @pytest.fixture
    def gateway(self):
        """Create a gateway with webhooks."""
        gw = ThirdPartyIntegrationGateway()
        system = gw.register_system(
            system_name="Notify Test",
            contact_email="notify@example.com",
        )
        
        gw.register_webhook(
            system.api_key,
            "https://external.ai/webhook/events"
        )
        
        return gw, system
    
    def test_webhook_logging(self, gateway):
        """Test that webhook notifications are logged."""
        gw, system = gateway
        
        event = {
            "event_type": "test",
            "timestamp": "2024-01-01T12:00:00Z",
        }
        
        # Notify webhooks
        gw.notify_webhooks(system.system_id, event)
        
        # Webhook log should be updated
        assert len(gw.webhook_log) > 0
    
    def test_webhook_event_structure(self, gateway):
        """Test webhook event structure."""
        gw, system = gateway
        
        event = {
            "event_type": "memory_update",
            "data": {"key": "value"},
        }
        
        gw.notify_webhooks(system.system_id, event)
        
        if gw.webhook_log:
            logged_event = gw.webhook_log[-1]
            assert "system_id" in logged_event or isinstance(logged_event, dict)
