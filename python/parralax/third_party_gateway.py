"""
Third-Party AI System Integration & Authentication
PARALLAX Sovereign Organism — Gateway for External Systems

PURPOSE: Manages third-party AI system registration, API keys, rate limiting,
and webhook subscriptions for memory updates and trading signals.
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import uuid


@dataclass
class ThirdPartySystem:
    """Registered third-party AI system."""
    system_id: str
    system_name: str
    api_key: str
    created_at: str
    contact_email: str
    rate_limit_per_hour: int = 1000
    active: bool = True
    description: str = ""
    webhook_urls: List[str] = field(default_factory=list)  # For subscriptions
    last_used: Optional[str] = None
    total_requests: int = 0


@dataclass
class APIKeyConfig:
    """Configuration for API key."""
    api_key: str
    system_id: str
    created_at: str
    expires_at: Optional[str] = None  # None = no expiration
    active: bool = True
    scope: List[str] = field(default_factory=lambda: ["public"])


class ThirdPartyIntegrationGateway:
    """
    Gateway for third-party AI system integration.
    Manages registration, authentication, rate limiting, webhooks.
    """
    
    def __init__(self):
        self.systems: Dict[str, ThirdPartySystem] = {}
        self.api_keys: Dict[str, APIKeyConfig] = {}
        self.webhook_log: List[Dict] = []  # Events sent to webhooks
        self.request_usage: Dict[str, int] = {}  # Tracks requests per hour
    
    def register_system(
        self,
        system_name: str,
        contact_email: str,
        description: str = "",
        rate_limit_per_hour: int = 1000,
    ) -> ThirdPartySystem:
        """
        Register a new third-party AI system.
        Returns API key for system to use.
        """
        system_id = f"sys_{uuid.uuid4().hex[:12]}"
        api_key = f"pk_{uuid.uuid4().hex}_{uuid.uuid4().hex}"
        
        system = ThirdPartySystem(
            system_id=system_id,
            system_name=system_name,
            api_key=api_key,
            created_at=datetime.utcnow().isoformat() + "Z",
            contact_email=contact_email,
            rate_limit_per_hour=rate_limit_per_hour,
            description=description,
        )
        
        self.systems[system_id] = system
        
        key_config = APIKeyConfig(
            api_key=api_key,
            system_id=system_id,
            created_at=datetime.utcnow().isoformat() + "Z",
        )
        self.api_keys[api_key] = key_config
        
        return system
    
    def verify_api_key(self, api_key: str) -> tuple[bool, Optional[ThirdPartySystem]]:
        """Verify API key and return system info if valid."""
        if api_key not in self.api_keys:
            return False, None
        
        key_config = self.api_keys[api_key]
        
        # Check if expired
        if key_config.expires_at:
            if datetime.fromisoformat(key_config.expires_at) < datetime.utcnow():
                return False, None
        
        # Check if active
        if not key_config.active:
            return False, None
        
        system_id = key_config.system_id
        if system_id not in self.systems:
            return False, None
        
        system = self.systems[system_id]
        if not system.active:
            return False, None
        
        return True, system
    
    def check_rate_limit(self, api_key: str) -> tuple[bool, str]:
        """
        Check if system has exceeded rate limit.
        Returns (allowed, reason)
        """
        valid, system = self.verify_api_key(api_key)
        if not valid or not system:
            return False, "Invalid API key"
        
        # Get usage for current hour
        hour_key = f"{system.system_id}_{datetime.utcnow().hour}"
        usage = self.request_usage.get(hour_key, 0)
        
        if usage >= system.rate_limit_per_hour:
            return False, f"Rate limit exceeded ({system.rate_limit_per_hour} per hour)"
        
        # Increment usage
        self.request_usage[hour_key] = usage + 1
        
        # Update system last_used
        system.last_used = datetime.utcnow().isoformat() + "Z"
        system.total_requests += 1
        
        return True, "Request allowed"
    
    def get_system_status(self, api_key: str) -> Optional[Dict]:
        """Get status and usage for a system."""
        valid, system = self.verify_api_key(api_key)
        if not valid or not system:
            return None
        
        hour_key = f"{system.system_id}_{datetime.utcnow().hour}"
        usage = self.request_usage.get(hour_key, 0)
        
        return {
            "system_id": system.system_id,
            "system_name": system.system_name,
            "active": system.active,
            "requests_this_hour": usage,
            "rate_limit": system.rate_limit_per_hour,
            "total_requests_all_time": system.total_requests,
            "last_used": system.last_used,
        }
    
    def register_webhook(self, api_key: str, webhook_url: str) -> bool:
        """Register webhook URL for system events."""
        valid, system = self.verify_api_key(api_key)
        if not valid or not system:
            return False
        
        if webhook_url not in system.webhook_urls:
            system.webhook_urls.append(webhook_url)
        
        return True
    
    def unregister_webhook(self, api_key: str, webhook_url: str) -> bool:
        """Unregister webhook URL."""
        valid, system = self.verify_api_key(api_key)
        if not valid or not system:
            return False
        
        if webhook_url in system.webhook_urls:
            system.webhook_urls.remove(webhook_url)
        
        return True
    
    def notify_webhooks(
        self,
        event_type: str,
        event_data: Dict,
        system_ids: Optional[List[str]] = None,
    ):
        """
        Send webhook notifications to interested systems.
        
        event_type can be:
        - memory.updated
        - signal.generated
        - vault.indexed
        """
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": event_data,
        }
        
        # Send to all systems if none specified
        if system_ids is None:
            system_ids = list(self.systems.keys())
        
        for system_id in system_ids:
            if system_id in self.systems:
                system = self.systems[system_id]
                for webhook_url in system.webhook_urls:
                    # In production, actually POST to webhook_url
                    self.webhook_log.append({
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "webhook_url": webhook_url,
                        "event": event,
                        "status": "queued",  # Would be sent asynchronously
                    })
    
    def list_systems(self, active_only: bool = True) -> List[Dict]:
        """List registered systems."""
        systems = []
        for system in self.systems.values():
            if active_only and not system.active:
                continue
            
            systems.append({
                "system_id": system.system_id,
                "system_name": system.system_name,
                "created_at": system.created_at,
                "contact_email": system.contact_email,
                "rate_limit": system.rate_limit_per_hour,
                "active": system.active,
                "total_requests": system.total_requests,
                "last_used": system.last_used,
            })
        
        return systems
    
    def deactivate_system(self, system_id: str) -> bool:
        """Deactivate a third-party system."""
        if system_id not in self.systems:
            return False
        
        system = self.systems[system_id]
        system.active = False
        return True
    
    def reactivate_system(self, system_id: str) -> bool:
        """Reactivate a deactivated system."""
        if system_id not in self.systems:
            return False
        
        system = self.systems[system_id]
        system.active = True
        return True
    
    def rotate_api_key(self, api_key: str) -> Optional[str]:
        """Generate new API key for system (invalidates old key)."""
        if api_key not in self.api_keys:
            return None
        
        old_config = self.api_keys[api_key]
        system_id = old_config.system_id
        
        # Deactivate old key
        old_config.active = False
        
        # Generate new key
        new_api_key = f"pk_{uuid.uuid4().hex}_{uuid.uuid4().hex}"
        new_config = APIKeyConfig(
            api_key=new_api_key,
            system_id=system_id,
            created_at=datetime.utcnow().isoformat() + "Z",
        )
        self.api_keys[new_api_key] = new_config
        
        return new_api_key


# Singleton instance
_gateway: Optional[ThirdPartyIntegrationGateway] = None


def get_integration_gateway() -> ThirdPartyIntegrationGateway:
    """Get or create the third-party integration gateway singleton."""
    global _gateway
    if _gateway is None:
        _gateway = ThirdPartyIntegrationGateway()
    return _gateway
