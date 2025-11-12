#!/usr/bin/env python3
"""
ECO Container Bot - Container Lifecycle Management
Part of the BSW-Arch Bot Factory ECO Domain

Manages container lifecycle, optimization, and compliance
"""

import sys
import os
import asyncio
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Add bot-utils to path
sys.path.insert(0, "/opt/documentation/bot-utils")

try:
    from doc_scanner import DocScanner
    from prometheus_client import start_http_server, Gauge, Counter, Histogram
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


@dataclass
class ContainerImage:
    """Container image metadata"""
    name: str
    tag: str
    size_mb: float
    created: str
    base_image: str
    layers: int
    vulnerabilities: int


class EcoContainerBot:
    """
    ECO Container Bot

    Responsibilities:
    - Container image optimization
    - Size monitoring (<50MB target)
    - Vulnerability scanning
    - Base image compliance (Wolfi only)
    - Layer optimization
    - Registry management
    """

    def __init__(self, docs_path: str = "/opt/documentation"):
        """Initialize the container bot"""
        self.docs_path = docs_path
        self.scanner = DocScanner(docs_path)

        # Load ECO domain documentation
        self.eco_docs = self.scanner.get_documents_by_domain("ECO")

        # Setup logging
        self.logger = self._setup_logging()

        # Initialize Prometheus metrics
        self._init_metrics()

        # Container limits
        self.size_limit_mb = 50
        self.vulnerability_threshold = 0  # Zero tolerance
        self.approved_base_images = ['cgr.dev/chainguard/wolfi-base', 'wolfi-base']

        self.logger.info(f"🐳 ECO Container Bot initialized")
        self.logger.info(f"📚 Loaded {len(self.eco_docs)} ECO domain documents")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_level = os.getenv('LOG_LEVEL', 'INFO')

        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        return logging.getLogger('eco-container-bot')

    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        self.container_size = Histogram(
            'bot_container_size_mb',
            'Container image sizes in MB',
            buckets=[5, 10, 15, 20, 30, 40, 50, 75, 100]
        )

        self.size_violations = Counter(
            'bot_container_size_violations_total',
            'Containers exceeding size limit',
            ['image_name']
        )

        self.vulnerability_count = Gauge(
            'bot_container_vulnerabilities',
            'Number of vulnerabilities detected',
            ['image_name', 'severity']
        )

        self.optimization_savings = Counter(
            'bot_container_optimization_savings_mb',
            'Total MB saved through optimization'
        )

        self.base_image_compliance = Gauge(
            'bot_container_base_compliance',
            'Base image compliance status (1=compliant, 0=non-compliant)',
            ['image_name']
        )

    async def analyze_image(self, image_name: str, image_tag: str) -> ContainerImage:
        """
        Analyze a container image

        Args:
            image_name: Image name
            image_tag: Image tag

        Returns:
            ContainerImage with analysis results
        """
        self.logger.info(f"Analyzing container: {image_name}:{image_tag}")

        # Simulate image analysis (in production, would use Docker/Podman API)
        # Mock data for demonstration
        size_mb = hash(f"{image_name}{image_tag}") % 100  # Random size for demo
        layers = hash(f"{image_name}layers") % 20
        vulns = hash(f"{image_name}vulns") % 5

        # Determine base image from name
        base_image = 'wolfi-base' if 'eco' in image_name else 'unknown'

        image = ContainerImage(
            name=image_name,
            tag=image_tag,
            size_mb=size_mb,
            created=datetime.utcnow().isoformat(),
            base_image=base_image,
            layers=layers,
            vulnerabilities=vulns
        )

        # Update metrics
        self.container_size.observe(size_mb)

        if vulns > 0:
            self.vulnerability_count.labels(
                image_name=image_name,
                severity='high' if vulns > 3 else 'medium'
            ).set(vulns)

        # Check base image compliance
        is_compliant = any(approved in base_image for approved in self.approved_base_images)
        self.base_image_compliance.labels(image_name=image_name).set(1 if is_compliant else 0)

        self.logger.info(
            f"Image analysis: {size_mb:.1f}MB, {layers} layers, {vulns} vulnerabilities"
        )

        return image

    async def check_compliance(self, image: ContainerImage) -> Dict:
        """
        Check container compliance against BSW-Arch standards

        Args:
            image: Container image to check

        Returns:
            Compliance report
        """
        violations = []
        warnings = []

        # Check size limit
        if image.size_mb > self.size_limit_mb:
            violations.append(
                f"Size {image.size_mb:.1f}MB exceeds limit of {self.size_limit_mb}MB"
            )
            self.size_violations.labels(image_name=image.name).inc()

        # Check vulnerabilities
        if image.vulnerabilities > self.vulnerability_threshold:
            violations.append(
                f"Found {image.vulnerabilities} vulnerabilities (threshold: {self.vulnerability_threshold})"
            )

        # Check base image
        is_approved_base = any(
            approved in image.base_image
            for approved in self.approved_base_images
        )

        if not is_approved_base:
            violations.append(
                f"Base image '{image.base_image}' not approved. Use Chainguard Wolfi."
            )

        # Check layer count
        if image.layers > 15:
            warnings.append(
                f"High layer count ({image.layers}). Consider multi-stage builds."
            )

        is_compliant = len(violations) == 0

        report = {
            'image': f"{image.name}:{image.tag}",
            'compliant': is_compliant,
            'violations': violations,
            'warnings': warnings,
            'metrics': {
                'size_mb': image.size_mb,
                'layers': image.layers,
                'vulnerabilities': image.vulnerabilities,
                'base_image': image.base_image
            }
        }

        if is_compliant:
            self.logger.info(f"✅ {image.name}:{image.tag} is compliant")
        else:
            self.logger.warning(
                f"❌ {image.name}:{image.tag} has {len(violations)} violations"
            )

        return report

    async def optimize_image(self, image: ContainerImage) -> Dict:
        """
        Generate optimization recommendations

        Args:
            image: Container image to optimize

        Returns:
            Optimization recommendations
        """
        recommendations = []
        potential_savings = 0

        # Size optimization
        if image.size_mb > 30:
            savings = image.size_mb - 25  # Target 25MB
            recommendations.append({
                'type': 'size_reduction',
                'current': f"{image.size_mb:.1f}MB",
                'target': "25MB",
                'savings': f"{savings:.1f}MB",
                'actions': [
                    'Use Wolfi base image (15MB)',
                    'Remove build dependencies',
                    'Use multi-stage builds',
                    'Clean package manager cache'
                ]
            })
            potential_savings += savings

        # Layer optimization
        if image.layers > 10:
            recommendations.append({
                'type': 'layer_reduction',
                'current': f"{image.layers} layers",
                'target': "5-8 layers",
                'actions': [
                    'Combine RUN commands',
                    'Use multi-stage builds',
                    'Place static files last'
                ]
            })

        # Base image optimization
        if 'wolfi' not in image.base_image.lower():
            recommendations.append({
                'type': 'base_image',
                'current': image.base_image,
                'target': 'cgr.dev/chainguard/wolfi-base:latest',
                'savings': '~300MB',
                'actions': [
                    'Switch to Chainguard Wolfi base',
                    'Use apko for declarative builds',
                    'Remove unnecessary packages'
                ]
            })
            potential_savings += 300

        # Update savings metric
        if potential_savings > 0:
            self.optimization_savings.inc(potential_savings)

        result = {
            'image': f"{image.name}:{image.tag}",
            'recommendations': recommendations,
            'potential_savings_mb': potential_savings,
            'priority': 'high' if image.size_mb > 50 else 'medium'
        }

        self.logger.info(
            f"💡 Generated {len(recommendations)} optimization recommendations "
            f"(potential savings: {potential_savings:.1f}MB)"
        )

        return result

    async def scan_vulnerabilities(self, image: ContainerImage) -> Dict:
        """
        Scan for vulnerabilities (simulated)

        Args:
            image: Container image to scan

        Returns:
            Vulnerability scan results
        """
        # In production, would use Trivy or similar scanner
        vulnerabilities = []

        if image.vulnerabilities > 0:
            for i in range(image.vulnerabilities):
                severity = 'critical' if i == 0 else 'high' if i < 2 else 'medium'
                vulnerabilities.append({
                    'id': f"CVE-2024-{1000 + i}",
                    'severity': severity,
                    'package': f"package-{i}",
                    'fixed_version': f"1.2.{i + 1}"
                })

        scan_result = {
            'image': f"{image.name}:{image.tag}",
            'scan_time': datetime.utcnow().isoformat(),
            'total_vulnerabilities': len(vulnerabilities),
            'by_severity': {
                'critical': sum(1 for v in vulnerabilities if v['severity'] == 'critical'),
                'high': sum(1 for v in vulnerabilities if v['severity'] == 'high'),
                'medium': sum(1 for v in vulnerabilities if v['severity'] == 'medium')
            },
            'vulnerabilities': vulnerabilities,
            'recommendation': 'Update base image and dependencies' if vulnerabilities else 'No action needed'
        }

        if vulnerabilities:
            self.logger.warning(
                f"⚠️  Found {len(vulnerabilities)} vulnerabilities in {image.name}"
            )
        else:
            self.logger.info(f"✅ No vulnerabilities found in {image.name}")

        return scan_result

    async def run(self):
        """Main bot loop"""
        metrics_port = int(os.getenv('METRICS_PORT', 8000))

        # Start Prometheus metrics server
        start_http_server(metrics_port)
        self.logger.info(f"📊 Metrics server started on :{metrics_port}")

        self.logger.info("🚀 ECO Container Bot running...")

        try:
            # Example: Analyze containers
            test_images = [
                ('eco-monitoring-bot', 'latest'),
                ('eco-infra-bot', 'latest'),
                ('eco-resource-bot', 'latest'),
                ('legacy-app', 'v1.0'),
            ]

            while True:
                self.logger.info("\n" + "="*60)
                self.logger.info("Container Analysis Cycle")
                self.logger.info("="*60)

                for image_name, tag in test_images:
                    # Analyze image
                    image = await self.analyze_image(image_name, tag)

                    # Check compliance
                    compliance = await self.check_compliance(image)

                    # Scan vulnerabilities
                    vuln_scan = await self.scan_vulnerabilities(image)

                    # Generate optimizations if needed
                    if not compliance['compliant'] or image.size_mb > 30:
                        optimization = await self.optimize_image(image)

                        self.logger.info(f"\n💡 Optimization for {image_name}:")
                        for rec in optimization['recommendations']:
                            self.logger.info(f"   {rec['type']}: {rec.get('savings', 'N/A')}")

                    await asyncio.sleep(2)  # Brief pause between images

                self.logger.info("\n⏳ Waiting 60s for next cycle...")
                await asyncio.sleep(60)

        except KeyboardInterrupt:
            self.logger.info("🛑 Container bot stopped by user")

        except Exception as e:
            self.logger.error(f"❌ Error in bot loop: {e}", exc_info=True)


def main():
    """Main entry point"""
    print("=" * 80)
    print("ECO CONTAINER MANAGEMENT BOT")
    print("=" * 80)
    print()
    print("📋 Responsibilities:")
    print("   - Container size monitoring (<50MB target)")
    print("   - Vulnerability scanning")
    print("   - Base image compliance (Wolfi only)")
    print("   - Optimization recommendations")
    print()

    # Check documentation
    docs_path = os.getenv('DOCS_PATH', '/opt/documentation')

    if not Path(docs_path).exists():
        print(f"⚠️  Warning: Documentation not found at {docs_path}")
        print(f"   Clone with: git clone https://github.com/bsw-arch/bsw-arch.git {docs_path}")
        print()

    # Create and run bot
    bot = EcoContainerBot(docs_path)
    asyncio.run(bot.run())


if __name__ == '__main__':
    main()
