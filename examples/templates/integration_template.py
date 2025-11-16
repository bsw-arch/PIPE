"""
Integration Template

Use this template to create your own domain integration.
Replace placeholders with your actual domain information.

Template sections:
1. Domain configuration
2. Service implementation
3. Event handlers
4. Governance setup
5. Testing
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.governance.governance_manager import GovernanceManager  # noqa: E402
from src.core.event_bus import Event, EventBus  # noqa: E402
from src.core.state_manager import StateManager  # noqa: E402
from src.utils.metrics import MetricsCollector  # noqa: E402


# ============================================================================
# STEP 1: Configure Your Domain
# ============================================================================

DOMAIN_CONFIG = {
    # Replace with your domain code (BNI, BNP, AXIS, IV, EcoX, THRIVE, DC, BU, or PIPE)
    "domain_code": "YOUR_DOMAIN",
    # Replace with your domain's full name
    "domain_name": "Your Domain Name",
    # List the capabilities your domain provides
    "capabilities": [
        "capability_1",
        "capability_2",
        "capability_3",
    ],
    # Define services your domain offers
    "services": {
        "service_1": {
            "description": "Description of service 1",
            "endpoint": "/api/v1/service1",
            "methods": ["GET", "POST"],
        },
        "service_2": {
            "description": "Description of service 2",
            "endpoint": "/api/v1/service2",
            "methods": ["GET", "POST", "PUT"],
        },
    },
}


# ============================================================================
# STEP 2: Implement Your Service
# ============================================================================


class YourDomainService:
    """
    Your domain service integration.

    Replace this docstring with your domain's description.
    """

    def __init__(
        self,
        event_bus: EventBus,
        state_manager: StateManager,
        metrics: MetricsCollector,
    ):
        """Initialize your service."""
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.metrics = metrics
        self.domain = DOMAIN_CONFIG["domain_code"]

        # Subscribe to events your service handles
        self.event_bus.subscribe("your.event.type", self._handle_event)
        self.event_bus.subscribe("your.request.type", self._handle_request)

    async def _handle_event(self, event: Event) -> None:
        """
        Handle incoming events.

        Args:
            event: Event object containing data
        """
        requesting_domain = event.source
        event_data = event.data

        print(f"[{self.domain}] Received event from {requesting_domain}")
        print(f"            Data: {event_data}")

        # TODO: Implement your event handling logic here

        # Example: Process the event and publish response
        result = await self._process_event_data(event_data)

        # Publish response
        await self.event_bus.publish(
            Event(
                event_type="your.event.response",
                source=self.domain,
                data={
                    "original_request": event_data,
                    "result": result,
                    "status": "success",
                },
            )
        )

        # Track metrics
        self.metrics.increment(f"{self.domain}.events.processed")

    async def _handle_request(self, event: Event) -> None:
        """
        Handle service requests.

        Args:
            event: Event object containing request data
        """
        request_type = event.data.get("type")
        requesting_domain = event.source

        print(f"[{self.domain}] Service request from {requesting_domain}")
        print(f"            Type: {request_type}")

        # TODO: Route to appropriate service handler
        if request_type == "service_1":
            result = await self._handle_service_1(event.data)
        elif request_type == "service_2":
            result = await self._handle_service_2(event.data)
        else:
            result = {"error": f"Unknown service type: {request_type}"}

        # Publish response
        await self.event_bus.publish(
            Event(
                event_type="your.request.response",
                source=self.domain,
                data={
                    "request_type": request_type,
                    "target_domain": requesting_domain,
                    "result": result,
                },
            )
        )

    async def _process_event_data(self, event_data: dict) -> dict:
        """
        Process event data.

        TODO: Implement your business logic here.

        Args:
            event_data: Data from the event

        Returns:
            Processing result
        """
        # Example implementation
        return {
            "processed": True,
            "data": event_data,
            "message": "Successfully processed",
        }

    async def _handle_service_1(self, request_data: dict) -> dict:
        """
        Handle service 1 requests.

        TODO: Implement service 1 logic.

        Args:
            request_data: Request parameters

        Returns:
            Service response
        """
        # Example implementation
        return {
            "service": "service_1",
            "result": "Service 1 result",
            "data": request_data,
        }

    async def _handle_service_2(self, request_data: dict) -> dict:
        """
        Handle service 2 requests.

        TODO: Implement service 2 logic.

        Args:
            request_data: Request parameters

        Returns:
            Service response
        """
        # Example implementation
        return {
            "service": "service_2",
            "result": "Service 2 result",
            "data": request_data,
        }


# ============================================================================
# STEP 3: Setup Governance
# ============================================================================


async def setup_governance(governance: GovernanceManager) -> dict:
    """
    Setup governance for your domain.

    Args:
        governance: GovernanceManager instance

    Returns:
        Setup results
    """
    print(f"\n📋 Registering {DOMAIN_CONFIG['domain_code']} domain...")

    # Register your domain
    result = await governance.register_domain(
        DOMAIN_CONFIG["domain_code"], DOMAIN_CONFIG["capabilities"]
    )

    print(f"   ✓ Domain registered: {result['compliance_id']}")

    return result


async def setup_integrations(
    governance: GovernanceManager, target_domains: list
) -> list:
    """
    Setup integrations with other domains.

    Args:
        governance: GovernanceManager instance
        target_domains: List of domains to integrate with

    Returns:
        List of integration results
    """
    print("\n📋 Requesting integrations...")
    integrations = []

    for target_domain in target_domains:
        result = await governance.request_integration(
            source_domain=DOMAIN_CONFIG["domain_code"],
            target_domain=target_domain,
            integration_type="api",
            description=f"{DOMAIN_CONFIG['domain_code']} to {target_domain} integration",
            priority="medium",
        )

        integrations.append(result)
        print(
            f"   ✓ {DOMAIN_CONFIG['domain_code']} → {target_domain}: {result['integration_id']}"
        )

    return integrations


async def approve_integrations(
    governance: GovernanceManager, integrations: list
) -> None:
    """
    Approve integration requests.

    Args:
        governance: GovernanceManager instance
        integrations: List of integration results
    """
    print("\n📋 Approving integrations...")

    for integration in integrations:
        # Assign reviewers
        governance.review_pipeline.assign_reviewers(
            integration["review_id"], ["reviewer@pipe.com"]
        )

        # Approve
        governance.review_pipeline.approve_review(
            integration["review_id"], "reviewer@pipe.com"
        )

        result = await governance.approve_integration(  # noqa: F841
            integration["integration_id"], reviewer="admin@pipe.com"
        )

        print(f"   ✓ Approved: {integration['integration_id']}")


# ============================================================================
# STEP 4: Demo/Test Your Integration
# ============================================================================


async def demo_integration():
    """
    Demonstrate your domain integration.

    TODO: Customize this demo for your use case.
    """
    print("=" * 70)
    print(f"{DOMAIN_CONFIG['domain_name']} Integration Demo")
    print("=" * 70)

    # Initialize components
    event_bus = EventBus()
    state_manager = StateManager("./state/examples")
    metrics = MetricsCollector()
    governance = GovernanceManager()

    # Setup governance
    await setup_governance(governance)

    # TODO: Define which domains you want to integrate with
    target_domains = ["PIPE"]  # Add your target domains here

    # Setup integrations
    integrations = await setup_integrations(governance, target_domains)

    # Approve integrations
    await approve_integrations(governance, integrations)

    # Start your service
    print(f"\n📋 Starting {DOMAIN_CONFIG['domain_code']} service...")
    service = YourDomainService(event_bus, state_manager, metrics)  # noqa: F841
    print(f"   ✓ {DOMAIN_CONFIG['domain_code']} service ready")

    # TODO: Add your test scenarios here
    print("\n📋 Testing service...")

    # Example: Publish a test event
    await event_bus.publish(
        Event(
            event_type="your.event.type",
            source="TEST",
            data={"test_data": "example value", "request_id": "TEST-001"},
        )
    )

    await asyncio.sleep(0.5)

    # Example: Request a service
    await event_bus.publish(
        Event(
            event_type="your.request.type",
            source="TEST",
            data={"type": "service_1", "parameters": {"param1": "value1"}},
        )
    )

    await asyncio.sleep(0.5)

    # Check metrics
    print("\n📋 Metrics...")
    all_metrics = metrics.get_all_metrics()
    if "counters" in all_metrics:
        for metric, count in all_metrics["counters"].items():
            if DOMAIN_CONFIG["domain_code"].lower() in metric.lower():
                print(f"   {metric}: {count}")

    # Check governance
    print("\n📋 Governance status...")
    dashboard = governance.get_governance_dashboard()
    print(f"   Active Integrations: {dashboard['ecosystem']['active_integrations']}")
    print(f"   Compliance: {dashboard['compliance']['ecosystem_percentage']:.1f}%")

    print("\n" + "=" * 70)
    print(f"✓ {DOMAIN_CONFIG['domain_name']} Integration Demo Complete")
    print("=" * 70)


# ============================================================================
# STEP 5: Run Your Integration
# ============================================================================

if __name__ == "__main__":
    """
    To use this template:

    1. Update DOMAIN_CONFIG with your domain information
    2. Implement service logic in YourDomainService methods
    3. Customize governance setup if needed
    4. Add test scenarios in demo_integration()
    5. Run: python integration_template.py
    """
    asyncio.run(demo_integration())
