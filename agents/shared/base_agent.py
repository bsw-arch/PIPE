"""
Base Agent Framework
====================
Foundation for all AXIS Augmentic AI agents
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
import logging


@dataclass
class AgentConfig:
    """Configuration for AXIS agents"""

    name: str
    role: str
    goal: str
    backstory: str

    # Operational settings
    autonomous: bool = True
    verbose: bool = False
    allow_delegation: bool = True

    # Integration endpoints
    keragr_url: Optional[str] = "http://localhost:3108"
    coordination_url: Optional[str] = "http://localhost:3111"

    # Augmentic AI settings
    learning_enabled: bool = True
    pattern_recognition: bool = True
    collaborative_intelligence: bool = True

    # Security & compliance
    togaf_compliance: bool = True
    audit_logging: bool = True
    encryption_enabled: bool = True

    # Metadata
    version: str = "0.1.0"
    created_at: datetime = field(default_factory=datetime.now)


class BaseAgent(ABC):
    """
    Base class for all AXIS Augmentic AI agents

    Provides core functionality:
    - Autonomous operation
    - Knowledge graph integration (META-KERAGR)
    - Multi-bot coordination
    - Continuous learning
    - TOGAF compliance
    """

    def __init__(self, config: AgentConfig):
        """Initialise base agent"""
        self.config = config
        self.logger = logging.getLogger(f"axis.{config.name}")

        # Agent state
        self.active = False
        self.task_count = 0
        self.errors = []

        # Knowledge graph connection
        self.keragr_client = None
        self.coordination_client = None

        self._log_initialization()

    def _log_initialization(self):
        """Log agent initialization"""
        self.logger.info(
            f"Initialising {self.config.name}",
            extra={
                "role": self.config.role,
                "autonomous": self.config.autonomous,
                "version": self.config.version,
            }
        )

    @abstractmethod
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task

        Args:
            task: Task definition with context

        Returns:
            Task execution result
        """
        pass

    @abstractmethod
    def autonomous_operation(self) -> None:
        """
        Autonomous operation loop

        Continuously:
        1. Monitor for relevant events
        2. Query knowledge graph for context
        3. Make autonomous decisions
        4. Execute actions
        5. Store outcomes for learning
        """
        pass

    def query_knowledge_graph(self, query: str) -> Dict[str, Any]:
        """
        Query META-KERAGR knowledge graph

        Args:
            query: SPARQL or natural language query

        Returns:
            Query results with historical patterns
        """
        if not self.keragr_client:
            self.logger.warning("META-KERAGR client not connected")
            return {"status": "unavailable", "results": []}

        # Query knowledge graph for historical patterns
        # This enables learning from past decisions
        try:
            results = self.keragr_client.query(query)
            return {"status": "success", "results": results}
        except Exception as e:
            self.logger.error(f"Knowledge graph query failed: {e}")
            return {"status": "error", "error": str(e)}

    def store_outcome(self, task: Dict[str, Any], outcome: Dict[str, Any]) -> None:
        """
        Store task outcome in knowledge graph

        Enables continuous learning and pattern optimisation

        Args:
            task: Original task definition
            outcome: Execution outcome with metrics
        """
        if not self.keragr_client:
            self.logger.warning("Cannot store outcome: META-KERAGR unavailable")
            return

        try:
            # Store in knowledge graph for future learning
            self.keragr_client.store({
                "agent": self.config.name,
                "task": task,
                "outcome": outcome,
                "timestamp": datetime.now().isoformat(),
                "success": outcome.get("status") == "success",
            })

            if self.config.learning_enabled:
                self.logger.info("Outcome stored for continuous learning")

        except Exception as e:
            self.logger.error(f"Failed to store outcome: {e}")

    def coordinate_with_bots(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate with other AXIS bots

        Enables collaborative intelligence across 46-bot ecosystem

        Args:
            action: Coordination action (e.g., 'request_review', 'notify')
            context: Action context and parameters

        Returns:
            Coordination result
        """
        if not self.coordination_client:
            self.logger.warning("Coordination service unavailable")
            return {"status": "unavailable"}

        try:
            result = self.coordination_client.coordinate(
                agent=self.config.name,
                action=action,
                context=context
            )

            self.logger.info(f"Coordinated action '{action}' with ecosystem")
            return {"status": "success", "result": result}

        except Exception as e:
            self.logger.error(f"Coordination failed: {e}")
            return {"status": "error", "error": str(e)}

    def validate_togaf_compliance(self, action: Dict[str, Any]) -> bool:
        """
        Validate action against TOGAF 9.2 framework

        Args:
            action: Proposed action to validate

        Returns:
            True if compliant, False otherwise
        """
        if not self.config.togaf_compliance:
            return True  # Compliance checking disabled

        # Validate against TOGAF principles
        required_fields = ["architecture_domain", "governance_phase", "stakeholders"]

        for field in required_fields:
            if field not in action:
                self.logger.warning(f"TOGAF compliance check failed: missing {field}")
                return False

        self.logger.debug("TOGAF compliance validated")
        return True

    def start(self) -> None:
        """Start agent operation"""
        self.active = True
        self.logger.info(f"{self.config.name} started")

        if self.config.autonomous:
            self.logger.info("Autonomous operation mode enabled")

    def stop(self) -> None:
        """Stop agent operation"""
        self.active = False
        self.logger.info(
            f"{self.config.name} stopped",
            extra={"tasks_completed": self.task_count}
        )

    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status

        Returns:
            Current agent status and metrics
        """
        return {
            "name": self.config.name,
            "role": self.config.role,
            "active": self.active,
            "tasks_completed": self.task_count,
            "errors": len(self.errors),
            "version": self.config.version,
            "autonomous": self.config.autonomous,
        }
