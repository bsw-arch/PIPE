#!/usr/bin/env python3
"""
ECO Security Bot - Security Hardening and Compliance
Part of the BSW-Arch Bot Factory ECO Domain

Manages security hardening, scanning, and compliance for all bot infrastructure
"""

import sys
import os
import asyncio
import logging
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
class SecurityFinding:
    """Security finding/vulnerability"""
    id: str
    severity: str  # critical, high, medium, low
    category: str  # network, container, config, rbac
    resource: str
    description: str
    remediation: str
    status: str  # open, remediated, accepted_risk


class EcoSecurityBot:
    """
    ECO Security Bot

    Responsibilities:
    - Security scanning and hardening
    - RBAC policy validation
    - Network policy enforcement
    - Secret management (OpenBao integration)
    - Compliance checking
    - Security posture monitoring
    - Vulnerability management
    """

    def __init__(self, docs_path: str = "/opt/documentation"):
        """Initialize the security bot"""
        self.docs_path = docs_path
        self.scanner = DocScanner(docs_path)

        # Load ECO domain documentation
        self.eco_docs = self.scanner.get_documents_by_domain("ECO")

        # Setup logging
        self.logger = self._setup_logging()

        # Initialize Prometheus metrics
        self._init_metrics()

        # Security policies
        self.required_network_policies = True
        self.require_nonroot_containers = True
        self.require_readonly_filesystem = False  # Not always possible
        self.max_capability_add = 0  # No additional capabilities
        self.require_pod_security_policy = True

        self.logger.info(f"🔒 ECO Security Bot initialized")
        self.logger.info(f"📚 Loaded {len(self.eco_docs)} ECO domain documents")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_level = os.getenv('LOG_LEVEL', 'INFO')

        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        return logging.getLogger('eco-security-bot')

    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        self.security_findings = Gauge(
            'bot_security_findings',
            'Number of security findings',
            ['severity', 'category', 'status']
        )

        self.security_score = Gauge(
            'bot_security_score',
            'Overall security score (0-100)',
            ['resource_type']
        )

        self.compliance_status = Gauge(
            'bot_compliance_status',
            'Compliance status (1=compliant, 0=non-compliant)',
            ['policy']
        )

        self.vulnerability_scans = Counter(
            'bot_vulnerability_scans_total',
            'Total vulnerability scans performed',
            ['scan_type']
        )

        self.remediation_actions = Counter(
            'bot_remediation_actions_total',
            'Security remediation actions taken',
            ['action_type']
        )

    async def scan_container_security(self, container_name: str) -> List[SecurityFinding]:
        """
        Scan container for security issues

        Args:
            container_name: Name of container to scan

        Returns:
            List of security findings
        """
        self.logger.info(f"Scanning container security: {container_name}")

        findings = []

        # Mock scan (in production, would use actual security scanner)
        await asyncio.sleep(1)

        # Check if running as root
        if hash(container_name) % 3 == 0:  # Simulate 33% running as root
            findings.append(SecurityFinding(
                id=f"SEC-{hash(container_name) % 1000}",
                severity='high',
                category='container',
                resource=container_name,
                description='Container running as root (UID 0)',
                remediation='Set runAsUser to non-root (e.g., 65532)',
                status='open'
            ))

        # Check for privilege escalation
        if hash(container_name + 'priv') % 4 == 0:  # Simulate 25%
            findings.append(SecurityFinding(
                id=f"SEC-{hash(container_name + 'priv') % 1000}",
                severity='critical',
                category='container',
                resource=container_name,
                description='allowPrivilegeEscalation set to true',
                remediation='Set securityContext.allowPrivilegeEscalation: false',
                status='open'
            ))

        # Check for added capabilities
        if hash(container_name + 'cap') % 5 == 0:  # Simulate 20%
            findings.append(SecurityFinding(
                id=f"SEC-{hash(container_name + 'cap') % 1000}",
                severity='medium',
                category='container',
                resource=container_name,
                description='Container has additional capabilities',
                remediation='Remove unnecessary capabilities, drop ALL',
                status='open'
            ))

        # Update metrics
        self.vulnerability_scans.labels(scan_type='container').inc()

        for finding in findings:
            self.security_findings.labels(
                severity=finding.severity,
                category=finding.category,
                status=finding.status
            ).inc()

        if findings:
            self.logger.warning(
                f"⚠️  Found {len(findings)} security issues in {container_name}"
            )
        else:
            self.logger.info(f"✅ No security issues found in {container_name}")

        return findings

    async def scan_network_policies(self, namespace: str) -> List[SecurityFinding]:
        """
        Scan network policies for security gaps

        Args:
            namespace: Kubernetes namespace

        Returns:
            List of security findings
        """
        self.logger.info(f"Scanning network policies in namespace: {namespace}")

        findings = []

        # Mock scan
        await asyncio.sleep(0.5)

        # Check if network policies exist
        has_network_policy = hash(namespace) % 2 == 0  # 50% have policies

        if not has_network_policy:
            findings.append(SecurityFinding(
                id=f"SEC-NET-{hash(namespace) % 1000}",
                severity='high',
                category='network',
                resource=namespace,
                description='No NetworkPolicy defined for namespace',
                remediation='Create NetworkPolicy to restrict pod-to-pod communication',
                status='open'
            ))

        # Check for overly permissive policies
        if has_network_policy and hash(namespace + 'perm') % 3 == 0:
            findings.append(SecurityFinding(
                id=f"SEC-NET-{hash(namespace + 'perm') % 1000}",
                severity='medium',
                category='network',
                resource=namespace,
                description='NetworkPolicy allows all egress traffic',
                remediation='Restrict egress to only required destinations',
                status='open'
            ))

        # Update metrics
        self.vulnerability_scans.labels(scan_type='network').inc()

        for finding in findings:
            self.security_findings.labels(
                severity=finding.severity,
                category=finding.category,
                status=finding.status
            ).inc()

        return findings

    async def scan_rbac_policies(self, namespace: str) -> List[SecurityFinding]:
        """
        Scan RBAC policies for overly permissive access

        Args:
            namespace: Kubernetes namespace

        Returns:
            List of security findings
        """
        self.logger.info(f"Scanning RBAC policies in namespace: {namespace}")

        findings = []

        # Mock scan
        await asyncio.sleep(0.5)

        # Check for overly broad permissions
        if hash(namespace + 'rbac') % 3 == 0:  # 33% overly broad
            findings.append(SecurityFinding(
                id=f"SEC-RBAC-{hash(namespace) % 1000}",
                severity='high',
                category='rbac',
                resource=namespace,
                description='ServiceAccount has cluster-admin permissions',
                remediation='Apply principle of least privilege, use Role instead of ClusterRole',
                status='open'
            ))

        # Check for wildcard permissions
        if hash(namespace + 'wild') % 4 == 0:  # 25% have wildcards
            findings.append(SecurityFinding(
                id=f"SEC-RBAC-{hash(namespace + 'wild') % 1000}",
                severity='medium',
                category='rbac',
                resource=namespace,
                description='RBAC policy uses wildcard (*) for resources or verbs',
                remediation='Specify explicit resources and verbs',
                status='open'
            ))

        # Update metrics
        self.vulnerability_scans.labels(scan_type='rbac').inc()

        for finding in findings:
            self.security_findings.labels(
                severity=finding.severity,
                category=finding.category,
                status=finding.status
            ).inc()

        return findings

    async def scan_secrets_management(self, namespace: str) -> List[SecurityFinding]:
        """
        Scan secrets management practices

        Args:
            namespace: Kubernetes namespace

        Returns:
            List of security findings
        """
        self.logger.info(f"Scanning secrets management in namespace: {namespace}")

        findings = []

        # Mock scan
        await asyncio.sleep(0.5)

        # Check for unencrypted secrets
        if hash(namespace + 'enc') % 3 == 0:  # 33% unencrypted
            findings.append(SecurityFinding(
                id=f"SEC-SECRET-{hash(namespace) % 1000}",
                severity='critical',
                category='config',
                resource=namespace,
                description='Secrets not encrypted at rest',
                remediation='Enable encryption at rest, use OpenBao for secret management',
                status='open'
            ))

        # Check for secrets in environment variables
        if hash(namespace + 'env') % 4 == 0:  # 25%
            findings.append(SecurityFinding(
                id=f"SEC-SECRET-{hash(namespace + 'env') % 1000}",
                severity='medium',
                category='config',
                resource=namespace,
                description='Secrets exposed as environment variables',
                remediation='Use volume mounts for secrets instead of env vars',
                status='open'
            ))

        # Check for OpenBao usage (should use OpenBao, not Vault)
        uses_hashicorp_vault = hash(namespace + 'vault') % 5 == 0
        if uses_hashicorp_vault:
            findings.append(SecurityFinding(
                id=f"SEC-FAGAM-{hash(namespace) % 1000}",
                severity='high',
                category='config',
                resource=namespace,
                description='Using HashiCorp Vault (FAGAM violation)',
                remediation='Migrate to OpenBao (open source Vault alternative)',
                status='open'
            ))

        # Update metrics
        self.vulnerability_scans.labels(scan_type='secrets').inc()

        for finding in findings:
            self.security_findings.labels(
                severity=finding.severity,
                category=finding.category,
                status=finding.status
            ).inc()

        return findings

    async def calculate_security_score(self, findings: List[SecurityFinding]) -> float:
        """
        Calculate overall security score

        Args:
            findings: List of security findings

        Returns:
            Security score (0-100)
        """
        # Start with perfect score
        score = 100.0

        # Deduct points based on severity
        severity_weights = {
            'critical': 20,
            'high': 10,
            'medium': 5,
            'low': 2
        }

        for finding in findings:
            if finding.status == 'open':
                deduction = severity_weights.get(finding.severity, 0)
                score -= deduction

        # Ensure score doesn't go below 0
        score = max(0.0, score)

        return score

    async def auto_remediate(self, finding: SecurityFinding) -> bool:
        """
        Attempt automatic remediation

        Args:
            finding: Security finding to remediate

        Returns:
            True if remediation successful
        """
        self.logger.info(f"Attempting auto-remediation for {finding.id}")

        # Simulate remediation (in production, would apply actual fixes)
        await asyncio.sleep(1)

        # Only auto-remediate low/medium severity issues
        can_auto_remediate = finding.severity in ['low', 'medium']

        if can_auto_remediate:
            success = hash(finding.id) % 100 > 10  # 90% success rate

            if success:
                self.logger.info(f"✅ Auto-remediated {finding.id}")
                self.remediation_actions.labels(
                    action_type=finding.category
                ).inc()
                finding.status = 'remediated'
            else:
                self.logger.warning(f"❌ Auto-remediation failed for {finding.id}")

            return success
        else:
            self.logger.info(
                f"⚠️  {finding.severity} severity issue requires manual remediation"
            )
            return False

    async def run(self):
        """Main bot loop"""
        metrics_port = int(os.getenv('METRICS_PORT', 8000))

        # Start Prometheus metrics server
        start_http_server(metrics_port)
        self.logger.info(f"📊 Metrics server started on :{metrics_port}")

        self.logger.info("🚀 ECO Security Bot running...")

        try:
            cycle_count = 0

            while True:
                cycle_count += 1
                self.logger.info(f"\n{'='*60}")
                self.logger.info(f"Security Scan Cycle #{cycle_count}")
                self.logger.info(f"{'='*60}")

                all_findings = []

                # Scan different security aspects
                test_resources = ['eco-bots', 'cag-rag', 'monitoring']

                for resource in test_resources:
                    self.logger.info(f"\n🔍 Scanning {resource}...")

                    # Container security
                    container_findings = await self.scan_container_security(resource)
                    all_findings.extend(container_findings)

                    # Network policies
                    network_findings = await self.scan_network_policies(resource)
                    all_findings.extend(network_findings)

                    # RBAC policies
                    rbac_findings = await self.scan_rbac_policies(resource)
                    all_findings.extend(rbac_findings)

                    # Secrets management
                    secret_findings = await self.scan_secrets_management(resource)
                    all_findings.extend(secret_findings)

                    await asyncio.sleep(1)

                # Calculate security score
                security_score = await self.calculate_security_score(all_findings)
                self.security_score.labels(resource_type='overall').set(security_score)

                self.logger.info(f"\n📊 Security Summary:")
                self.logger.info(f"   Total Findings: {len(all_findings)}")
                self.logger.info(f"   Security Score: {security_score:.1f}/100")

                # Categorize findings by severity
                by_severity = {}
                for finding in all_findings:
                    by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1

                for severity, count in sorted(by_severity.items()):
                    self.logger.info(f"   {severity.upper()}: {count}")

                # Attempt auto-remediation for eligible findings
                self.logger.info(f"\n🔧 Attempting auto-remediation...")
                remediated_count = 0

                for finding in all_findings:
                    if finding.status == 'open':
                        if await self.auto_remediate(finding):
                            remediated_count += 1

                self.logger.info(f"✅ Auto-remediated {remediated_count} findings")

                # Wait before next scan
                self.logger.info(f"\n⏳ Next security scan in 10 minutes...")
                await asyncio.sleep(600)  # 10 minutes

        except KeyboardInterrupt:
            self.logger.info("🛑 Security bot stopped by user")

        except Exception as e:
            self.logger.error(f"❌ Error in bot loop: {e}", exc_info=True)


def main():
    """Main entry point"""
    print("=" * 80)
    print("ECO SECURITY HARDENING BOT")
    print("=" * 80)
    print()
    print("📋 Responsibilities:")
    print("   - Container security scanning")
    print("   - Network policy validation")
    print("   - RBAC policy audit")
    print("   - Secrets management (OpenBao)")
    print("   - Auto-remediation")
    print("   - Security scoring")
    print()

    # Check documentation
    docs_path = os.getenv('DOCS_PATH', '/opt/documentation')

    if not Path(docs_path).exists():
        print(f"⚠️  Warning: Documentation not found at {docs_path}")
        print(f"   Clone with: git clone https://github.com/bsw-arch/bsw-arch.git {docs_path}")
        print()

    # Create and run bot
    bot = EcoSecurityBot(docs_path)
    asyncio.run(bot.run())


if __name__ == '__main__':
    main()
