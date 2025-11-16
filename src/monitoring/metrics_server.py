"""
Metrics and Health HTTP Server for PIPE.

Provides HTTP endpoints for Prometheus metrics scraping
and health checks (liveness/readiness probes).
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable
from aiohttp import web

from .prometheus_exporter import PrometheusExporter
from .health_checker import HealthChecker
from ..utils.metrics import MetricsCollector


class MetricsServer:
    """
    HTTP server for metrics and health endpoints.

    Exposes:
    - /metrics - Prometheus metrics endpoint
    - /health/live - Liveness probe
    - /health/ready - Readiness probe
    - /health - Detailed health check
    """

    def __init__(
        self,
        metrics_collector: MetricsCollector,
        health_checker: HealthChecker,
        port: int = 9090,
        host: str = "0.0.0.0",
    ):
        """
        Initialize metrics server.

        Args:
            metrics_collector: MetricsCollector instance
            health_checker: HealthChecker instance
            port: Port to listen on (default: 9090)
            host: Host to bind to (default: 0.0.0.0)
        """
        self.metrics_collector = metrics_collector
        self.health_checker = health_checker
        self.port = port
        self.host = host
        self.logger = logging.getLogger("pipe.monitoring.server")

        # Create Prometheus exporter
        self.prometheus = PrometheusExporter(metrics_collector)

        # Callbacks for fetching current state
        self.bot_status_callback: Optional[Callable] = None
        self.governance_dashboard_callback: Optional[Callable] = None

        # Create web application
        self.app = web.Application()
        self._setup_routes()

        # Server runner
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None

    def _setup_routes(self) -> None:
        """Setup HTTP routes."""
        self.app.router.add_get("/metrics", self.handle_metrics)
        self.app.router.add_get("/health/live", self.handle_liveness)
        self.app.router.add_get("/health/ready", self.handle_readiness)
        self.app.router.add_get("/health", self.handle_health)
        self.app.router.add_get("/", self.handle_index)

    def set_bot_status_callback(self, callback: Callable) -> None:
        """
        Set callback for fetching bot statuses.

        Args:
            callback: Function that returns list of bot status dicts
        """
        self.bot_status_callback = callback

    def set_governance_dashboard_callback(self, callback: Callable) -> None:
        """
        Set callback for fetching governance dashboard.

        Args:
            callback: Function that returns governance dashboard dict
        """
        self.governance_dashboard_callback = callback

    async def handle_metrics(self, request: web.Request) -> web.Response:
        """
        Handle /metrics endpoint (Prometheus scraping).

        Args:
            request: HTTP request

        Returns:
            Prometheus-formatted metrics response
        """
        try:
            # Export basic metrics
            metrics_text = self.prometheus.export_metrics()

            # Add bot metrics if available
            if self.bot_status_callback:
                bot_statuses = await self._get_bot_statuses()
                bot_metrics = self.prometheus.get_bot_metrics(bot_statuses)
                metrics_text += "\n" + bot_metrics

            # Add governance metrics if available
            if self.governance_dashboard_callback:
                gov_dashboard = await self._get_governance_dashboard()
                gov_metrics = self.prometheus.get_governance_metrics(gov_dashboard)
                metrics_text += "\n" + gov_metrics

            return web.Response(
                text=metrics_text,
                content_type="text/plain; version=0.0.4",
                charset="utf-8",
            )
        except Exception as e:
            self.logger.error(f"Error generating metrics: {str(e)}", exc_info=True)
            return web.Response(
                text=f"Error generating metrics: {str(e)}",
                status=500,
                content_type="text/plain",
            )

    async def handle_liveness(self, request: web.Request) -> web.Response:
        """
        Handle /health/live endpoint (Kubernetes liveness probe).

        Args:
            request: HTTP request

        Returns:
            Liveness status (200 = alive, 503 = dead)
        """
        try:
            liveness = self.health_checker.liveness_check()
            return web.json_response(liveness, status=200)
        except Exception as e:
            self.logger.error(f"Liveness check failed: {str(e)}", exc_info=True)
            return web.json_response({"status": "error", "message": str(e)}, status=503)

    async def handle_readiness(self, request: web.Request) -> web.Response:
        """
        Handle /health/ready endpoint (Kubernetes readiness probe).

        Args:
            request: HTTP request

        Returns:
            Readiness status (200 = ready, 503 = not ready)
        """
        try:
            bot_statuses = await self._get_bot_statuses()
            readiness = self.health_checker.readiness_check(bot_statuses)

            status_code = 200 if readiness["ready"] else 503
            return web.json_response(readiness, status=status_code)
        except Exception as e:
            self.logger.error(f"Readiness check failed: {str(e)}", exc_info=True)
            return web.json_response(
                {"status": "error", "ready": False, "message": str(e)}, status=503
            )

    async def handle_health(self, request: web.Request) -> web.Response:
        """
        Handle /health endpoint (detailed health check).

        Args:
            request: HTTP request

        Returns:
            Detailed health status
        """
        try:
            bot_statuses = await self._get_bot_statuses()
            gov_dashboard = await self._get_governance_dashboard()
            metrics = self.metrics_collector.get_all_metrics()

            health = self.health_checker.detailed_health_check(
                bot_statuses=bot_statuses,
                governance_dashboard=gov_dashboard,
                metrics=metrics,
            )

            # Return 200 for healthy/degraded, 503 for unhealthy
            status_code = 200 if health["status"] != "unhealthy" else 503
            return web.json_response(health, status=status_code)
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}", exc_info=True)
            return web.json_response({"status": "error", "message": str(e)}, status=503)

    async def handle_index(self, request: web.Request) -> web.Response:
        """
        Handle / endpoint (index page with links).

        Args:
            request: HTTP request

        Returns:
            HTML index page
        """
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>PIPE Metrics & Health</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                }
                h1 { color: #333; }
                ul { list-style-type: none; padding: 0; }
                li { margin: 10px 0; }
                a {
                    color: #007bff;
                    text-decoration: none;
                    padding: 5px 10px;
                    border: 1px solid #007bff;
                    border-radius: 3px;
                    display: inline-block;
                }
                a:hover { background-color: #007bff; color: white; }
                .description { color: #666; margin-left: 10px; }
            </style>
        </head>
        <body>
            <h1>PIPE Metrics & Health Server</h1>
            <p>Available endpoints:</p>
            <ul>
                <li>
                    <a href="/metrics">/metrics</a>
                    <span class="description">Prometheus metrics (text format)</span>
                </li>
                <li>
                    <a href="/health/live">/health/live</a>
                    <span class="description">Liveness probe (JSON)</span>
                </li>
                <li>
                    <a href="/health/ready">/health/ready</a>
                    <span class="description">Readiness probe (JSON)</span>
                </li>
                <li>
                    <a href="/health">/health</a>
                    <span class="description">Detailed health check (JSON)</span>
                </li>
            </ul>
            <hr>
            <p style="color: #999; font-size: 12px;">
                PIPE Bot System - Monitoring & Observability
            </p>
        </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")

    async def _get_bot_statuses(self) -> List[Dict[str, Any]]:
        """Get bot statuses from callback."""
        if self.bot_status_callback:
            result = self.bot_status_callback()
            # Handle both sync and async callbacks
            if asyncio.iscoroutine(result):
                return await result
            return result
        return []

    async def _get_governance_dashboard(self) -> Dict[str, Any]:
        """Get governance dashboard from callback."""
        if self.governance_dashboard_callback:
            result = self.governance_dashboard_callback()
            # Handle both sync and async callbacks
            if asyncio.iscoroutine(result):
                return await result
            return result
        return {}

    async def start(self) -> None:
        """Start the metrics server."""
        self.logger.info(f"Starting metrics server on {self.host}:{self.port}")

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()

        self.logger.info(f"Metrics server running at http://{self.host}:{self.port}")
        self.logger.info(f"  Metrics: http://{self.host}:{self.port}/metrics")
        self.logger.info(f"  Health:  http://{self.host}:{self.port}/health")

    async def stop(self) -> None:
        """Stop the metrics server."""
        self.logger.info("Stopping metrics server")

        if self.runner:
            await self.runner.cleanup()

        self.logger.info("Metrics server stopped")
