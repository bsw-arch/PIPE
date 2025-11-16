"""Governance Manager for coordinating all governance components.

Orchestrates the PIPE AgenticAI Governance Architecture across
domain governance and bot implementation tiers.
"""

import logging
from typing import Dict, Any, Optional

from .domain_registry import DomainRegistry, IntegrationStatus
from .compliance_tracker import ComplianceTracker
from .review_pipeline import ReviewPipeline, ReviewStatus, ReviewType, ReviewPriority


class GovernanceManager:
    """
    Central governance coordination system.

    Orchestrates domain registry, compliance tracking, and review pipeline
    to implement the complete PIPE AgenticAI Governance Architecture.
    """

    def __init__(self):
        """Initialize the governance manager."""
        self.logger = logging.getLogger("pipe.governance.manager")

        # Initialize governance components
        self.domain_registry = DomainRegistry()
        self.compliance_tracker = ComplianceTracker()
        self.review_pipeline = ReviewPipeline()

        # Ensure PIPE hub is registered
        self._initialize_pipe_hub()

        self.logger.info("Governance manager initialized")

    def _initialize_pipe_hub(self):
        """Initialize PIPE as the central hub."""
        self.domain_registry.register_domain(
            "PIPE",
            capabilities=[
                "cross_domain_routing",
                "governance_management",
                "quality_monitoring",
                "review_orchestration",
            ],
        )

    async def register_domain(
        self, domain_code: str, capabilities: list = None
    ) -> Dict[str, Any]:
        """
        Register a domain in the governance system.

        Args:
            domain_code: Domain identifier
            capabilities: Domain capabilities

        Returns:
            Registration result
        """
        # Register in domain registry
        success = self.domain_registry.register_domain(domain_code, capabilities)

        if not success:
            return {"success": False, "error": "Domain registration failed"}

        # Create compliance record
        compliance_id = self.compliance_tracker.create_compliance_record(
            entity_id=domain_code, entity_type="domain", domain=domain_code
        )

        # Auto-connect to PIPE hub (except for PIPE itself)
        if domain_code != "PIPE":
            try:
                hub_integration_id = self.domain_registry.register_integration(
                    domain_code, "PIPE", "hub"
                )
                self.logger.info(
                    f"Domain {domain_code} auto-connected to PIPE hub: {hub_integration_id}"
                )
            except Exception as e:
                self.logger.warning(
                    f"Failed to auto-connect {domain_code} to PIPE: {str(e)}"
                )

        self.logger.info(f"Domain {domain_code} registered with governance")

        return {
            "success": True,
            "domain_code": domain_code,
            "compliance_id": compliance_id,
            "status": "registered",
        }

    async def request_integration(
        self,
        source_domain: str,
        target_domain: str,
        integration_type: str,
        description: str,
        priority: str = "medium",
    ) -> Dict[str, Any]:
        """
        Request a new cross-domain integration.

        Args:
            source_domain: Source domain code
            target_domain: Target domain code
            integration_type: Type of integration
            description: Integration description
            priority: Priority level

        Returns:
            Integration request result
        """
        # Validate integration path
        path_validation = self.domain_registry.validate_integration_path(
            source_domain, target_domain
        )

        if not path_validation["valid"]:
            return {
                "success": False,
                "error": path_validation["reason"],
            }

        # Create review request
        priority_enum = getattr(ReviewPriority, priority.upper(), ReviewPriority.MEDIUM)
        review_id = self.review_pipeline.create_review(
            title=f"Integration: {source_domain} → {target_domain}",
            review_type=ReviewType.INTEGRATION,
            source_domain=source_domain,
            target_domain=target_domain,
            description=description,
            priority=priority_enum,
            metadata={
                "integration_type": integration_type,
                "path_type": path_validation.get("path_type"),
            },
        )

        # Register integration (pending approval)
        integration_id = self.domain_registry.register_integration(
            source_domain, target_domain, integration_type
        )

        # Create compliance record
        compliance_id = self.compliance_tracker.create_compliance_record(
            entity_id=integration_id, entity_type="integration", domain="PIPE"
        )

        self.logger.info(
            f"Integration request created: {integration_id} (Review: {review_id})"
        )

        return {
            "success": True,
            "integration_id": integration_id,
            "review_id": review_id,
            "status": "pending_review",
            "compliance_id": compliance_id,
        }

    async def approve_integration(
        self, integration_id: str, reviewer: str, notes: str = None
    ) -> Dict[str, Any]:
        """
        Approve an integration request.

        Args:
            integration_id: Integration identifier
            reviewer: Reviewer identifier
            notes: Optional approval notes

        Returns:
            Approval result
        """
        # Update integration status
        success = self.domain_registry.update_integration_status(
            integration_id, IntegrationStatus.CONNECTED
        )

        if not success:
            return {"success": False, "error": "Integration not found"}

        # Find and approve review
        reviews = self.review_pipeline.list_reviews()
        review_id = None
        for review in reviews:
            if review.get("metadata", {}).get("integration_id") == integration_id:
                review_id = review["id"]
                break

        if review_id:
            self.review_pipeline.approve_review(review_id, reviewer, notes)

        self.logger.info(f"Integration {integration_id} approved by {reviewer}")

        return {
            "success": True,
            "integration_id": integration_id,
            "status": "approved",
            "review_id": review_id,
        }

    def get_governance_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive governance dashboard data.

        Returns:
            Dashboard data with all governance metrics
        """
        # Get ecosystem topology
        topology = self.domain_registry.get_ecosystem_topology()

        # Get compliance metrics
        compliance = self.compliance_tracker.get_ecosystem_compliance()

        # Get review metrics
        review_metrics = self.review_pipeline.get_review_metrics()

        # Compile dashboard
        dashboard = {
            "timestamp": topology.get("timestamp"),
            "ecosystem": {
                "total_domains": len(topology["domains"]),
                "active_domains": len(
                    [d for d in topology["domains"].values() if d["status"] == "active"]
                ),
                "total_integrations": topology["total_integrations"],
                "active_integrations": topology["active_integrations"],
            },
            "compliance": {
                "ecosystem_percentage": compliance["ecosystem_compliance_percentage"],
                "total_entities": compliance["total_entities"],
                "by_domain": {
                    domain: {
                        "percentage": data["compliance_percentage"],
                        "compliant": data["compliance_summary"]["compliant"],
                        "total": data["total_entities"],
                    }
                    for domain, data in compliance["domains"].items()
                },
            },
            "reviews": {
                "total": review_metrics["total_reviews"],
                "pending": review_metrics["pending"],
                "in_review": review_metrics["in_review"],
                "approved": review_metrics["approved"],
                "requires_changes": review_metrics["requires_changes"],
            },
            "domains": topology["domains"],
        }

        return dashboard

    def get_domain_status(self, domain_code: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive status for a specific domain.

        Args:
            domain_code: Domain identifier

        Returns:
            Domain status and metrics
        """
        # Get domain info
        domain_info = self.domain_registry.get_domain_info(domain_code)
        if not domain_info:
            return None

        # Get connections
        connections = self.domain_registry.get_domain_connections(domain_code)

        # Get integrations
        integrations = self.domain_registry.list_integrations(domain_code=domain_code)

        # Get compliance summary
        compliance_summary = self.compliance_tracker.get_domain_compliance_summary(
            domain_code
        )

        # Get reviews
        reviews = self.review_pipeline.list_reviews(domain=domain_code)

        return {
            "domain": {
                "code": domain_code,
                "name": domain_info["name"],
                "status": domain_info["status"].value,
                "capabilities": list(domain_info["capabilities"]),
            },
            "connectivity": {
                "connected_domains": len(connections),
                "connections": list(connections),
                "integrations": len(integrations),
            },
            "compliance": compliance_summary,
            "reviews": {
                "total": len(reviews),
                "pending": len(
                    [r for r in reviews if r["status"] == ReviewStatus.PENDING]
                ),
                "approved": len(
                    [r for r in reviews if r["status"] == ReviewStatus.APPROVED]
                ),
            },
        }
