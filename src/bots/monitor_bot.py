"""Monitoring and health check bot for PIPE domain."""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta

from ..core.bot_base import BotBase, BotStatus
from ..core.event_bus import Event, EventBus
from ..core.state_manager import StateManager
from ..utils.metrics import MetricsCollector


class MonitorBot(BotBase):
    """
    Bot for monitoring system health and performance.

    Tracks bot status, collects metrics, performs health checks,
    and sends alerts when issues are detected.
    """

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        event_bus: EventBus,
        state_manager: StateManager,
        metrics: MetricsCollector
    ):
        """
        Initialize the monitor bot.

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
        self.monitored_bots: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.health_checks: List[asyncio.Task] = []

    async def initialize(self) -> bool:
        """Initialize the monitor bot."""
        try:
            self.logger.info("Initializing MonitorBot")

            # Load saved state
            state = await self.state_manager.load_state(self.name)
            self.monitored_bots = state.get('monitored_bots', {})

            # Subscribe to bot status events
            self.event_bus.subscribe('bot.status', self._on_bot_status)
            self.event_bus.subscribe('bot.error', self._on_bot_error)
            self.event_bus.subscribe('pipeline.failed', self._on_pipeline_failed)
            self.event_bus.subscribe('data.processed', self._on_data_processed)

            # Start periodic health checks
            health_check_task = asyncio.create_task(self._periodic_health_checks())
            self.health_checks.append(health_check_task)

            self.logger.info("MonitorBot initialized")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize MonitorBot: {str(e)}")
            return False

    async def execute(self) -> None:
        """Main execution loop."""
        self.logger.info("MonitorBot execution started")

        while self.status.value == "running":
            try:
                # Analyze system health
                health_report = await self._analyze_system_health()

                # Check for alerts
                await self._check_alerts(health_report)

                # Publish monitoring report
                await self._publish_monitoring_report(health_report)

                # Clean up old alerts
                self._cleanup_old_alerts()

                # Sleep interval
                await asyncio.sleep(self.config.get('monitor_interval', 60))

            except Exception as e:
                self.logger.error(f"Error in execution loop: {str(e)}", exc_info=True)
                self.error_count += 1
                await asyncio.sleep(5)

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up MonitorBot")

        # Cancel health check tasks
        for task in self.health_checks:
            task.cancel()

        await asyncio.gather(*self.health_checks, return_exceptions=True)

        # Save state
        await self.state_manager.save_state(self.name, {
            'monitored_bots': self.monitored_bots
        })

        self.logger.info("MonitorBot cleanup complete")

    async def _periodic_health_checks(self) -> None:
        """Perform periodic health checks on all monitored bots."""
        while self.status.value == "running":
            try:
                self.logger.debug("Performing health checks")

                for bot_name, bot_info in self.monitored_bots.items():
                    await self._check_bot_health(bot_name, bot_info)

                await asyncio.sleep(self.config.get('health_check_interval', 30))

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health checks: {str(e)}", exc_info=True)

    async def _check_bot_health(self, bot_name: str, bot_info: Dict[str, Any]) -> None:
        """
        Check health of a specific bot.

        Args:
            bot_name: Name of the bot
            bot_info: Bot information dictionary
        """
        last_seen = bot_info.get('last_seen')
        if not last_seen:
            return

        # Check if bot has been silent for too long
        last_seen_time = datetime.fromisoformat(last_seen)
        silence_threshold = self.config.get('silence_threshold_seconds', 300)

        if (datetime.now() - last_seen_time).total_seconds() > silence_threshold:
            await self._create_alert(
                severity='warning',
                message=f"Bot {bot_name} has not reported status for {silence_threshold}s",
                bot_name=bot_name
            )

        # Check error rate
        error_count = bot_info.get('error_count', 0)
        error_threshold = self.config.get('error_threshold', 10)

        if error_count > error_threshold:
            await self._create_alert(
                severity='critical',
                message=f"Bot {bot_name} has {error_count} errors",
                bot_name=bot_name
            )

    async def _analyze_system_health(self) -> Dict[str, Any]:
        """
        Analyze overall system health.

        Returns:
            Health report dictionary
        """
        total_bots = len(self.monitored_bots)
        healthy_bots = sum(
            1 for bot in self.monitored_bots.values()
            if bot.get('status') == 'running'
        )
        unhealthy_bots = total_bots - healthy_bots

        # Get metrics
        all_metrics = self.metrics.get_all_metrics()

        health_score = (healthy_bots / total_bots * 100) if total_bots > 0 else 100

        return {
            'timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'total_bots': total_bots,
            'healthy_bots': healthy_bots,
            'unhealthy_bots': unhealthy_bots,
            'active_alerts': len(self.alerts),
            'metrics': all_metrics,
            'monitored_bots': {
                name: {
                    'status': info.get('status'),
                    'uptime': info.get('uptime_seconds'),
                    'error_count': info.get('error_count'),
                    'task_count': info.get('task_count')
                }
                for name, info in self.monitored_bots.items()
            }
        }

    async def _check_alerts(self, health_report: Dict[str, Any]) -> None:
        """
        Check if any alerts should be triggered.

        Args:
            health_report: System health report
        """
        health_score = health_report['health_score']

        # Check system health score
        if health_score < 50:
            await self._create_alert(
                severity='critical',
                message=f"System health score is low: {health_score:.1f}%"
            )
        elif health_score < 80:
            await self._create_alert(
                severity='warning',
                message=f"System health score is degraded: {health_score:.1f}%"
            )

    async def _create_alert(
        self,
        severity: str,
        message: str,
        bot_name: str = None
    ) -> None:
        """
        Create a new alert.

        Args:
            severity: Alert severity (info, warning, critical)
            message: Alert message
            bot_name: Optional bot name associated with alert
        """
        alert = {
            'id': f"alert_{len(self.alerts)}",
            'severity': severity,
            'message': message,
            'bot_name': bot_name,
            'timestamp': datetime.now().isoformat(),
            'acknowledged': False
        }

        self.alerts.append(alert)
        self.logger.warning(f"Alert created: [{severity}] {message}")

        # Publish alert event
        await self.event_bus.publish(Event(
            event_type='monitor.alert',
            source=self.name,
            data=alert
        ))

        self.metrics.increment(f'monitor.alerts.{severity}')

    async def _publish_monitoring_report(self, health_report: Dict[str, Any]) -> None:
        """
        Publish monitoring report to event bus.

        Args:
            health_report: Health report to publish
        """
        await self.event_bus.publish(Event(
            event_type='monitor.report',
            source=self.name,
            data=health_report
        ))

    def _cleanup_old_alerts(self) -> None:
        """Remove old resolved alerts."""
        max_age_hours = self.config.get('alert_retention_hours', 24)
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        self.alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]

    async def _on_bot_status(self, event: Event) -> None:
        """Handle bot status events."""
        bot_name = event.data.get('name')
        if not bot_name or bot_name == self.name:
            return

        # Update monitored bot info
        self.monitored_bots[bot_name] = {
            **event.data,
            'last_seen': datetime.now().isoformat()
        }

    async def _on_bot_error(self, event: Event) -> None:
        """Handle bot error events."""
        bot_name = event.source
        error_message = event.data.get('error', 'Unknown error')

        await self._create_alert(
            severity='warning',
            message=f"Bot {bot_name} reported error: {error_message}",
            bot_name=bot_name
        )

    async def _on_pipeline_failed(self, event: Event) -> None:
        """Handle pipeline failure events."""
        pipeline_id = event.data.get('pipeline_id')
        error = event.data.get('error', 'Unknown error')

        await self._create_alert(
            severity='warning',
            message=f"Pipeline {pipeline_id} failed: {error}",
            bot_name=event.source
        )

    async def _on_data_processed(self, event: Event) -> None:
        """Handle data processed events for metrics."""
        self.metrics.increment('monitor.data_items_tracked')

    def get_alerts(self, severity: str = None) -> List[Dict[str, Any]]:
        """
        Get current alerts.

        Args:
            severity: Optional filter by severity

        Returns:
            List of alerts
        """
        if severity:
            return [a for a in self.alerts if a['severity'] == severity]
        return self.alerts

    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: ID of the alert to acknowledge

        Returns:
            True if acknowledged, False if not found
        """
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_at'] = datetime.now().isoformat()
                return True
        return False
