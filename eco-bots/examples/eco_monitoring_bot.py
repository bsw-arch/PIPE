#!/usr/bin/env python3
"""
ECO Monitoring Bot - Resource Monitoring and Health Checks
Part of the BSW-Arch Bot Factory ECO Domain

Monitors resource usage across all bots and provides health status
"""

import sys
import os
import time
import logging
from pathlib import Path
from typing import Dict, Optional

# Add bot-utils to path
sys.path.insert(0, "/opt/documentation/bot-utils")

try:
    from doc_scanner import DocScanner
    from prometheus_client import start_http_server, Gauge, Counter, Histogram
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Ensure prometheus_client is installed: pip install prometheus-client")
    sys.exit(1)


class EcoMonitoringBot:
    """
    ECO Monitoring Bot

    Responsibilities:
    - Monitor CPU, memory, disk, network usage
    - Perform health checks on all bots
    - Export metrics to Prometheus
    - Alert on threshold violations
    - Provide status dashboard data
    """

    def __init__(self, docs_path: str = "/opt/documentation"):
        """Initialize the monitoring bot"""
        self.docs_path = docs_path
        self.scanner = DocScanner(docs_path)

        # Load ECO domain documentation
        self.eco_docs = self.scanner.get_documents_by_domain("ECO")

        # Setup logging
        self.logger = self._setup_logging()

        # Initialize Prometheus metrics
        self._init_metrics()

        self.logger.info(f"🌍 ECO Monitoring Bot initialized")
        self.logger.info(f"📚 Loaded {len(self.eco_docs)} ECO domain documents")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_level = os.getenv('LOG_LEVEL', 'INFO')

        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        return logging.getLogger('eco-monitoring-bot')

    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        # CPU metrics
        self.cpu_usage_gauge = Gauge(
            'bot_cpu_usage_percent',
            'CPU usage percentage',
            ['bot_name', 'domain']
        )

        # Memory metrics
        self.memory_usage_gauge = Gauge(
            'bot_memory_usage_bytes',
            'Memory usage in bytes',
            ['bot_name', 'domain']
        )

        # Disk metrics
        self.disk_usage_gauge = Gauge(
            'bot_disk_usage_bytes',
            'Disk usage in bytes',
            ['bot_name', 'domain']
        )

        # Network metrics
        self.network_rx_counter = Counter(
            'bot_network_rx_bytes_total',
            'Network bytes received',
            ['bot_name', 'domain']
        )

        self.network_tx_counter = Counter(
            'bot_network_tx_bytes_total',
            'Network bytes transmitted',
            ['bot_name', 'domain']
        )

        # Request metrics
        self.request_counter = Counter(
            'bot_requests_total',
            'Total number of requests',
            ['bot_name', 'domain', 'status']
        )

        # Error metrics
        self.error_counter = Counter(
            'bot_errors_total',
            'Total number of errors',
            ['bot_name', 'domain', 'error_type']
        )

        # Response time
        self.response_time_histogram = Histogram(
            'bot_response_time_seconds',
            'Response time in seconds',
            ['bot_name', 'domain']
        )

        # Health status
        self.health_gauge = Gauge(
            'bot_health_status',
            'Bot health status (1=healthy, 0=unhealthy)',
            ['bot_name', 'domain']
        )

        # Container size
        self.container_size_gauge = Gauge(
            'bot_container_size_bytes',
            'Container image size in bytes',
            ['bot_name', 'domain']
        )

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                fields = line.split()

                # Calculate CPU usage
                idle = int(fields[4])
                total = sum(int(x) for x in fields[1:8])

                # Simple approximation
                if not hasattr(self, '_prev_idle'):
                    self._prev_idle = idle
                    self._prev_total = total
                    return 0.0

                idle_delta = idle - self._prev_idle
                total_delta = total - self._prev_total

                self._prev_idle = idle
                self._prev_total = total

                if total_delta == 0:
                    return 0.0

                usage = 100.0 * (1.0 - idle_delta / total_delta)
                return max(0.0, min(100.0, usage))

        except Exception as e:
            self.logger.error(f"Error getting CPU usage: {e}")
            return 0.0

    def get_memory_usage(self) -> Dict[str, int]:
        """Get current memory usage"""
        try:
            mem_info = {}

            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        key = parts[0].rstrip(':')
                        value = int(parts[1]) * 1024  # Convert KB to bytes
                        mem_info[key] = value

            total = mem_info.get('MemTotal', 0)
            available = mem_info.get('MemAvailable', 0)
            used = total - available

            return {
                'total': total,
                'used': used,
                'available': available,
                'percent': (used / total * 100) if total > 0 else 0
            }

        except Exception as e:
            self.logger.error(f"Error getting memory usage: {e}")
            return {'total': 0, 'used': 0, 'available': 0, 'percent': 0}

    def get_disk_usage(self, path: str = '/') -> Dict[str, int]:
        """Get disk usage for a path"""
        try:
            import shutil
            stat = shutil.disk_usage(path)

            return {
                'total': stat.total,
                'used': stat.used,
                'free': stat.free,
                'percent': (stat.used / stat.total * 100) if stat.total > 0 else 0
            }

        except Exception as e:
            self.logger.error(f"Error getting disk usage: {e}")
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}

    def check_health(self) -> bool:
        """Perform health check"""
        try:
            # Check CPU
            cpu = self.get_cpu_usage()
            if cpu > 95:
                self.logger.warning(f"⚠️  Critical CPU usage: {cpu:.2f}%")
                return False

            # Check memory
            memory = self.get_memory_usage()
            if memory['percent'] > 95:
                self.logger.warning(f"⚠️  Critical memory usage: {memory['percent']:.2f}%")
                return False

            # Check disk
            disk = self.get_disk_usage()
            if disk['percent'] > 90:
                self.logger.warning(f"⚠️  Critical disk usage: {disk['percent']:.2f}%")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def update_metrics(self):
        """Update all metrics"""
        bot_name = os.getenv('BOT_NAME', 'eco-monitoring-bot')
        domain = os.getenv('BOT_DOMAIN', 'ECO')

        # Update CPU
        cpu = self.get_cpu_usage()
        self.cpu_usage_gauge.labels(bot_name=bot_name, domain=domain).set(cpu)

        # Update memory
        memory = self.get_memory_usage()
        self.memory_usage_gauge.labels(bot_name=bot_name, domain=domain).set(memory['used'])

        # Update disk
        disk = self.get_disk_usage()
        self.disk_usage_gauge.labels(bot_name=bot_name, domain=domain).set(disk['used'])

        # Update health
        health = 1 if self.check_health() else 0
        self.health_gauge.labels(bot_name=bot_name, domain=domain).set(health)

        # Increment request counter
        self.request_counter.labels(bot_name=bot_name, domain=domain, status='success').inc()

    def log_status(self):
        """Log current status"""
        cpu = self.get_cpu_usage()
        memory = self.get_memory_usage()
        disk = self.get_disk_usage()

        self.logger.info(
            f"📊 CPU: {cpu:.1f}% | "
            f"Memory: {memory['used']/1024/1024:.0f}MB ({memory['percent']:.1f}%) | "
            f"Disk: {disk['used']/1024/1024/1024:.1f}GB ({disk['percent']:.1f}%)"
        )

    def run(self):
        """Main monitoring loop"""
        metrics_port = int(os.getenv('METRICS_PORT', 8000))
        interval = int(os.getenv('HEALTH_CHECK_INTERVAL', 30))

        # Start Prometheus metrics server
        start_http_server(metrics_port)
        self.logger.info(f"📊 Metrics server started on :{metrics_port}")

        self.logger.info("🚀 Starting monitoring loop...")

        try:
            while True:
                # Update metrics
                self.update_metrics()

                # Log status
                self.log_status()

                # Sleep
                time.sleep(interval)

        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")

        except Exception as e:
            self.logger.error(f"❌ Error in monitoring loop: {e}")
            bot_name = os.getenv('BOT_NAME', 'eco-monitoring-bot')
            domain = os.getenv('BOT_DOMAIN', 'ECO')
            self.error_counter.labels(
                bot_name=bot_name,
                domain=domain,
                error_type=type(e).__name__
            ).inc()


def main():
    """Main entry point"""
    print("=" * 80)
    print("ECO MONITORING BOT")
    print("=" * 80)
    print()

    # Check documentation
    docs_path = os.getenv('DOCS_PATH', '/opt/documentation')

    if not Path(docs_path).exists():
        print(f"⚠️  Warning: Documentation not found at {docs_path}")
        print(f"   Clone with: git clone https://github.com/bsw-arch/bsw-arch.git {docs_path}")
        print()

    # Create and run bot
    bot = EcoMonitoringBot(docs_path)
    bot.run()


if __name__ == '__main__':
    main()
