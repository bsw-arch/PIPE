"""
Real-World Integration Example: BNP Business Services

This example demonstrates how to integrate the BNP (Business Network Platform)
domain to provide business services to other domains.

Scenario:
- BNP provides core business services (CRM, invoicing, analytics)
- IV (Innovation Ventures) needs analytics data for innovation metrics
- AXIS needs service health data for architecture monitoring
- All services communicate through PIPE hub with governance

Use Case: Cross-domain business service consumption
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.governance.governance_manager import GovernanceManager  # noqa: E402
from src.core.event_bus import Event, EventBus  # noqa: E402
from src.core.state_manager import StateManager  # noqa: E402
from src.utils.metrics import MetricsCollector  # noqa: E402


class BNPBusinessServices:
    """
    BNP Business Services Integration.

    Provides core business services to the ecosystem.
    """

    def __init__(
        self,
        event_bus: EventBus,
        state_manager: StateManager,
        metrics: MetricsCollector,
    ):
        """Initialize BNP business services."""
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.metrics = metrics
        self.domain = "BNP"

        # Subscribe to service requests
        self.event_bus.subscribe("service.request", self._handle_service_request)
        self.event_bus.subscribe("data.request", self._handle_data_request)

    async def _handle_service_request(self, event: Event) -> None:
        """Handle business service request."""
        service_type = event.data.get("service")
        requesting_domain = event.source
        request_id = event.data.get("request_id")

        print(f"\n[BNP] Received service request from {requesting_domain}")
        print(f"      Service: {service_type}")
        print(f"      Request ID: {request_id}")

        # Route to appropriate service
        if service_type == "analytics":
            await self._provide_analytics(requesting_domain, event.data, request_id)
        elif service_type == "crm":
            await self._provide_crm_data(requesting_domain, event.data, request_id)
        elif service_type == "invoicing":
            await self._provide_invoicing(requesting_domain, event.data, request_id)
        else:
            await self._service_not_found(requesting_domain, service_type, request_id)

        # Track metrics
        self.metrics.increment(f"service.requests.{service_type}")

    async def _provide_analytics(
        self, domain: str, request_data: dict, request_id: str
    ) -> None:
        """Provide analytics service."""
        # Simulate analytics processing
        analytics_data = {
            "period": request_data.get("period", "monthly"),
            "metrics": {
                "total_transactions": 15420,
                "revenue": 1254000.50,
                "customer_growth": 12.5,
                "churn_rate": 2.1,
                "avg_transaction_value": 81.35,
            },
            "trends": {
                "revenue_trend": "increasing",
                "customer_trend": "stable",
                "market_share": 23.4,
            },
            "generated_at": datetime.now().isoformat(),
        }

        await self.event_bus.publish(
            Event(
                event_type="service.response",
                source=self.domain,
                data={
                    "request_id": request_id,
                    "service": "analytics",
                    "target_domain": domain,
                    "status": "success",
                    "data": analytics_data,
                },
            )
        )

        print(f"[BNP] ✓ Analytics data sent to {domain}")
        print(f"      Revenue: ${analytics_data['metrics']['revenue']:,.2f}")
        print(
            f"      Transactions: {analytics_data['metrics']['total_transactions']:,}"
        )

    async def _provide_crm_data(
        self, domain: str, request_data: dict, request_id: str
    ) -> None:
        """Provide CRM service."""
        customer_id = request_data.get("customer_id")

        # Simulate CRM data retrieval
        crm_data = {
            "customer_id": customer_id,
            "name": "Acme Corporation",
            "tier": "Enterprise",
            "lifetime_value": 450000,
            "active_contracts": 3,
            "last_interaction": "2025-11-10",
            "health_score": 85,
            "contacts": [
                {
                    "name": "John Doe",
                    "role": "CTO",
                    "email": "john@acme.com",
                },
                {
                    "name": "Jane Smith",
                    "role": "CFO",
                    "email": "jane@acme.com",
                },
            ],
        }

        await self.event_bus.publish(
            Event(
                event_type="service.response",
                source=self.domain,
                data={
                    "request_id": request_id,
                    "service": "crm",
                    "target_domain": domain,
                    "status": "success",
                    "data": crm_data,
                },
            )
        )

        print(f"[BNP] ✓ CRM data sent to {domain}")
        print(f"      Customer: {crm_data['name']} ({crm_data['tier']})")

    async def _provide_invoicing(
        self, domain: str, request_data: dict, request_id: str
    ) -> None:
        """Provide invoicing service."""
        invoice_data = {
            "invoice_id": "INV-2025-11-001",
            "customer": "Acme Corporation",
            "amount": 15000.00,
            "due_date": "2025-12-01",
            "status": "pending",
            "line_items": [
                {"description": "Enterprise License", "quantity": 10, "price": 1000},
                {"description": "Support & Maintenance", "quantity": 1, "price": 5000},
            ],
        }

        await self.event_bus.publish(
            Event(
                event_type="service.response",
                source=self.domain,
                data={
                    "request_id": request_id,
                    "service": "invoicing",
                    "target_domain": domain,
                    "status": "success",
                    "data": invoice_data,
                },
            )
        )

        print(f"[BNP] ✓ Invoice sent to {domain}")
        print(
            f"      Invoice: {invoice_data['invoice_id']} - ${invoice_data['amount']}"
        )

    async def _service_not_found(
        self, domain: str, service: str, request_id: str
    ) -> None:
        """Handle unknown service request."""
        await self.event_bus.publish(
            Event(
                event_type="service.error",
                source=self.domain,
                data={
                    "request_id": request_id,
                    "target_domain": domain,
                    "status": "error",
                    "error": f"Service not found: {service}",
                },
            )
        )

        print(f"[BNP] ✗ Service not found: {service}")

    async def _handle_data_request(self, event: Event) -> None:
        """Handle data export request."""
        data_type = event.data.get("data_type")
        requesting_domain = event.source

        print(f"\n[BNP] Data export requested by {requesting_domain}")
        print(f"      Type: {data_type}")

        # Simulate data export
        if data_type == "transactions":
            data = self._generate_transaction_data()
        elif data_type == "customers":
            data = self._generate_customer_data()
        else:
            data = {"error": f"Unknown data type: {data_type}"}

        await self.event_bus.publish(
            Event(
                event_type="data.export",
                source=self.domain,
                data={
                    "target_domain": requesting_domain,
                    "data_type": data_type,
                    "records": data,
                    "count": len(data) if isinstance(data, list) else 0,
                },
            )
        )

        print(f"[BNP] ✓ Exported {len(data) if isinstance(data, list) else 0} records")

    def _generate_transaction_data(self) -> list:
        """Generate sample transaction data."""
        return [
            {
                "id": f"TXN-{i:05d}",
                "amount": 100 + (i * 10),
                "customer_id": f"CUST-{i % 100:03d}",
                "status": "completed",
            }
            for i in range(1, 101)
        ]

    def _generate_customer_data(self) -> list:
        """Generate sample customer data."""
        return [
            {
                "id": f"CUST-{i:03d}",
                "name": f"Customer {i}",
                "tier": "Enterprise" if i % 10 == 0 else "Standard",
                "active": True,
            }
            for i in range(1, 51)
        ]


async def demo_bnp_services():
    """Demonstrate BNP business services integration."""
    print("=" * 70)
    print("BNP Business Services Integration Demo")
    print("=" * 70)

    # Initialize components
    event_bus = EventBus()
    state_manager = StateManager("./state/examples")
    metrics = MetricsCollector()
    governance = GovernanceManager()

    # Step 1: Register domains
    print("\n📋 Step 1: Registering domains...")
    domains = {
        "BNP": [
            "business_services",
            "data_processing",
            "api_gateway",
            "crm",
            "analytics",
        ],
        "IV": ["innovation_metrics", "research_data", "venture_tracking"],
        "AXIS": ["architecture_monitoring", "service_health", "integration_patterns"],
    }

    for domain_code, capabilities in domains.items():
        result = await governance.register_domain(domain_code, capabilities)
        print(f"   ✓ {domain_code} registered: {result['compliance_id']}")

    # Step 2: Request service integrations
    print("\n📋 Step 2: Requesting service integrations...")
    integrations = []

    for consumer in ["IV", "AXIS"]:
        result = await governance.request_integration(
            source_domain=consumer,
            target_domain="BNP",
            integration_type="api",
            description=f"{consumer} accessing BNP business services",
            priority="high",
        )
        integrations.append(result)
        print(f"   ✓ {consumer} → BNP: {result['integration_id']}")

    # Step 3: Approve integrations
    print("\n📋 Step 3: Approving integrations...")
    for integration in integrations:
        governance.review_pipeline.assign_reviewers(
            integration["review_id"], ["service.owner@bnp.com"]
        )
        governance.review_pipeline.approve_review(
            integration["review_id"], "service.owner@bnp.com"
        )

        result = await governance.approve_integration(
            integration["integration_id"], reviewer="admin@pipe.com"
        )
        print(f"   ✓ Approved: {integration['integration_id']}")

    # Step 4: Start BNP services
    print("\n📋 Step 4: Starting BNP business services...")
    bnp_services = BNPBusinessServices(event_bus, state_manager, metrics)  # noqa: F841
    print("   ✓ BNP services ready")

    # Step 5: Simulate service requests
    print("\n📋 Step 5: Simulating service requests...")

    # IV requests analytics
    print("\n   → IV requesting analytics data...")
    await event_bus.publish(
        Event(
            event_type="service.request",
            source="IV",
            data={
                "service": "analytics",
                "period": "quarterly",
                "request_id": "REQ-IV-001",
            },
        )
    )

    await asyncio.sleep(0.3)

    # AXIS requests CRM data
    print("\n   → AXIS requesting CRM data...")
    await event_bus.publish(
        Event(
            event_type="service.request",
            source="AXIS",
            data={
                "service": "crm",
                "customer_id": "CUST-12345",
                "request_id": "REQ-AXIS-001",
            },
        )
    )

    await asyncio.sleep(0.3)

    # IV requests invoicing
    print("\n   → IV requesting invoice generation...")
    await event_bus.publish(
        Event(
            event_type="service.request",
            source="IV",
            data={"service": "invoicing", "request_id": "REQ-IV-002"},
        )
    )

    await asyncio.sleep(0.3)

    # Step 6: Request data exports
    print("\n📋 Step 6: Requesting data exports...")

    await event_bus.publish(
        Event(
            event_type="data.request",
            source="IV",
            data={"data_type": "transactions"},
        )
    )

    await asyncio.sleep(0.3)

    # Step 7: Check metrics
    print("\n📋 Step 7: Service metrics...")
    all_metrics = metrics.get_all_metrics()
    if "counters" in all_metrics:
        for metric, count in all_metrics["counters"].items():
            if "service" in metric:
                print(f"   {metric}: {count}")

    # Step 8: Governance dashboard
    print("\n📋 Step 8: Governance status...")
    dashboard = governance.get_governance_dashboard()
    print(f"   Active Integrations: {dashboard['ecosystem']['active_integrations']}")
    print(f"   Compliance: {dashboard['compliance']['ecosystem_percentage']:.1f}%")
    print(f"   Reviews Approved: {dashboard['reviews']['approved']}")

    print("\n" + "=" * 70)
    print("✓ BNP Business Services Integration Demo Complete")
    print("=" * 70)

    print("\n💡 Key Takeaways:")
    print("   • BNP provides multiple business services (CRM, analytics, invoicing)")
    print("   • Services are consumed by other domains (IV, AXIS)")
    print("   • All communication goes through PIPE hub")
    print("   • Governance tracks all integrations")
    print("   • Metrics track service usage")
    print("   • Event-driven architecture enables async processing")


if __name__ == "__main__":
    asyncio.run(demo_bnp_services())
