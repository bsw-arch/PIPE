"""Domain Registry for cross-domain integration management.

Manages domain boundaries, connectivity standards, and inter-domain relationships
as defined in the PIPE AgenticAI Governance Architecture.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum


class DomainStatus(Enum):
    """Domain operational status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    SUSPENDED = "suspended"


class IntegrationStatus(Enum):
    """Integration connection status."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    DEGRADED = "degraded"
    INITIALIZING = "initializing"


class DomainRegistry:
    """
    Central registry for managing domain relationships and integrations.

    Implements the Integration Hub component from PIPE AgenticAI Governance
    Architecture, maintaining connectivity standards across all domains.
    """

    # Supported domains as per governance architecture
    SUPPORTED_DOMAINS = {
        "BNI": "Business Network Infrastructure",
        "BNP": "Business Network Platform",
        "AXIS": "Architecture eXchange Integration System",
        "IV": "Innovation Ventures",
        "EcoX": "Ecosystem Exchange",
        "THRIVE": "Technology Hub for Research & Innovation Ventures Ecosystem",
        "DC": "Disconnect Collective",
        "BU": "Business Unit",
        "PIPE": "Platform Interface for Pipeline & Environment",
    }

    def __init__(self):
        """Initialize the domain registry."""
        self.logger = logging.getLogger("pipe.governance.domain_registry")
        self.domains: Dict[str, Dict[str, Any]] = {}
        self.integrations: Dict[str, Dict[str, Any]] = {}
        self.connection_matrix: Dict[str, Set[str]] = {}

        # Initialize registry with supported domains
        self._initialize_domains()

    def _initialize_domains(self) -> None:
        """Initialize registry with supported domains."""
        for domain_code, domain_name in self.SUPPORTED_DOMAINS.items():
            self.domains[domain_code] = {
                "code": domain_code,
                "name": domain_name,
                "status": DomainStatus.INACTIVE,
                "registered_at": datetime.now().isoformat(),
                "last_seen": None,
                "capabilities": set(),
                "metadata": {},
            }
            self.connection_matrix[domain_code] = set()

        self.logger.info(
            f"Initialized domain registry with {len(self.domains)} domains"
        )

    def register_domain(
        self, domain_code: str, capabilities: List[str] = None, metadata: Dict = None
    ) -> bool:
        """
        Register or update a domain in the registry.

        Args:
            domain_code: Domain identifier (e.g., 'BNI', 'PIPE')
            capabilities: List of domain capabilities
            metadata: Additional domain metadata

        Returns:
            True if registration successful
        """
        if domain_code not in self.SUPPORTED_DOMAINS:
            self.logger.error(f"Unsupported domain code: {domain_code}")
            return False

        domain = self.domains[domain_code]
        domain["status"] = DomainStatus.ACTIVE
        domain["last_seen"] = datetime.now().isoformat()

        if capabilities:
            domain["capabilities"].update(capabilities)

        if metadata:
            domain["metadata"].update(metadata)

        self.logger.info(f"Registered domain: {domain_code} - {domain['name']}")
        return True

    def register_integration(
        self,
        source_domain: str,
        target_domain: str,
        integration_type: str,
        config: Dict = None,
    ) -> str:
        """
        Register an integration between two domains.

        Args:
            source_domain: Source domain code
            target_domain: Target domain code
            integration_type: Type of integration (api, event, data)
            config: Integration configuration

        Returns:
            Integration ID
        """
        if source_domain not in self.domains or target_domain not in self.domains:
            raise ValueError(f"Invalid domain codes: {source_domain}, {target_domain}")

        integration_id = f"{source_domain}-{target_domain}-{integration_type}"

        self.integrations[integration_id] = {
            "id": integration_id,
            "source": source_domain,
            "target": target_domain,
            "type": integration_type,
            "status": IntegrationStatus.INITIALIZING,
            "created_at": datetime.now().isoformat(),
            "last_health_check": None,
            "config": config or {},
            "metrics": {"message_count": 0, "error_count": 0, "last_success": None},
        }

        # Update connection matrix
        self.connection_matrix[source_domain].add(target_domain)
        self.connection_matrix[target_domain].add(source_domain)

        self.logger.info(
            f"Registered integration: {integration_id} ({source_domain} ↔ {target_domain})"
        )
        return integration_id

    def update_integration_status(
        self, integration_id: str, status: IntegrationStatus
    ) -> bool:
        """
        Update the status of an integration.

        Args:
            integration_id: Integration identifier
            status: New integration status

        Returns:
            True if update successful
        """
        if integration_id not in self.integrations:
            self.logger.error(f"Integration not found: {integration_id}")
            return False

        self.integrations[integration_id]["status"] = status
        self.integrations[integration_id][
            "last_health_check"
        ] = datetime.now().isoformat()

        self.logger.info(
            f"Updated integration {integration_id} status to {status.value}"
        )
        return True

    def get_domain_info(self, domain_code: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific domain."""
        return self.domains.get(domain_code)

    def get_domain_connections(self, domain_code: str) -> Set[str]:
        """Get all domains connected to a specific domain."""
        return self.connection_matrix.get(domain_code, set())

    def get_integration(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific integration."""
        return self.integrations.get(integration_id)

    def list_active_domains(self) -> List[str]:
        """Get list of active domains."""
        return [
            code
            for code, domain in self.domains.items()
            if domain["status"] == DomainStatus.ACTIVE
        ]

    def list_integrations(
        self, domain_code: str = None, status: IntegrationStatus = None
    ) -> List[Dict[str, Any]]:
        """
        List integrations with optional filtering.

        Args:
            domain_code: Filter by domain (source or target)
            status: Filter by integration status

        Returns:
            List of integration records
        """
        integrations = list(self.integrations.values())

        if domain_code:
            integrations = [
                i
                for i in integrations
                if i["source"] == domain_code or i["target"] == domain_code
            ]

        if status:
            integrations = [i for i in integrations if i["status"] == status]

        return integrations

    def get_ecosystem_topology(self) -> Dict[str, Any]:
        """
        Get complete ecosystem topology.

        Returns:
            Dictionary containing domains and their connections
        """
        return {
            "domains": {
                code: {
                    "name": domain["name"],
                    "status": domain["status"].value,
                    "connections": len(self.connection_matrix[code]),
                    "capabilities": list(domain["capabilities"]),
                }
                for code, domain in self.domains.items()
            },
            "total_integrations": len(self.integrations),
            "active_integrations": len(
                [
                    i
                    for i in self.integrations.values()
                    if i["status"] == IntegrationStatus.CONNECTED
                ]
            ),
            "connection_matrix": {
                domain: list(connections)
                for domain, connections in self.connection_matrix.items()
            },
        }

    def validate_integration_path(self, source: str, target: str) -> Dict[str, Any]:
        """
        Validate if integration path exists between domains.

        Args:
            source: Source domain code
            target: Target domain code

        Returns:
            Dictionary with validation results
        """
        if source not in self.domains or target not in self.domains:
            return {"valid": False, "reason": "Invalid domain codes"}

        # Direct connection check
        if target in self.connection_matrix[source]:
            return {
                "valid": True,
                "path_type": "direct",
                "hops": 1,
                "path": [source, target],
            }

        # Check for indirect path through PIPE hub
        if source != "PIPE" and target != "PIPE":
            if (
                "PIPE" in self.connection_matrix[source]
                and "PIPE" in self.connection_matrix[target]
            ):
                return {
                    "valid": True,
                    "path_type": "hub",
                    "hops": 2,
                    "path": [source, "PIPE", target],
                }

        return {"valid": False, "reason": "No integration path available"}
