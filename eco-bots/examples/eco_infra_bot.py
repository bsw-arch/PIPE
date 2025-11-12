#!/usr/bin/env python3
"""
ECO Infrastructure Bot - Infrastructure Provisioning using OpenTofu
Part of the BSW-Arch Bot Factory ECO Domain
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Add bot-utils to path
sys.path.insert(0, "/opt/documentation/bot-utils")

try:
    from doc_scanner import DocScanner
    from prometheus_client import start_http_server, Gauge, Counter
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class EcoInfraBot:
    """
    ECO Infrastructure Bot

    Responsibilities:
    - Infrastructure provisioning using OpenTofu (NOT Terraform)
    - Resource allocation
    - Cluster management
    - Configuration management
    """

    def __init__(self, docs_path: str = "/opt/documentation"):
        """Initialize the infrastructure bot"""
        self.docs_path = docs_path
        self.scanner = DocScanner(docs_path)

        # Load ECO domain documentation
        self.eco_docs = self.scanner.get_documents_by_domain("ECO")

        # Setup logging
        self.logger = self._setup_logging()

        # Initialize Prometheus metrics
        self._init_metrics()

        self.logger.info(f"🏗️  ECO Infrastructure Bot initialized")
        self.logger.info(f"📚 Loaded {len(self.eco_docs)} ECO domain documents")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_level = os.getenv('LOG_LEVEL', 'INFO')

        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        return logging.getLogger('eco-infra-bot')

    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        self.provision_counter = Counter(
            'bot_infra_provisions_total',
            'Total infrastructure provisions',
            ['resource_type', 'status']
        )

        self.resource_gauge = Gauge(
            'bot_infra_resources_count',
            'Number of managed resources',
            ['resource_type']
        )

        self.provision_duration = Gauge(
            'bot_infra_provision_duration_seconds',
            'Infrastructure provision duration'
        )

    async def check_fagam_compliance(self, config: Dict) -> bool:
        """
        Check if infrastructure configuration is FAGAM-compliant

        FAGAM = Facebook, Apple, Google, Amazon, Microsoft, HashiCorp
        """
        prohibited_providers = [
            'aws', 'google', 'azure', 'azurerm', 'gcp',
            'terraform', 'hashicorp-vault'
        ]

        config_str = str(config).lower()

        for provider in prohibited_providers:
            if provider in config_str:
                self.logger.error(f"❌ FAGAM violation detected: {provider}")
                return False

        # Check for OpenTofu (good) vs Terraform (bad)
        if 'terraform' in config_str and 'opentofu' not in config_str:
            self.logger.error("❌ Use OpenTofu, NOT Terraform")
            return False

        self.logger.info("✅ FAGAM compliance verified")
        return True

    async def provision_infrastructure(self,
                                      resource_type: str,
                                      spec: Dict) -> Dict:
        """
        Provision infrastructure using OpenTofu

        Args:
            resource_type: Type of resource (namespace, deployment, etc.)
            spec: Resource specification

        Returns:
            Provisioning result
        """
        self.logger.info(f"Provisioning {resource_type}...")

        # Check FAGAM compliance
        if not await self.check_fagam_compliance(spec):
            self.provision_counter.labels(
                resource_type=resource_type,
                status='fagam_violation'
            ).inc()
            return {
                'status': 'failed',
                'error': 'FAGAM compliance violation'
            }

        # Simulate provisioning (in production, would use OpenTofu)
        await asyncio.sleep(1)  # Simulate provision time

        # Update metrics
        self.provision_counter.labels(
            resource_type=resource_type,
            status='success'
        ).inc()

        self.resource_gauge.labels(resource_type=resource_type).inc()

        result = {
            'status': 'success',
            'resource_type': resource_type,
            'resource_id': f"{resource_type}-{os.urandom(4).hex()}",
            'provider': 'opentofu',
            'fagam_compliant': True
        }

        self.logger.info(f"✅ Provisioned {resource_type}: {result['resource_id']}")

        return result

    async def provision_namespace(self, name: str, labels: Dict) -> Dict:
        """Provision a Kubernetes namespace"""
        spec = {
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {
                'name': name,
                'labels': labels
            }
        }

        return await self.provision_infrastructure('namespace', spec)

    async def provision_deployment(self,
                                  name: str,
                                  image: str,
                                  replicas: int = 1) -> Dict:
        """Provision a Kubernetes deployment"""
        spec = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': name
            },
            'spec': {
                'replicas': replicas,
                'template': {
                    'spec': {
                        'containers': [{
                            'name': name,
                            'image': image
                        }]
                    }
                }
            }
        }

        return await self.provision_infrastructure('deployment', spec)

    async def get_infrastructure_status(self) -> Dict:
        """Get current infrastructure status"""
        return {
            'managed_resources': {
                'namespaces': self.resource_gauge.labels(resource_type='namespace')._value.get(),
                'deployments': self.resource_gauge.labels(resource_type='deployment')._value.get(),
            },
            'total_provisions': self.provision_counter._metrics,
            'fagam_compliant': True,
            'provider': 'opentofu'
        }

    async def run(self):
        """Main bot loop"""
        metrics_port = int(os.getenv('METRICS_PORT', 8000))

        # Start Prometheus metrics server
        start_http_server(metrics_port)
        self.logger.info(f"📊 Metrics server started on :{metrics_port}")

        self.logger.info("🚀 ECO Infrastructure Bot running...")

        try:
            # Example: Provision infrastructure
            await self.provision_namespace(
                name='eco-test',
                labels={'domain': 'ECO', 'env': 'test'}
            )

            await self.provision_deployment(
                name='test-app',
                image='eco-app:latest',
                replicas=3
            )

            # Main loop
            while True:
                status = await self.get_infrastructure_status()
                self.logger.info(f"📊 Status: {status}")

                await asyncio.sleep(30)

        except KeyboardInterrupt:
            self.logger.info("🛑 Infrastructure bot stopped by user")

        except Exception as e:
            self.logger.error(f"❌ Error in bot loop: {e}", exc_info=True)


def main():
    """Main entry point"""
    print("=" * 80)
    print("ECO INFRASTRUCTURE BOT")
    print("=" * 80)
    print()
    print("⚠️  IMPORTANT:")
    print("   - Uses OpenTofu (NOT Terraform)")
    print("   - Uses OpenBao (NOT Vault)")
    print("   - FAGAM-compliant only")
    print()

    # Check documentation
    docs_path = os.getenv('DOCS_PATH', '/opt/documentation')

    if not Path(docs_path).exists():
        print(f"⚠️  Warning: Documentation not found at {docs_path}")
        print(f"   Clone with: git clone https://github.com/bsw-arch/bsw-arch.git {docs_path}")
        print()

    # Create and run bot
    bot = EcoInfraBot(docs_path)
    asyncio.run(bot.run())


if __name__ == '__main__':
    main()
