"""Integration Hub Bot for cross-domain orchestration.

Implements the Integration Hub component from PIPE AgenticAI Governance
Architecture, managing all cross-domain connections and communications.
"""

import asyncio
from typing import Dict, Any

from ..core.bot_base import BotBase
from ..core.event_bus import Event, EventBus
from ..core.state_manager import StateManager
from ..utils.metrics import MetricsCollector
from ..governance.governance_manager import GovernanceManager


class IntegrationHubBot(BotBase):
    """
    Bot for managing cross-domain integrations and governance.

    Serves as the central orchestration point for inter-domain communication
    and implements governance standards across the ecosystem.
    """

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        event_bus: EventBus,
        state_manager: StateManager,
        metrics: MetricsCollector,
    ):
        """
        Initialize the integration hub bot.

        Args:
            name: Bot name
            config: Configuration dictionary
            event_bus: Event bus for communication
            state_manager: State manager for persistence
            metrics: Metrics collector
        """
        super().__init__(name, config)
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.metrics = metrics

        # Initialize governance manager
        self.governance = GovernanceManager()

        # Integration tracking
        self.active_routes: Dict[str, Dict[str, Any]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()

    async def initialize(self) -> bool:
        """Initialize the integration hub bot."""
        try:
            self.logger.info("Initializing IntegrationHubBot")

            # Load saved state
            state = await self.state_manager.load_state(self.name)
            self.active_routes = state.get("active_routes", {})

            # Subscribe to integration events
            self.event_bus.subscribe(
                "integration.request", self._on_integration_request
            )
            self.event_bus.subscribe(
                "integration.message", self._on_integration_message
            )
            self.event_bus.subscribe("domain.register", self._on_domain_register)
            self.event_bus.subscribe("governance.review", self._on_governance_review)

            # Register PIPE domain itself
            await self.governance.register_domain(
                "PIPE",
                capabilities=[
                    "cross_domain_routing",
                    "governance_management",
                    "quality_monitoring",
                    "review_orchestration",
                ],
            )

            self.logger.info("IntegrationHubBot initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize IntegrationHubBot: {str(e)}")
            return False

    async def execute(self) -> None:
        """Main execution loop."""
        self.logger.info("IntegrationHubBot execution started")

        while self.status.value == "running":
            try:
                # Process message queue
                await self._process_message_queue()

                # Publish governance dashboard
                await self._publish_governance_metrics()

                # Monitor integration health
                await self._monitor_integrations()

                # Sleep interval
                await asyncio.sleep(self.config.get("check_interval", 30))

            except Exception as e:
                self.logger.error(f"Error in execution loop: {str(e)}", exc_info=True)
                self.error_count += 1
                await asyncio.sleep(5)

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up IntegrationHubBot")

        # Save state
        await self.state_manager.save_state(
            self.name, {"active_routes": self.active_routes}
        )

        self.logger.info("IntegrationHubBot cleanup complete")

    async def _process_message_queue(self) -> None:
        """Process queued integration messages."""
        try:
            # Process up to 10 messages per cycle
            for _ in range(10):
                if self.message_queue.empty():
                    break

                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self._route_message(message)
                self.task_count += 1
                self.metrics.increment("integration_hub.messages_routed")

        except asyncio.TimeoutError:
            pass
        except Exception as e:
            self.logger.error(f"Error processing message queue: {str(e)}")
            self.error_count += 1

    async def _route_message(self, message: Dict[str, Any]) -> None:
        """
        Route a message between domains.

        Args:
            message: Message to route
        """
        source = message.get("source_domain")
        target = message.get("target_domain")
        payload = message.get("payload")

        self.logger.debug(f"Routing message: {source} → {target}")

        # Validate integration exists
        path = self.governance.domain_registry.validate_integration_path(source, target)

        if not path["valid"]:
            self.logger.warning(f"Invalid integration path: {source} → {target}")
            self.metrics.increment("integration_hub.routing_failures")
            return

        # Record routing metrics
        route_key = f"{source}-{target}"
        if route_key not in self.active_routes:
            self.active_routes[route_key] = {"message_count": 0, "error_count": 0}

        self.active_routes[route_key]["message_count"] += 1

        # Publish routed message
        await self.event_bus.publish(
            Event(
                event_type="integration.routed",
                source=self.name,
                data={
                    "source_domain": source,
                    "target_domain": target,
                    "payload": payload,
                    "route_type": path["path_type"],
                    "hops": path["hops"],
                },
            )
        )

    async def _publish_governance_metrics(self) -> None:
        """Publish governance dashboard metrics."""
        dashboard = self.governance.get_governance_dashboard()

        await self.event_bus.publish(
            Event(
                event_type="governance.dashboard",
                source=self.name,
                data=dashboard,
            )
        )

        # Update metrics
        self.metrics.gauge(
            "integration_hub.total_domains", dashboard["ecosystem"]["total_domains"]
        )
        self.metrics.gauge(
            "integration_hub.active_integrations",
            dashboard["ecosystem"]["active_integrations"],
        )
        self.metrics.gauge(
            "integration_hub.compliance_percentage",
            dashboard["compliance"]["ecosystem_percentage"],
        )

    async def _monitor_integrations(self) -> None:
        """Monitor health of active integrations."""
        integrations = self.governance.domain_registry.list_integrations()

        active_count = 0
        degraded_count = 0

        for integration in integrations:
            if integration["status"].value == "connected":
                active_count += 1
            elif integration["status"].value == "degraded":
                degraded_count += 1

        if degraded_count > 0:
            self.logger.warning(f"{degraded_count} integrations are degraded")

        self.metrics.gauge("integration_hub.active_integrations", active_count)
        self.metrics.gauge("integration_hub.degraded_integrations", degraded_count)

    async def _on_integration_request(self, event: Event) -> None:
        """Handle integration request events."""
        source_domain = event.data.get("source_domain")
        target_domain = event.data.get("target_domain")
        integration_type = event.data.get("integration_type", "api")
        description = event.data.get("description", "")
        priority = event.data.get("priority", "medium")

        result = await self.governance.request_integration(
            source_domain, target_domain, integration_type, description, priority
        )

        # Publish result
        await self.event_bus.publish(
            Event(
                event_type="integration.request.result",
                source=self.name,
                data=result,
            )
        )

        if result["success"]:
            self.metrics.increment("integration_hub.requests_approved")
        else:
            self.metrics.increment("integration_hub.requests_rejected")

    async def _on_integration_message(self, event: Event) -> None:
        """Handle integration messages."""
        await self.message_queue.put(event.data)

    async def _on_domain_register(self, event: Event) -> None:
        """Handle domain registration events."""
        domain_code = event.data.get("domain_code")
        capabilities = event.data.get("capabilities", [])

        result = await self.governance.register_domain(domain_code, capabilities)

        # Publish result
        await self.event_bus.publish(
            Event(
                event_type="domain.registered",
                source=self.name,
                data=result,
            )
        )

        if result["success"]:
            self.metrics.increment("integration_hub.domains_registered")

    async def _on_governance_review(self, event: Event) -> None:
        """Handle governance review events."""
        action = event.data.get("action")
        review_id = event.data.get("review_id")
        reviewer = event.data.get("reviewer")

        if action == "approve":
            # Approve review
            review = self.governance.review_pipeline.get_review(review_id)
            if review:
                self.governance.review_pipeline.approve_review(
                    review_id, reviewer, event.data.get("notes")
                )
                self.metrics.increment("integration_hub.reviews_approved")

        elif action == "reject":
            # Reject review
            self.governance.review_pipeline.reject_review(
                review_id, reviewer, event.data.get("reason")
            )
            self.metrics.increment("integration_hub.reviews_rejected")
