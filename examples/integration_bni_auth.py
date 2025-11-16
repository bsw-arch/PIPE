"""
Real-World Integration Example: BNI Authentication Service

This example demonstrates how to integrate the BNI (Business Network Infrastructure)
domain for authentication services across the PIPE ecosystem.

Scenario:
- BNI provides centralized authentication and user management
- Other domains (BNP, AXIS, IV) need to authenticate users through BNI
- PIPE hub orchestrates the authentication requests
- All integrations must pass governance compliance

Use Case: Single Sign-On (SSO) across all domains
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.governance.governance_manager import GovernanceManager  # noqa: E402
from src.core.event_bus import Event, EventBus  # noqa: E402
from src.core.state_manager import StateManager  # noqa: E402
from src.utils.metrics import MetricsCollector  # noqa: E402


class BNIAuthenticationService:
    """
    BNI Authentication Service Integration.

    Provides centralized authentication for the entire ecosystem.
    """

    def __init__(self, event_bus: EventBus, state_manager: StateManager):
        """Initialize BNI authentication service."""
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.domain = "BNI"

        # Subscribe to authentication requests
        self.event_bus.subscribe("auth.request", self._handle_auth_request)
        self.event_bus.subscribe("user.validate", self._handle_user_validation)

    async def _handle_auth_request(self, event: Event) -> None:
        """Handle authentication request from another domain."""
        username = event.data.get("username")
        password_hash = event.data.get("password_hash")
        requesting_domain = event.source

        print(f"\n[BNI] Received auth request from {requesting_domain}")
        print(f"      Username: {username}")

        # Simulate authentication
        is_valid = await self._authenticate_user(username, password_hash)

        # Create authentication token
        if is_valid:
            token = await self._generate_token(username, requesting_domain)

            # Publish authentication success
            await self.event_bus.publish(
                Event(
                    event_type="auth.success",
                    source=self.domain,
                    data={
                        "username": username,
                        "token": token,
                        "domain": requesting_domain,
                        "expires_in": 3600,
                        "permissions": await self._get_user_permissions(username),
                    },
                )
            )
            print(f"[BNI] ✓ Authentication successful for {username}")
            print(f"      Token: {token[:20]}...")
        else:
            await self.event_bus.publish(
                Event(
                    event_type="auth.failure",
                    source=self.domain,
                    data={
                        "username": username,
                        "domain": requesting_domain,
                        "reason": "Invalid credentials",
                    },
                )
            )
            print(f"[BNI] ✗ Authentication failed for {username}")

    async def _authenticate_user(self, username: str, password_hash: str) -> bool:
        """Authenticate user credentials."""
        # In real implementation, this would check against a database
        # For demo purposes, we'll simulate authentication
        valid_users = {
            "admin@bni.com": "hash_admin_password",
            "user@bnp.com": "hash_user_password",
            "dev@axis.com": "hash_dev_password",
        }

        return valid_users.get(username) == password_hash

    async def _generate_token(self, username: str, domain: str) -> str:
        """Generate authentication token."""
        import hashlib
        import time

        # Simulate JWT-like token
        payload = f"{username}:{domain}:{time.time()}"
        token = hashlib.sha256(payload.encode()).hexdigest()

        # Store token in state
        await self.state_manager.set_value(
            self.domain,
            f"token_{token}",
            {
                "username": username,
                "domain": domain,
                "created_at": time.time(),
                "expires_at": time.time() + 3600,
            },
        )

        return token

    async def _get_user_permissions(self, username: str) -> list:
        """Get user permissions."""
        # Simulate role-based permissions
        permissions_map = {
            "admin@bni.com": ["read", "write", "admin", "governance.approve"],
            "user@bnp.com": ["read", "write"],
            "dev@axis.com": ["read", "write", "deploy"],
        }

        return permissions_map.get(username, ["read"])

    async def _handle_user_validation(self, event: Event) -> None:
        """Validate user token."""
        token = event.data.get("token")

        # Retrieve token from state
        token_data = await self.state_manager.get_value(self.domain, f"token_{token}")

        if token_data:
            # Check if token is expired
            import time

            if token_data["expires_at"] > time.time():
                await self.event_bus.publish(
                    Event(
                        event_type="user.valid",
                        source=self.domain,
                        data={
                            "username": token_data["username"],
                            "domain": token_data["domain"],
                            "valid": True,
                        },
                    )
                )
            else:
                await self.event_bus.publish(
                    Event(
                        event_type="user.invalid",
                        source=self.domain,
                        data={"token": token, "reason": "Token expired"},
                    )
                )


async def demo_bni_authentication():
    """Demonstrate BNI authentication integration."""
    print("=" * 70)
    print("BNI Authentication Service Integration Demo")
    print("=" * 70)

    # Initialize components
    event_bus = EventBus()
    state_manager = StateManager("./state/examples")
    metrics = MetricsCollector()  # noqa: F841
    governance = GovernanceManager()

    # Step 1: Register BNI domain with governance
    print("\n📋 Step 1: Registering BNI domain...")
    result = await governance.register_domain(
        "BNI",
        capabilities=[
            "authentication",
            "user_management",
            "access_control",
            "session_management",
            "role_based_access",
        ],
    )
    print(f"   ✓ BNI registered: {result['compliance_id']}")

    # Step 2: Register consuming domains
    print("\n📋 Step 2: Registering consuming domains...")
    for domain, caps in [
        ("BNP", ["business_services", "data_processing"]),
        ("AXIS", ["architecture_governance", "integration_patterns"]),
    ]:
        result = await governance.register_domain(domain, caps)
        print(f"   ✓ {domain} registered: {result['compliance_id']}")

    # Step 3: Request authentication integrations
    print("\n📋 Step 3: Requesting authentication integrations...")
    integrations = []
    for domain in ["BNP", "AXIS"]:
        result = await governance.request_integration(
            source_domain=domain,
            target_domain="BNI",
            integration_type="api",
            description=f"Authentication service for {domain}",
            priority="high",
        )
        integrations.append(result)
        print(f"   ✓ {domain} → BNI: {result['integration_id']}")

    # Step 4: Approve integrations
    print("\n📋 Step 4: Approving integrations...")
    for integration in integrations:
        # Assign reviewers
        governance.review_pipeline.assign_reviewers(
            integration["review_id"], ["security@bni.com", "governance@pipe.com"]
        )

        # Approve from each reviewer
        for reviewer in ["security@bni.com", "governance@pipe.com"]:
            governance.review_pipeline.approve_review(
                integration["review_id"], reviewer
            )

        # Final approval
        result = await governance.approve_integration(
            integration["integration_id"],
            reviewer="admin@pipe.com",
            notes="Authentication integration approved",
        )
        print(f"   ✓ Integration approved: {integration['integration_id']}")

    # Step 5: Initialize BNI authentication service
    print("\n📋 Step 5: Starting BNI authentication service...")
    auth_service = BNIAuthenticationService(event_bus, state_manager)  # noqa: F841
    print("   ✓ BNI authentication service ready")

    # Step 6: Simulate authentication requests
    print("\n📋 Step 6: Simulating authentication requests...")

    # BNP requests authentication
    print("\n   → BNP requesting authentication...")
    await event_bus.publish(
        Event(
            event_type="auth.request",
            source="BNP",
            data={
                "username": "user@bnp.com",
                "password_hash": "hash_user_password",
            },
        )
    )

    await asyncio.sleep(0.5)

    # AXIS requests authentication
    print("\n   → AXIS requesting authentication...")
    await event_bus.publish(
        Event(
            event_type="auth.request",
            source="AXIS",
            data={
                "username": "dev@axis.com",
                "password_hash": "hash_dev_password",
            },
        )
    )

    await asyncio.sleep(0.5)

    # Failed authentication attempt
    print("\n   → Simulating failed authentication...")
    await event_bus.publish(
        Event(
            event_type="auth.request",
            source="BNP",
            data={
                "username": "hacker@evil.com",
                "password_hash": "wrong_password",
            },
        )
    )

    await asyncio.sleep(0.5)

    # Step 7: Check governance compliance
    print("\n📋 Step 7: Checking governance compliance...")
    dashboard = governance.get_governance_dashboard()
    print(f"   Active Domains: {dashboard['ecosystem']['active_domains']}")
    print(f"   Active Integrations: {dashboard['ecosystem']['active_integrations']}")
    print(f"   Compliance: {dashboard['compliance']['ecosystem_percentage']:.1f}%")
    print(f"   Approved Reviews: {dashboard['reviews']['approved']}")

    # Step 8: Show event history
    print("\n📋 Step 8: Event history...")
    auth_events = event_bus.get_history("auth.success")
    print(f"   Successful authentications: {len(auth_events)}")
    for event in auth_events:
        print(f"   - {event.data['username']} @ {event.data['domain']}")

    print("\n" + "=" * 70)
    print("✓ BNI Authentication Integration Demo Complete")
    print("=" * 70)

    print("\n💡 Key Takeaways:")
    print("   • BNI provides centralized authentication")
    print("   • All integrations pass through governance")
    print("   • Event-driven architecture enables loose coupling")
    print("   • Compliance is tracked automatically")
    print("   • Authentication tokens are managed by BNI")
    print("   • Permissions are centrally controlled")


if __name__ == "__main__":
    asyncio.run(demo_bni_authentication())
