"""
Prometheus Metrics Exporter for PIPE.

Converts internal metrics to Prometheus format and provides
HTTP endpoint for metrics scraping.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from ..utils.metrics import MetricsCollector


class PrometheusExporter:
    """
    Export metrics in Prometheus format.

    Converts MetricsCollector data to Prometheus text format
    for scraping by Prometheus server.
    """

    def __init__(self, metrics_collector: MetricsCollector, namespace: str = "pipe"):
        """
        Initialize Prometheus exporter.

        Args:
            metrics_collector: MetricsCollector instance to export from
            namespace: Metric namespace prefix (default: pipe)
        """
        self.metrics = metrics_collector
        self.namespace = namespace
        self.logger = logging.getLogger("pipe.monitoring.prometheus")

    def export_metrics(self) -> str:
        """
        Export all metrics in Prometheus text format.

        Returns:
            Prometheus-formatted metrics string
        """
        lines = []

        # Add header comment
        lines.append("# PIPE Bot System Metrics")
        lines.append(f"# Generated at {datetime.now().isoformat()}")
        lines.append("")

        # Get all metrics
        all_metrics = self.metrics.get_all_metrics()

        # Export counters
        if "counters" in all_metrics:
            for metric_name, value in all_metrics["counters"].items():
                prom_name = self._sanitize_metric_name(metric_name)
                lines.append(f"# TYPE {self.namespace}_{prom_name} counter")
                lines.append(f"{self.namespace}_{prom_name} {value}")
                lines.append("")

        # Export gauges
        if "gauges" in all_metrics:
            for metric_name, value in all_metrics["gauges"].items():
                prom_name = self._sanitize_metric_name(metric_name)
                lines.append(f"# TYPE {self.namespace}_{prom_name} gauge")
                lines.append(f"{self.namespace}_{prom_name} {value}")
                lines.append("")

        # Export timing metrics as summaries
        if "timings" in all_metrics:
            for metric_name, timing_stats in all_metrics["timings"].items():
                prom_name = self._sanitize_metric_name(metric_name)

                # timing_stats is a dict with min, max, avg, count
                if timing_stats:
                    count = timing_stats.get("count", 0)
                    total = timing_stats.get("sum", timing_stats.get("avg", 0) * count)
                    avg = timing_stats.get("avg", 0)

                    lines.append(f"# TYPE {self.namespace}_{prom_name} summary")
                    lines.append(f"{self.namespace}_{prom_name}_count {count}")
                    lines.append(f"{self.namespace}_{prom_name}_sum {total:.6f}")
                    lines.append(f"{self.namespace}_{prom_name}_avg {avg:.6f}")
                    lines.append("")

        return "\n".join(lines)

    def export_custom_metrics(self, custom_metrics: Dict[str, Any]) -> str:
        """
        Export custom metrics in Prometheus format.

        Args:
            custom_metrics: Dictionary of custom metrics to export

        Returns:
            Prometheus-formatted metrics string
        """
        lines = []

        for metric_name, metric_data in custom_metrics.items():
            prom_name = self._sanitize_metric_name(metric_name)

            if isinstance(metric_data, dict) and "type" in metric_data:
                metric_type = metric_data["type"]
                value = metric_data.get("value", 0)
                labels = metric_data.get("labels", {})

                lines.append(f"# TYPE {self.namespace}_{prom_name} {metric_type}")

                if labels:
                    label_str = self._format_labels(labels)
                    lines.append(f"{self.namespace}_{prom_name}{{{label_str}}} {value}")
                else:
                    lines.append(f"{self.namespace}_{prom_name} {value}")
                lines.append("")
            else:
                # Simple metric without type
                lines.append(f"# TYPE {self.namespace}_{prom_name} gauge")
                lines.append(f"{self.namespace}_{prom_name} {metric_data}")
                lines.append("")

        return "\n".join(lines)

    def get_bot_metrics(self, bot_statuses: List[Dict[str, Any]]) -> str:
        """
        Export bot-specific metrics.

        Args:
            bot_statuses: List of bot status dictionaries

        Returns:
            Prometheus-formatted bot metrics
        """
        lines = []

        # Bot status gauge
        lines.append(
            "# HELP pipe_bot_status Bot operational status (1=running, 0=other)"
        )
        lines.append("# TYPE pipe_bot_status gauge")

        for bot in bot_statuses:
            bot_name = bot.get("name", "unknown")
            status = bot.get("status", "unknown")
            status_value = 1 if status == "running" else 0

            lines.append(
                f'pipe_bot_status{{bot="{bot_name}",status="{status}"}} {status_value}'
            )

        lines.append("")

        # Bot uptime
        lines.append("# HELP pipe_bot_uptime_seconds Bot uptime in seconds")
        lines.append("# TYPE pipe_bot_uptime_seconds gauge")

        for bot in bot_statuses:
            bot_name = bot.get("name", "unknown")
            uptime = bot.get("uptime_seconds", 0)
            lines.append(f'pipe_bot_uptime_seconds{{bot="{bot_name}"}} {uptime}')

        lines.append("")

        # Bot task count
        lines.append("# HELP pipe_bot_tasks_total Total tasks processed by bot")
        lines.append("# TYPE pipe_bot_tasks_total counter")

        for bot in bot_statuses:
            bot_name = bot.get("name", "unknown")
            task_count = bot.get("task_count", 0)
            lines.append(f'pipe_bot_tasks_total{{bot="{bot_name}"}} {task_count}')

        lines.append("")

        # Bot error count
        lines.append("# HELP pipe_bot_errors_total Total errors encountered by bot")
        lines.append("# TYPE pipe_bot_errors_total counter")

        for bot in bot_statuses:
            bot_name = bot.get("name", "unknown")
            error_count = bot.get("error_count", 0)
            lines.append(f'pipe_bot_errors_total{{bot="{bot_name}"}} {error_count}')

        lines.append("")

        return "\n".join(lines)

    def get_governance_metrics(self, governance_dashboard: Dict[str, Any]) -> str:
        """
        Export governance-specific metrics.

        Args:
            governance_dashboard: Governance dashboard data

        Returns:
            Prometheus-formatted governance metrics
        """
        lines = []

        ecosystem = governance_dashboard.get("ecosystem", {})
        compliance = governance_dashboard.get("compliance", {})
        reviews = governance_dashboard.get("reviews", {})

        # Ecosystem metrics
        lines.append("# HELP pipe_governance_domains_total Total domains in ecosystem")
        lines.append("# TYPE pipe_governance_domains_total gauge")
        lines.append(
            f"pipe_governance_domains_total {ecosystem.get('total_domains', 0)}"
        )
        lines.append("")

        lines.append("# HELP pipe_governance_domains_active Active domains")
        lines.append("# TYPE pipe_governance_domains_active gauge")
        lines.append(
            f"pipe_governance_domains_active {ecosystem.get('active_domains', 0)}"
        )
        lines.append("")

        lines.append("# HELP pipe_governance_integrations_total Total integrations")
        lines.append("# TYPE pipe_governance_integrations_total gauge")
        lines.append(
            f"pipe_governance_integrations_total {ecosystem.get('total_integrations', 0)}"
        )
        lines.append("")

        lines.append("# HELP pipe_governance_integrations_active Active integrations")
        lines.append("# TYPE pipe_governance_integrations_active gauge")
        lines.append(
            f"pipe_governance_integrations_active {ecosystem.get('active_integrations', 0)}"
        )
        lines.append("")

        # Compliance metrics
        lines.append(
            "# HELP pipe_governance_compliance_percentage Ecosystem compliance percentage"
        )
        lines.append("# TYPE pipe_governance_compliance_percentage gauge")
        lines.append(
            f"pipe_governance_compliance_percentage {compliance.get('ecosystem_percentage', 0)}"
        )
        lines.append("")

        # Review metrics
        lines.append("# HELP pipe_governance_reviews_total Total reviews")
        lines.append("# TYPE pipe_governance_reviews_total gauge")
        lines.append(f"pipe_governance_reviews_total {reviews.get('total', 0)}")
        lines.append("")

        lines.append("# HELP pipe_governance_reviews_pending Pending reviews")
        lines.append("# TYPE pipe_governance_reviews_pending gauge")
        lines.append(f"pipe_governance_reviews_pending {reviews.get('pending', 0)}")
        lines.append("")

        lines.append("# HELP pipe_governance_reviews_approved Approved reviews")
        lines.append("# TYPE pipe_governance_reviews_approved gauge")
        lines.append(f"pipe_governance_reviews_approved {reviews.get('approved', 0)}")
        lines.append("")

        return "\n".join(lines)

    def _sanitize_metric_name(self, name: str) -> str:
        """
        Sanitize metric name for Prometheus.

        Args:
            name: Original metric name

        Returns:
            Sanitized metric name
        """
        # Replace dots with underscores
        name = name.replace(".", "_")
        # Remove any invalid characters
        name = "".join(c if c.isalnum() or c == "_" else "_" for c in name)
        # Ensure it doesn't start with a number
        if name and name[0].isdigit():
            name = "_" + name
        return name.lower()

    def _format_labels(self, labels: Dict[str, str]) -> str:
        """
        Format labels for Prometheus.

        Args:
            labels: Dictionary of label key-value pairs

        Returns:
            Formatted label string
        """
        label_pairs = [f'{key}="{value}"' for key, value in labels.items()]
        return ",".join(label_pairs)
