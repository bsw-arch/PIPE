"""
Health Check System for PIPE.

Provides health check endpoints for load balancers,
orchestrators, and monitoring systems.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthChecker:
    """
    Comprehensive health checking system.

    Provides liveness, readiness, and detailed health checks
    for the PIPE bot system.
    """

    def __init__(self):
        """Initialize health checker."""
        self.logger = logging.getLogger("pipe.monitoring.health")
        self.start_time = datetime.now()
        self.last_health_check = None
        self.health_history: List[Dict[str, Any]] = []
        self.max_history = 100

    def liveness_check(self) -> Dict[str, Any]:
        """
        Liveness probe - is the application alive?

        This is a simple check that the application is running.
        Used by Kubernetes/Docker for liveness probes.

        Returns:
            Liveness status
        """
        return {
            "status": "alive",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": self._get_uptime_seconds(),
        }

    def readiness_check(
        self, bot_statuses: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Readiness probe - is the application ready to serve traffic?

        Checks if all critical components are initialized and ready.
        Used by Kubernetes/Docker for readiness probes.

        Args:
            bot_statuses: Optional list of bot statuses

        Returns:
            Readiness status
        """
        ready = True
        reasons = []

        # Check if any bots are in error state
        if bot_statuses:
            error_bots = [bot for bot in bot_statuses if bot.get("status") == "error"]
            if error_bots:
                ready = False
                reasons.append(
                    f"{len(error_bots)} bot(s) in error state: "
                    f"{[bot['name'] for bot in error_bots]}"
                )

            # Check if minimum bots are running
            running_bots = [
                bot for bot in bot_statuses if bot.get("status") == "running"
            ]
            if len(running_bots) == 0:
                ready = False
                reasons.append("No bots are running")

        return {
            "status": "ready" if ready else "not_ready",
            "ready": ready,
            "timestamp": datetime.now().isoformat(),
            "reasons": reasons if reasons else ["All systems operational"],
        }

    def detailed_health_check(
        self,
        bot_statuses: Optional[List[Dict[str, Any]]] = None,
        governance_dashboard: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Detailed health check with component breakdown.

        Provides comprehensive health information including:
        - Overall health status
        - Individual component health
        - Performance metrics
        - Resource utilization

        Args:
            bot_statuses: Optional list of bot statuses
            governance_dashboard: Optional governance dashboard data
            metrics: Optional metrics data

        Returns:
            Detailed health status
        """
        health_data = {
            "status": HealthStatus.HEALTHY.value,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": self._get_uptime_seconds(),
            "components": {},
            "metrics": {},
            "issues": [],
        }

        # Check bot health
        if bot_statuses:
            bot_health = self._check_bot_health(bot_statuses)
            health_data["components"]["bots"] = bot_health

            if bot_health["status"] != HealthStatus.HEALTHY.value:
                health_data["status"] = bot_health["status"]
                health_data["issues"].extend(bot_health.get("issues", []))

        # Check governance health
        if governance_dashboard:
            gov_health = self._check_governance_health(governance_dashboard)
            health_data["components"]["governance"] = gov_health

            if gov_health["status"] != HealthStatus.HEALTHY.value:
                # Degrade overall status if needed
                if (
                    health_data["status"] == HealthStatus.HEALTHY.value
                    or gov_health["status"] == HealthStatus.UNHEALTHY.value
                ):
                    health_data["status"] = gov_health["status"]
                health_data["issues"].extend(gov_health.get("issues", []))

        # Add metrics summary
        if metrics:
            health_data["metrics"] = self._extract_key_metrics(metrics)

        # Record health check
        self.last_health_check = datetime.now()
        self._record_health_check(health_data)

        return health_data

    def _check_bot_health(self, bot_statuses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check health of bot system."""
        total_bots = len(bot_statuses)
        running_bots = sum(1 for bot in bot_statuses if bot.get("status") == "running")
        error_bots = sum(1 for bot in bot_statuses if bot.get("status") == "error")
        total_errors = sum(bot.get("error_count", 0) for bot in bot_statuses)

        issues = []
        status = HealthStatus.HEALTHY.value

        # Determine health status
        if error_bots > 0:
            status = HealthStatus.DEGRADED.value
            issues.append(f"{error_bots} bot(s) in error state")

        if running_bots == 0:
            status = HealthStatus.UNHEALTHY.value
            issues.append("No bots are running")

        if total_errors > 100:
            if status == HealthStatus.HEALTHY.value:
                status = HealthStatus.DEGRADED.value
            issues.append(f"High error count: {total_errors} total errors")

        return {
            "status": status,
            "total_bots": total_bots,
            "running_bots": running_bots,
            "error_bots": error_bots,
            "total_errors": total_errors,
            "issues": issues,
        }

    def _check_governance_health(
        self, governance_dashboard: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check health of governance system."""
        ecosystem = governance_dashboard.get("ecosystem", {})
        compliance = governance_dashboard.get("compliance", {})
        reviews = governance_dashboard.get("reviews", {})

        issues = []
        status = HealthStatus.HEALTHY.value

        # Check compliance
        compliance_pct = compliance.get("ecosystem_percentage", 0)
        if compliance_pct < 50:
            status = HealthStatus.DEGRADED.value
            issues.append(f"Low compliance: {compliance_pct:.1f}%")
        elif compliance_pct < 30:
            status = HealthStatus.UNHEALTHY.value
            issues.append(f"Critical compliance: {compliance_pct:.1f}%")

        # Check review backlog
        pending_reviews = reviews.get("pending", 0)
        if pending_reviews > 10:
            if status == HealthStatus.HEALTHY.value:
                status = HealthStatus.DEGRADED.value
            issues.append(f"High review backlog: {pending_reviews} pending")

        return {
            "status": status,
            "active_domains": ecosystem.get("active_domains", 0),
            "active_integrations": ecosystem.get("active_integrations", 0),
            "compliance_percentage": compliance_pct,
            "pending_reviews": pending_reviews,
            "issues": issues,
        }

    def _extract_key_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics for health summary."""
        key_metrics = {}

        # Extract important counters
        for key in ["events_published", "events_processed", "tasks_completed"]:
            if key in metrics:
                key_metrics[key] = metrics[key]

        # Extract gauges
        if "gauges" in metrics:
            key_metrics["gauges"] = metrics["gauges"]

        return key_metrics

    def _get_uptime_seconds(self) -> float:
        """Get application uptime in seconds."""
        delta = datetime.now() - self.start_time
        return delta.total_seconds()

    def _record_health_check(self, health_data: Dict[str, Any]) -> None:
        """Record health check in history."""
        self.health_history.append(
            {
                "timestamp": health_data["timestamp"],
                "status": health_data["status"],
                "issue_count": len(health_data.get("issues", [])),
            }
        )

        # Trim history if needed
        if len(self.health_history) > self.max_history:
            self.health_history = self.health_history[-self.max_history :]

    def get_health_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent health check history.

        Args:
            limit: Maximum number of history entries to return

        Returns:
            List of health check records
        """
        return self.health_history[-limit:]

    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get summary of health check history.

        Returns:
            Health summary statistics
        """
        if not self.health_history:
            return {
                "total_checks": 0,
                "last_check": None,
                "status_distribution": {},
            }

        status_counts = {}
        for entry in self.health_history:
            status = entry["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_checks": len(self.health_history),
            "last_check": (
                self.health_history[-1]["timestamp"] if self.health_history else None
            ),
            "status_distribution": status_counts,
            "healthy_percentage": (
                100
                * status_counts.get(HealthStatus.HEALTHY.value, 0)
                / len(self.health_history)
            ),
        }
