"""Unit tests for monitoring metrics server."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase

from src.monitoring.metrics_server import MetricsServer
from src.monitoring.health_checker import HealthChecker
from src.utils.metrics import MetricsCollector


class TestMetricsServer(AioHTTPTestCase):
    """Test suite for MetricsServer using aiohttp test utilities."""

    async def get_application(self):
        """Create application for testing."""
        # Create mock dependencies
        self.metrics_collector = Mock(spec=MetricsCollector)
        self.health_checker = Mock(spec=HealthChecker)

        # Configure mock methods
        self.metrics_collector.get_all_metrics = Mock(return_value={
            "total_events": 100,
            "total_bots": 3,
        })

        self.health_checker.liveness_check = Mock(return_value={
            "status": "alive",
            "timestamp": "2024-01-01T00:00:00",
        })

        self.health_checker.readiness_check = Mock(return_value={
            "ready": True,
            "bots_running": 3,
        })

        self.health_checker.detailed_health_check = Mock(return_value={
            "status": "healthy",
            "bots": [],
            "governance": {},
            "metrics": {},
        })

        # Create server - save to metrics_server attribute
        self.metrics_server = MetricsServer(
            metrics_collector=self.metrics_collector,
            health_checker=self.health_checker,
            port=9999,
            host="127.0.0.1",
        )

        return self.metrics_server.app

    async def test_initialization(self):
        """Test server initialization."""
        assert self.metrics_server.port == 9999
        assert self.metrics_server.host == "127.0.0.1"
        assert self.metrics_server.metrics_collector is self.metrics_collector
        assert self.metrics_server.health_checker is self.health_checker
        assert self.metrics_server.bot_status_callback is None
        assert self.metrics_server.governance_dashboard_callback is None

    async def test_handle_index(self):
        """Test index endpoint returns HTML."""
        async with self.client.request("GET", "/") as resp:
            assert resp.status == 200
            assert resp.content_type == "text/html"
            text = await resp.text()
            assert "PIPE Metrics & Health Server" in text
            assert "/metrics" in text
            assert "/health" in text

    @patch("src.monitoring.metrics_server.PrometheusExporter")
    async def test_handle_metrics_basic(self, mock_prometheus_class):
        """Test /metrics endpoint with basic metrics."""
        # Mock prometheus exporter
        mock_prom = Mock()
        mock_prom.export_metrics.return_value = "# Basic metrics\ntest_metric 42"
        mock_prometheus_class.return_value = mock_prom

        # Recreate server with mocked prometheus
        self.metrics_server.prometheus = mock_prom

        async with self.client.request("GET", "/metrics") as resp:
            assert resp.status == 200
            assert resp.content_type == "text/plain"
            text = await resp.text()
            assert "test_metric 42" in text

    @patch("src.monitoring.metrics_server.PrometheusExporter")
    async def test_handle_metrics_with_bot_callback(self, mock_prometheus_class):
        """Test /metrics endpoint with bot status callback."""
        # Mock prometheus exporter
        mock_prom = Mock()
        mock_prom.export_metrics.return_value = "# Basic metrics"
        mock_prom.get_bot_metrics.return_value = "# Bot metrics\nbot_count 3"
        mock_prometheus_class.return_value = mock_prom

        self.metrics_server.prometheus = mock_prom

        # Set bot callback
        bot_statuses = [
            {"bot_id": "bot1", "status": "running"},
            {"bot_id": "bot2", "status": "running"},
        ]
        self.metrics_server.set_bot_status_callback(lambda: bot_statuses)

        async with self.client.request("GET", "/metrics") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "# Basic metrics" in text
            assert "bot_count 3" in text

    @patch("src.monitoring.metrics_server.PrometheusExporter")
    async def test_handle_metrics_with_async_bot_callback(self, mock_prometheus_class):
        """Test /metrics endpoint with async bot status callback."""
        mock_prom = Mock()
        mock_prom.export_metrics.return_value = "# Basic metrics"
        mock_prom.get_bot_metrics.return_value = "# Bot metrics"
        mock_prometheus_class.return_value = mock_prom

        self.metrics_server.prometheus = mock_prom

        # Set async bot callback
        async def async_bot_callback():
            return [{"bot_id": "bot1", "status": "running"}]

        self.metrics_server.set_bot_status_callback(async_bot_callback)

        async with self.client.request("GET", "/metrics") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "# Bot metrics" in text

    @patch("src.monitoring.metrics_server.PrometheusExporter")
    async def test_handle_metrics_with_governance_callback(self, mock_prometheus_class):
        """Test /metrics endpoint with governance dashboard callback."""
        mock_prom = Mock()
        mock_prom.export_metrics.return_value = "# Basic metrics"
        mock_prom.get_governance_metrics.return_value = "# Governance metrics\ntotal_domains 3"
        mock_prometheus_class.return_value = mock_prom

        self.metrics_server.prometheus = mock_prom

        # Set governance callback
        gov_dashboard = {"total_domains": 3, "total_integrations": 5}
        self.metrics_server.set_governance_dashboard_callback(lambda: gov_dashboard)

        async with self.client.request("GET", "/metrics") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "total_domains 3" in text

    @patch("src.monitoring.metrics_server.PrometheusExporter")
    async def test_handle_metrics_error(self, mock_prometheus_class):
        """Test /metrics endpoint error handling."""
        # Make prometheus export raise error
        mock_prom = Mock()
        mock_prom.export_metrics.side_effect = Exception("Export failed")
        mock_prometheus_class.return_value = mock_prom

        self.metrics_server.prometheus = mock_prom

        async with self.client.request("GET", "/metrics") as resp:
            assert resp.status == 500
            text = await resp.text()
            assert "Error generating metrics" in text

    async def test_handle_liveness_success(self):
        """Test /health/live endpoint success."""
        self.health_checker.liveness_check.return_value = {
            "status": "alive",
            "timestamp": "2024-01-01T00:00:00",
        }

        async with self.client.request("GET", "/health/live") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "alive"
            assert "timestamp" in data

    async def test_handle_liveness_error(self):
        """Test /health/live endpoint error handling."""
        self.health_checker.liveness_check.side_effect = Exception("Liveness check failed")

        async with self.client.request("GET", "/health/live") as resp:
            assert resp.status == 503
            data = await resp.json()
            assert data["status"] == "error"
            assert "Liveness check failed" in data["message"]

    async def test_handle_readiness_ready(self):
        """Test /health/ready endpoint when ready."""
        self.health_checker.readiness_check.return_value = {
            "ready": True,
            "bots_running": 3,
        }

        # Set bot callback
        self.metrics_server.set_bot_status_callback(lambda: [
            {"bot_id": "bot1", "status": "running"},
        ])

        async with self.client.request("GET", "/health/ready") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["ready"] is True

    async def test_handle_readiness_not_ready(self):
        """Test /health/ready endpoint when not ready."""
        self.health_checker.readiness_check.return_value = {
            "ready": False,
            "reason": "Bots not running",
        }

        self.metrics_server.set_bot_status_callback(lambda: [])

        async with self.client.request("GET", "/health/ready") as resp:
            assert resp.status == 503
            data = await resp.json()
            assert data["ready"] is False

    async def test_handle_readiness_error(self):
        """Test /health/ready endpoint error handling."""
        self.metrics_server.set_bot_status_callback(lambda: None)
        self.health_checker.readiness_check.side_effect = Exception("Readiness check failed")

        async with self.client.request("GET", "/health/ready") as resp:
            assert resp.status == 503
            data = await resp.json()
            assert data["ready"] is False
            assert "error" in data["status"]

    async def test_handle_health_healthy(self):
        """Test /health endpoint when system is healthy."""
        self.health_checker.detailed_health_check.return_value = {
            "status": "healthy",
            "bots": [{"bot_id": "bot1", "status": "running"}],
            "governance": {"total_domains": 3},
            "metrics": {"total_events": 100},
        }

        self.metrics_server.set_bot_status_callback(lambda: [{"bot_id": "bot1"}])
        self.metrics_server.set_governance_dashboard_callback(lambda: {"total_domains": 3})

        async with self.client.request("GET", "/health") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "healthy"
            assert "bots" in data
            assert "governance" in data

    async def test_handle_health_degraded(self):
        """Test /health endpoint when system is degraded."""
        self.health_checker.detailed_health_check.return_value = {
            "status": "degraded",
            "issues": ["Some bots not responding"],
        }

        self.metrics_server.set_bot_status_callback(lambda: [])
        self.metrics_server.set_governance_dashboard_callback(lambda: {})

        async with self.client.request("GET", "/health") as resp:
            assert resp.status == 200  # degraded still returns 200
            data = await resp.json()
            assert data["status"] == "degraded"

    async def test_handle_health_unhealthy(self):
        """Test /health endpoint when system is unhealthy."""
        self.health_checker.detailed_health_check.return_value = {
            "status": "unhealthy",
            "critical_issues": ["All bots down"],
        }

        self.metrics_server.set_bot_status_callback(lambda: [])
        self.metrics_server.set_governance_dashboard_callback(lambda: {})

        async with self.client.request("GET", "/health") as resp:
            assert resp.status == 503
            data = await resp.json()
            assert data["status"] == "unhealthy"

    async def test_handle_health_error(self):
        """Test /health endpoint error handling."""
        self.health_checker.detailed_health_check.side_effect = Exception("Health check failed")

        self.metrics_server.set_bot_status_callback(lambda: [])
        self.metrics_server.set_governance_dashboard_callback(lambda: {})

        async with self.client.request("GET", "/health") as resp:
            assert resp.status == 503
            data = await resp.json()
            assert data["status"] == "error"

    async def test_set_callbacks(self):
        """Test setting bot and governance callbacks."""
        bot_callback = lambda: [{"bot_id": "test"}]
        gov_callback = lambda: {"domains": 5}

        self.metrics_server.set_bot_status_callback(bot_callback)
        self.metrics_server.set_governance_dashboard_callback(gov_callback)

        assert self.metrics_server.bot_status_callback is bot_callback
        assert self.metrics_server.governance_dashboard_callback is gov_callback

    async def test_get_bot_statuses_no_callback(self):
        """Test _get_bot_statuses with no callback set."""
        result = await self.metrics_server._get_bot_statuses()
        assert result == []

    async def test_get_bot_statuses_sync_callback(self):
        """Test _get_bot_statuses with synchronous callback."""
        bot_statuses = [{"bot_id": "bot1"}]
        self.metrics_server.set_bot_status_callback(lambda: bot_statuses)

        result = await self.metrics_server._get_bot_statuses()
        assert result == bot_statuses

    async def test_get_bot_statuses_async_callback(self):
        """Test _get_bot_statuses with asynchronous callback."""
        async def async_callback():
            return [{"bot_id": "bot1"}]

        self.metrics_server.set_bot_status_callback(async_callback)

        result = await self.metrics_server._get_bot_statuses()
        assert result == [{"bot_id": "bot1"}]

    async def test_get_governance_dashboard_no_callback(self):
        """Test _get_governance_dashboard with no callback set."""
        result = await self.metrics_server._get_governance_dashboard()
        assert result == {}

    async def test_get_governance_dashboard_sync_callback(self):
        """Test _get_governance_dashboard with synchronous callback."""
        dashboard = {"total_domains": 5}
        self.metrics_server.set_governance_dashboard_callback(lambda: dashboard)

        result = await self.metrics_server._get_governance_dashboard()
        assert result == dashboard

    async def test_get_governance_dashboard_async_callback(self):
        """Test _get_governance_dashboard with asynchronous callback."""
        async def async_callback():
            return {"total_domains": 5}

        self.metrics_server.set_governance_dashboard_callback(async_callback)

        result = await self.metrics_server._get_governance_dashboard()
        assert result == {"total_domains": 5}


# Separate tests for start/stop that don't use AioHTTPTestCase
@pytest.mark.asyncio
async def test_server_start_stop():
    """Test server start and stop lifecycle."""
    metrics_collector = Mock(spec=MetricsCollector)
    health_checker = Mock(spec=HealthChecker)

    server = MetricsServer(
        metrics_collector=metrics_collector,
        health_checker=health_checker,
        port=19999,  # Use high port to avoid conflicts
        host="127.0.0.1",
    )

    # Start server
    await server.start()
    assert server.runner is not None
    assert server.site is not None

    # Stop server
    await server.stop()

    # Verify cleanup was called
    # (We can't easily check if runner.cleanup() was called without more mocking)
