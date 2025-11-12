#!/usr/bin/env python3
"""
ECO Resource Bot - Resource Optimization and Allocation
Part of the BSW-Arch Bot Factory ECO Domain
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Add bot-utils to path
sys.path.insert(0, "/opt/documentation/bot-utils")

try:
    from doc_scanner import DocScanner
    from prometheus_client import start_http_server, Gauge, Counter, Histogram
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


@dataclass
class ResourceRecommendation:
    """Resource optimization recommendation"""
    resource_type: str
    current_value: float
    recommended_value: float
    savings: float
    reason: str


class EcoResourceBot:
    """
    ECO Resource Bot

    Responsibilities:
    - Resource usage analysis
    - Optimization recommendations
    - Cost tracking
    - Efficiency reporting
    """

    def __init__(self, docs_path: str = "/opt/documentation"):
        """Initialize the resource bot"""
        self.docs_path = docs_path
        self.scanner = DocScanner(docs_path)

        # Load ECO domain documentation
        self.eco_docs = self.scanner.get_documents_by_domain("ECO")

        # Setup logging
        self.logger = self._setup_logging()

        # Initialize Prometheus metrics
        self._init_metrics()

        # Resource thresholds
        self.cpu_threshold = 80  # %
        self.memory_threshold = 85  # %
        self.efficiency_target = 70  # %

        self.logger.info(f"📊 ECO Resource Bot initialized")
        self.logger.info(f"📚 Loaded {len(self.eco_docs)} ECO domain documents")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_level = os.getenv('LOG_LEVEL', 'INFO')

        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        return logging.getLogger('eco-resource-bot')

    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        self.resource_efficiency = Gauge(
            'bot_resource_efficiency_percent',
            'Resource efficiency percentage',
            ['resource_type']
        )

        self.optimization_savings = Counter(
            'bot_optimization_savings_total',
            'Total optimization savings',
            ['resource_type', 'unit']
        )

        self.recommendation_count = Counter(
            'bot_recommendations_total',
            'Total recommendations made',
            ['recommendation_type']
        )

        self.waste_gauge = Gauge(
            'bot_resource_waste_percent',
            'Resource waste percentage',
            ['resource_type']
        )

    async def analyze_resource_usage(self, pods: List[Dict]) -> Dict:
        """
        Analyze resource usage across pods

        Args:
            pods: List of pod specifications with resource usage

        Returns:
            Analysis results
        """
        self.logger.info(f"Analyzing {len(pods)} pods...")

        total_cpu_requested = 0
        total_cpu_used = 0
        total_memory_requested = 0
        total_memory_used = 0

        for pod in pods:
            resources = pod.get('resources', {})
            usage = pod.get('usage', {})

            # CPU
            cpu_request = self._parse_cpu(resources.get('cpu_request', '0m'))
            cpu_usage = self._parse_cpu(usage.get('cpu', '0m'))
            total_cpu_requested += cpu_request
            total_cpu_used += cpu_usage

            # Memory
            mem_request = self._parse_memory(resources.get('memory_request', '0Mi'))
            mem_usage = self._parse_memory(usage.get('memory', '0Mi'))
            total_memory_requested += mem_request
            total_memory_used += mem_usage

        # Calculate efficiency
        cpu_efficiency = (total_cpu_used / total_cpu_requested * 100) if total_cpu_requested > 0 else 0
        memory_efficiency = (total_memory_used / total_memory_requested * 100) if total_memory_requested > 0 else 0

        # Update metrics
        self.resource_efficiency.labels(resource_type='cpu').set(cpu_efficiency)
        self.resource_efficiency.labels(resource_type='memory').set(memory_efficiency)

        # Calculate waste
        cpu_waste = 100 - cpu_efficiency
        memory_waste = 100 - memory_efficiency

        self.waste_gauge.labels(resource_type='cpu').set(cpu_waste)
        self.waste_gauge.labels(resource_type='memory').set(memory_waste)

        analysis = {
            'cpu': {
                'requested': total_cpu_requested,
                'used': total_cpu_used,
                'efficiency': cpu_efficiency,
                'waste': cpu_waste
            },
            'memory': {
                'requested': total_memory_requested,
                'used': total_memory_used,
                'efficiency': memory_efficiency,
                'waste': memory_waste
            },
            'pod_count': len(pods)
        }

        self.logger.info(
            f"📊 CPU Efficiency: {cpu_efficiency:.1f}% | "
            f"Memory Efficiency: {memory_efficiency:.1f}%"
        )

        return analysis

    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU string to millicores"""
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1])
        return float(cpu_str) * 1000

    def _parse_memory(self, mem_str: str) -> float:
        """Parse memory string to MiB"""
        if mem_str.endswith('Mi'):
            return float(mem_str[:-2])
        elif mem_str.endswith('Gi'):
            return float(mem_str[:-2]) * 1024
        return float(mem_str)

    async def generate_recommendations(self,
                                      analysis: Dict) -> List[ResourceRecommendation]:
        """
        Generate optimization recommendations

        Args:
            analysis: Resource analysis results

        Returns:
            List of recommendations
        """
        recommendations = []

        # CPU recommendations
        cpu_data = analysis['cpu']
        if cpu_data['efficiency'] < self.efficiency_target:
            savings = cpu_data['requested'] - cpu_data['used']
            recommendations.append(ResourceRecommendation(
                resource_type='cpu',
                current_value=cpu_data['requested'],
                recommended_value=cpu_data['used'] * 1.2,  # 20% buffer
                savings=savings,
                reason=f"CPU efficiency is {cpu_data['efficiency']:.1f}%, below target {self.efficiency_target}%"
            ))

        # Memory recommendations
        mem_data = analysis['memory']
        if mem_data['efficiency'] < self.efficiency_target:
            savings = mem_data['requested'] - mem_data['used']
            recommendations.append(ResourceRecommendation(
                resource_type='memory',
                current_value=mem_data['requested'],
                recommended_value=mem_data['used'] * 1.2,  # 20% buffer
                savings=savings,
                reason=f"Memory efficiency is {mem_data['efficiency']:.1f}%, below target {self.efficiency_target}%"
            ))

        # Update metrics
        for rec in recommendations:
            self.recommendation_count.labels(
                recommendation_type=rec.resource_type
            ).inc()

            self.optimization_savings.labels(
                resource_type=rec.resource_type,
                unit='millicores' if rec.resource_type == 'cpu' else 'MiB'
            ).inc(rec.savings)

        self.logger.info(f"💡 Generated {len(recommendations)} recommendations")

        return recommendations

    async def run(self):
        """Main bot loop"""
        metrics_port = int(os.getenv('METRICS_PORT', 8000))

        # Start Prometheus metrics server
        start_http_server(metrics_port)
        self.logger.info(f"📊 Metrics server started on :{metrics_port}")

        self.logger.info("🚀 ECO Resource Bot running...")

        try:
            # Main loop
            while True:
                # Mock pod data (in production, would fetch from Kubernetes)
                mock_pods = [
                    {
                        'name': 'pod-1',
                        'resources': {'cpu_request': '500m', 'memory_request': '512Mi'},
                        'usage': {'cpu': '200m', 'memory': '300Mi'}
                    },
                    {
                        'name': 'pod-2',
                        'resources': {'cpu_request': '1000m', 'memory_request': '1Gi'},
                        'usage': {'cpu': '600m', 'memory': '700Mi'}
                    },
                    {
                        'name': 'pod-3',
                        'resources': {'cpu_request': '250m', 'memory_request': '256Mi'},
                        'usage': {'cpu': '150m', 'memory': '180Mi'}
                    },
                ]

                # Analyze resources
                analysis = await self.analyze_resource_usage(mock_pods)

                # Generate recommendations
                recommendations = await self.generate_recommendations(analysis)

                if recommendations:
                    self.logger.info("\n💡 Optimization Recommendations:")
                    for rec in recommendations:
                        self.logger.info(
                            f"   {rec.resource_type.upper()}: "
                            f"{rec.current_value:.0f} → {rec.recommended_value:.0f} "
                            f"(save {rec.savings:.0f})"
                        )
                        self.logger.info(f"      Reason: {rec.reason}")

                await asyncio.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            self.logger.info("🛑 Resource bot stopped by user")

        except Exception as e:
            self.logger.error(f"❌ Error in bot loop: {e}", exc_info=True)


def main():
    """Main entry point"""
    print("=" * 80)
    print("ECO RESOURCE OPTIMIZATION BOT")
    print("=" * 80)
    print()

    # Check documentation
    docs_path = os.getenv('DOCS_PATH', '/opt/documentation')

    if not Path(docs_path).exists():
        print(f"⚠️  Warning: Documentation not found at {docs_path}")
        print(f"   Clone with: git clone https://github.com/bsw-arch/bsw-arch.git {docs_path}")
        print()

    # Create and run bot
    bot = EcoResourceBot(docs_path)
    asyncio.run(bot.run())


if __name__ == '__main__':
    main()
