#!/usr/bin/env python3
"""
ECO Scaler Bot - Auto-scaling Management
Part of the BSW-Arch Bot Factory ECO Domain

Manages horizontal and vertical pod autoscaling
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, "/opt/documentation/bot-utils")

try:
    from doc_scanner import DocScanner
    from prometheus_client import start_http_server, Gauge, Counter, Histogram
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class EcoScalerBot:
    """
    ECO Scaler Bot

    Responsibilities:
    - Horizontal Pod Autoscaling (HPA)
    - Vertical Pod Autoscaling (VPA)
    - Predictive scaling
    - Cost-aware scaling
    - Load-based scaling decisions
    """

    def __init__(self, docs_path: str = "/opt/documentation"):
        """Initialize the scaler bot"""
        self.docs_path = docs_path
        self.scanner = DocScanner(docs_path)
        self.eco_docs = self.scanner.get_documents_by_domain("ECO")
        self.logger = self._setup_logging()
        self._init_metrics()

        # Scaling thresholds
        self.cpu_scale_up_threshold = 70  # %
        self.cpu_scale_down_threshold = 30  # %
        self.memory_scale_up_threshold = 80  # %
        self.memory_scale_down_threshold = 40  # %

        self.logger.info(f"⚖️  ECO Scaler Bot initialized")

    def _setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        return logging.getLogger('eco-scaler-bot')

    def _init_metrics(self):
        self.scaling_decisions = Counter(
            'bot_scaling_decisions_total',
            'Total scaling decisions made',
            ['deployment', 'direction', 'reason']
        )
        self.current_replicas = Gauge(
            'bot_deployment_replicas',
            'Current number of replicas',
            ['deployment']
        )
        self.scaling_efficiency = Gauge(
            'bot_scaling_efficiency_percent',
            'Scaling efficiency percentage',
            ['deployment']
        )

    async def analyze_metrics(self, deployment: str) -> Dict:
        """Analyze deployment metrics"""
        # Simulate metrics (in production, would query Prometheus)
        cpu_usage = hash(deployment) % 100
        memory_usage = hash(deployment + 'mem') % 100
        current_replicas = hash(deployment + 'rep') % 5 + 1

        return {
            'deployment': deployment,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'current_replicas': current_replicas,
            'target_replicas': current_replicas
        }

    async def make_scaling_decision(self, metrics: Dict) -> Dict:
        """Make scaling decision based on metrics"""
        deployment = metrics['deployment']
        cpu = metrics['cpu_usage']
        memory = metrics['memory_usage']
        current = metrics['current_replicas']

        target = current
        reason = 'stable'
        direction = 'none'

        # Scale up decisions
        if cpu > self.cpu_scale_up_threshold or memory > self.memory_scale_up_threshold:
            target = min(current + 1, 10)  # Max 10 replicas
            reason = f"cpu={cpu}%" if cpu > self.cpu_scale_up_threshold else f"memory={memory}%"
            direction = 'up'
        # Scale down decisions
        elif cpu < self.cpu_scale_down_threshold and memory < self.memory_scale_down_threshold:
            target = max(current - 1, 1)  # Min 1 replica
            reason = f"low_usage cpu={cpu}% memory={memory}%"
            direction = 'down'

        if target != current:
            self.scaling_decisions.labels(
                deployment=deployment,
                direction=direction,
                reason=reason
            ).inc()

            self.logger.info(
                f"{'↗️' if direction == 'up' else '↘️'} Scaling {deployment}: {current} → {target} ({reason})"
            )

        self.current_replicas.labels(deployment=deployment).set(target)

        return {
            'deployment': deployment,
            'action': direction,
            'from_replicas': current,
            'to_replicas': target,
            'reason': reason
        }

    async def run(self):
        """Main bot loop"""
        metrics_port = int(os.getenv('METRICS_PORT', 8000))
        start_http_server(metrics_port)
        self.logger.info(f"📊 Metrics server started on :{metrics_port}")
        self.logger.info("🚀 ECO Scaler Bot running...")

        test_deployments = ['eco-monitoring', 'cag-rag-mcp', 'eco-infra']

        try:
            while True:
                self.logger.info(f"\n{'='*60}")
                self.logger.info("Scaling Analysis Cycle")
                self.logger.info(f"{'='*60}")

                for deployment in test_deployments:
                    metrics = await self.analyze_metrics(deployment)
                    decision = await self.make_scaling_decision(metrics)
                    await asyncio.sleep(0.5)

                self.logger.info(f"\n⏳ Next analysis in 30 seconds...")
                await asyncio.sleep(30)

        except KeyboardInterrupt:
            self.logger.info("🛑 Scaler bot stopped")


def main():
    print("=" * 80)
    print("ECO AUTO-SCALING BOT")
    print("=" * 80)
    bot = EcoScalerBot()
    asyncio.run(bot.run())


if __name__ == '__main__':
    main()
