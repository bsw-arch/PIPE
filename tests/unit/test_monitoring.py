"""Unit tests for monitoring components."""

import pytest
from src.monitoring.prometheus_exporter import PrometheusExporter
from src.monitoring.health_checker import HealthChecker, HealthStatus
from src.monitoring.structured_logger import JSONFormatter, ContextLogger
from src.utils.metrics import MetricsCollector
import logging
import json


def test_prometheus_exporter_basic_metrics(metrics_collector):
    """Test basic Prometheus metrics export."""
    # Add some test metrics
    metrics_collector.increment("test_counter", 5)
    metrics_collector.gauge("test_gauge", 42)

    # Create exporter
    exporter = PrometheusExporter(metrics_collector, namespace="test")

    # Export metrics
    output = exporter.export_metrics()

    # Verify format
    assert "# TYPE test_test_counter counter" in output
    assert "test_test_counter 5" in output
    assert "# TYPE test_test_gauge gauge" in output
    assert "test_test_gauge 42" in output


def test_prometheus_exporter_bot_metrics():
    """Test bot metrics export."""
    metrics = MetricsCollector()
    exporter = PrometheusExporter(metrics)

    bot_statuses = [
        {
            "name": "test_bot",
            "status": "running",
            "uptime_seconds": 100,
            "task_count": 50,
            "error_count": 2,
        }
    ]

    output = exporter.get_bot_metrics(bot_statuses)

    assert "pipe_bot_status" in output
    assert 'bot="test_bot"' in output
    assert "pipe_bot_uptime_seconds" in output
    assert "pipe_bot_tasks_total" in output
    assert "pipe_bot_errors_total" in output


def test_prometheus_exporter_governance_metrics():
    """Test governance metrics export."""
    metrics = MetricsCollector()
    exporter = PrometheusExporter(metrics)

    dashboard = {
        "ecosystem": {
            "total_domains": 5,
            "active_domains": 3,
            "total_integrations": 4,
            "active_integrations": 2,
        },
        "compliance": {"ecosystem_percentage": 75.5},
        "reviews": {"total": 10, "pending": 3, "approved": 7},
    }

    output = exporter.get_governance_metrics(dashboard)

    assert "pipe_governance_domains_total 5" in output
    assert "pipe_governance_domains_active 3" in output
    assert "pipe_governance_compliance_percentage 75.5" in output
    assert "pipe_governance_reviews_pending 3" in output


def test_prometheus_exporter_sanitize_names():
    """Test metric name sanitization."""
    metrics = MetricsCollector()
    exporter = PrometheusExporter(metrics)

    # Test various names
    assert exporter._sanitize_metric_name("test.metric") == "test_metric"
    assert exporter._sanitize_metric_name("test-metric") == "test_metric"
    assert exporter._sanitize_metric_name("123metric") == "_123metric"
    assert exporter._sanitize_metric_name("test metric") == "test_metric"


def test_health_checker_liveness():
    """Test liveness probe."""
    checker = HealthChecker()
    result = checker.liveness_check()

    assert result["status"] == "alive"
    assert "timestamp" in result
    assert "uptime_seconds" in result
    assert result["uptime_seconds"] >= 0


def test_health_checker_readiness_healthy():
    """Test readiness probe with healthy bots."""
    checker = HealthChecker()

    bot_statuses = [
        {"name": "bot1", "status": "running"},
        {"name": "bot2", "status": "running"},
    ]

    result = checker.readiness_check(bot_statuses)

    assert result["ready"] is True
    assert result["status"] == "ready"
    assert "All systems operational" in result["reasons"]


def test_health_checker_readiness_unhealthy():
    """Test readiness probe with error bots."""
    checker = HealthChecker()

    bot_statuses = [
        {"name": "bot1", "status": "error"},
        {"name": "bot2", "status": "stopped"},
    ]

    result = checker.readiness_check(bot_statuses)

    assert result["ready"] is False
    assert result["status"] == "not_ready"
    assert len(result["reasons"]) > 0


def test_health_checker_detailed():
    """Test detailed health check."""
    checker = HealthChecker()

    bot_statuses = [
        {"name": "bot1", "status": "running", "error_count": 0},
        {"name": "bot2", "status": "running", "error_count": 1},
    ]

    governance_dashboard = {
        "ecosystem": {"total_domains": 5, "active_domains": 5},
        "compliance": {"ecosystem_percentage": 85.5},
        "reviews": {"total": 10, "pending": 2, "approved": 8},
    }

    result = checker.detailed_health_check(
        bot_statuses=bot_statuses, governance_dashboard=governance_dashboard
    )

    assert result["status"] == HealthStatus.HEALTHY.value
    assert "components" in result
    assert "bots" in result["components"]
    assert "governance" in result["components"]
    assert result["components"]["bots"]["total_bots"] == 2
    assert result["components"]["bots"]["running_bots"] == 2


def test_health_checker_degraded_compliance():
    """Test health checker with low compliance."""
    checker = HealthChecker()

    governance_dashboard = {
        "ecosystem": {},
        "compliance": {"ecosystem_percentage": 45.0},  # Below 50%
        "reviews": {"total": 5, "pending": 1, "approved": 4},
    }

    result = checker.detailed_health_check(governance_dashboard=governance_dashboard)

    assert result["status"] == HealthStatus.DEGRADED.value
    assert len(result["issues"]) > 0


def test_health_checker_history():
    """Test health check history tracking."""
    checker = HealthChecker()

    # Perform multiple checks
    for i in range(5):
        checker.detailed_health_check()

    history = checker.get_health_history()
    assert len(history) == 5

    summary = checker.get_health_summary()
    assert summary["total_checks"] == 5
    assert "status_distribution" in summary


def test_json_formatter():
    """Test JSON log formatter."""
    formatter = JSONFormatter()

    # Create a log record
    logger = logging.getLogger("test")
    record = logger.makeRecord(
        "test",
        logging.INFO,
        "test.py",
        10,
        "Test message",
        None,
        None,
        "test_function",
    )

    # Format the record
    output = formatter.format(record)

    # Parse JSON
    log_data = json.loads(output)

    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Test message"
    assert log_data["logger"] == "test"
    assert log_data["function"] == "test_function"
    assert "timestamp" in log_data


def test_json_formatter_with_exception():
    """Test JSON formatter with exception."""
    formatter = JSONFormatter()

    logger = logging.getLogger("test")

    try:
        raise ValueError("Test error")
    except ValueError:
        import sys

        record = logger.makeRecord(
            "test",
            logging.ERROR,
            "test.py",
            10,
            "Error occurred",
            None,
            sys.exc_info(),
            "test_function",
        )

        output = formatter.format(record)
        log_data = json.loads(output)

        assert "exception" in log_data
        assert log_data["exception"]["type"] == "ValueError"
        assert "Test error" in log_data["exception"]["message"]


def test_context_logger():
    """Test context logger."""
    base_logger = logging.getLogger("test")
    context_logger = ContextLogger(base_logger, context={"service": "test"})

    # Add context
    context_logger.add_context(request_id="123")

    assert context_logger.context["service"] == "test"
    assert context_logger.context["request_id"] == "123"

    # Remove context
    context_logger.remove_context("request_id")
    assert "request_id" not in context_logger.context

    # Clear context
    context_logger.clear_context()
    assert len(context_logger.context) == 0
