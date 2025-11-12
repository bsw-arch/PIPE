#!/usr/bin/env python3
"""
AXIS Validation Bot - Architecture Validation and Compliance

Purpose: Validates architecture for TOGAF compliance, FAGAM prohibition,
         container size requirements, and standards adherence.

Domain: AXIS (Architecture)
Category: Validation & Compliance
Version: 1.0.0
"""

import os
import sys
import yaml
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('axis-validation-bot')


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ValidationResult:
    """Validation result"""
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Optional[str] = None
    remediation: Optional[str] = None


class AxisValidationBot:
    """AXIS Validation Bot for architecture compliance checking"""

    # FAGAM prohibited packages and keywords
    FAGAM_PROHIBITED = [
        # Google
        'google', 'gcp', 'google-cloud', 'googleapis', 'terraform', 'golang',
        # Amazon
        'aws-', 'boto', 'amazon', 'dynamodb',
        # Microsoft
        'azure', 'microsoft', 'windows', 'dotnet', 'mssql',
        # HashiCorp
        'hashicorp', 'terraform', 'vault', 'consul', 'nomad', 'packer',
        # Apple
        'apple', 'swift', 'cocoa', 'xcode',
        # Facebook/Meta
        'facebook', 'meta', 'react', 'jest'
    ]

    # Approved alternatives
    FAGAM_ALTERNATIVES = {
        'terraform': 'opentofu',
        'vault': 'openbao',
        'alpine': 'wolfi',
        'ubuntu': 'wolfi',
        'aws-cli': 'minio-client',
        'google-cloud': 'open-source alternative',
        'azure': 'open-source alternative',
    }

    def __init__(self, strict_mode: bool = True):
        """
        Initialise AXIS Validation Bot

        Args:
            strict_mode: Enable strict validation mode
        """
        self.bot_name = "axis-validation-bot"
        self.version = "1.0.0"
        self.strict_mode = strict_mode
        self.validation_results: List[ValidationResult] = []

        logger.info(f"🔍 {self.bot_name} v{self.version} starting...")
        logger.info(f"⚙️  Strict mode: {'enabled' if strict_mode else 'disabled'}")

    def validate_togaf_compliance(self, architecture_doc: Dict) -> List[ValidationResult]:
        """
        Validate TOGAF 10 compliance

        Args:
            architecture_doc: Architecture document as dictionary

        Returns:
            List[ValidationResult]: Validation results
        """
        logger.info("📋 Validating TOGAF 10 compliance...")

        results = []

        # Check ADM phases
        required_phases = [
            'Preliminary',
            'Architecture Vision',
            'Business Architecture',
            'Information Systems Architecture',
            'Technology Architecture',
            'Opportunities and Solutions',
            'Migration Planning',
            'Implementation Governance',
            'Architecture Change Management'
        ]

        adm_phases = architecture_doc.get('togaf', {}).get('adm_phases', [])

        for phase in required_phases:
            if phase not in adm_phases:
                results.append(ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.HIGH,
                    message=f"Missing TOGAF ADM Phase: {phase}",
                    remediation=f"Complete TOGAF ADM Phase {phase} documentation"
                ))
            else:
                results.append(ValidationResult(
                    passed=True,
                    severity=ValidationSeverity.INFO,
                    message=f"TOGAF ADM Phase {phase}: Present ✅"
                ))

        # Check architecture principles
        principles = architecture_doc.get('principles', [])
        if len(principles) < 4:
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"Insufficient architecture principles: {len(principles)}/4 minimum",
                remediation="Define at least 4 architecture principles"
            ))

        # Check stakeholder analysis
        if 'stakeholders' not in architecture_doc:
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Missing stakeholder analysis",
                remediation="Complete stakeholder identification and analysis"
            ))

        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)
        logger.info(f"✅ TOGAF validation: {passed_count}/{total_count} checks passed")

        return results

    def validate_fagam_prohibition(self, file_path: Path) -> List[ValidationResult]:
        """
        Validate FAGAM prohibition compliance

        Args:
            file_path: Path to file to validate

        Returns:
            List[ValidationResult]: Validation results
        """
        logger.info(f"🚫 Validating FAGAM prohibition: {file_path}")

        results = []

        try:
            if file_path.suffix in ['.py', '.yaml', '.yml', '.txt', '.toml', '.json']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()

                violations = []
                for prohibited in self.FAGAM_PROHIBITED:
                    if prohibited in content:
                        alternative = self.FAGAM_ALTERNATIVES.get(prohibited, 'open-source alternative')
                        violations.append((prohibited, alternative))

                if violations:
                    for prohibited, alternative in violations:
                        results.append(ValidationResult(
                            passed=False,
                            severity=ValidationSeverity.CRITICAL,
                            message=f"FAGAM violation detected: '{prohibited}'",
                            details=f"Found in {file_path}",
                            remediation=f"Replace with {alternative}"
                        ))
                else:
                    results.append(ValidationResult(
                        passed=True,
                        severity=ValidationSeverity.INFO,
                        message=f"FAGAM compliance: {file_path.name} ✅"
                    ))

        except Exception as e:
            logger.error(f"❌ Error validating {file_path}: {e}")
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"Could not validate file: {file_path}",
                details=str(e)
            ))

        return results

    def validate_container_size(self, image_name: str, max_size_mb: int = 50) -> ValidationResult:
        """
        Validate container image size

        Args:
            image_name: Container image name
            max_size_mb: Maximum allowed size in MB

        Returns:
            ValidationResult: Validation result
        """
        logger.info(f"📦 Validating container size: {image_name}")

        try:
            # Check if image exists
            result = subprocess.run(
                ['docker', 'images', image_name, '--format', '{{.Size}}'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Container image not found: {image_name}",
                    remediation="Build container image first"
                )

            size_str = result.stdout.strip()
            if not size_str:
                return ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Could not determine size for: {image_name}",
                    remediation="Verify image exists and is built correctly"
                )

            # Parse size
            size_mb = self._parse_size_to_mb(size_str)

            if size_mb > max_size_mb:
                return ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.HIGH,
                    message=f"Container exceeds size limit: {size_mb}MB > {max_size_mb}MB",
                    details=f"Image: {image_name}",
                    remediation="Optimize container:\n"
                               "1. Use Chainguard Wolfi base (15MB)\n"
                               "2. Multi-stage builds\n"
                               "3. Remove unnecessary dependencies"
                )
            else:
                return ValidationResult(
                    passed=True,
                    severity=ValidationSeverity.INFO,
                    message=f"Container size OK: {size_mb}MB ≤ {max_size_mb}MB ✅",
                    details=f"Image: {image_name}"
                )

        except Exception as e:
            logger.error(f"❌ Error validating container size: {e}")
            return ValidationResult(
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="Container size validation failed",
                details=str(e)
            ))

    def _parse_size_to_mb(self, size_str: str) -> float:
        """
        Parse Docker size string to MB

        Args:
            size_str: Size string (e.g., "42MB", "1.2GB")

        Returns:
            float: Size in MB
        """
        size_str = size_str.strip().upper()

        if 'GB' in size_str:
            return float(size_str.replace('GB', '')) * 1024
        elif 'MB' in size_str:
            return float(size_str.replace('MB', ''))
        elif 'KB' in size_str:
            return float(size_str.replace('KB', '')) / 1024
        else:
            # Assume bytes
            return float(size_str) / (1024 * 1024)

    def validate_uk_english(self, file_path: Path) -> List[ValidationResult]:
        """
        Validate UK English spelling in documentation

        Args:
            file_path: Path to documentation file

        Returns:
            List[ValidationResult]: Validation results
        """
        logger.info(f"🇬🇧 Validating UK English: {file_path}")

        results = []

        us_spellings = {
            'favor': 'favour',
            'color': 'colour',
            'organize': 'organise',
            'analyze': 'analyse',
            'center': 'centre',
            'defense': 'defence',
            'license': 'licence',
            'meter': 'metre',
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            violations = []
            for us_word, uk_word in us_spellings.items():
                if us_word in content:
                    violations.append((us_word, uk_word))

            if violations:
                for us_word, uk_word in violations:
                    results.append(ValidationResult(
                        passed=False,
                        severity=ValidationSeverity.LOW,
                        message=f"US spelling detected: '{us_word}'",
                        details=f"In {file_path}",
                        remediation=f"Change to UK spelling: '{uk_word}'"
                    ))
            else:
                results.append(ValidationResult(
                    passed=True,
                    severity=ValidationSeverity.INFO,
                    message=f"UK English compliance: {file_path.name} ✅"
                ))

        except Exception as e:
            logger.error(f"❌ Error validating UK English: {e}")

        return results

    def generate_validation_report(self, results: List[ValidationResult]) -> str:
        """
        Generate validation report

        Args:
            results: List of validation results

        Returns:
            str: Validation report in Markdown
        """
        logger.info("📊 Generating validation report...")

        report = f"""# Architecture Validation Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Validator**: {self.bot_name} v{self.version}
**Mode**: {'Strict' if self.strict_mode else 'Standard'}

---

## Summary

"""
        # Count by severity
        critical = sum(1 for r in results if not r.passed and r.severity == ValidationSeverity.CRITICAL)
        high = sum(1 for r in results if not r.passed and r.severity == ValidationSeverity.HIGH)
        medium = sum(1 for r in results if not r.passed and r.severity == ValidationSeverity.MEDIUM)
        low = sum(1 for r in results if not r.passed and r.severity == ValidationSeverity.LOW)
        passed = sum(1 for r in results if r.passed)

        total = len(results)
        pass_rate = (passed / total * 100) if total > 0 else 0

        report += f"| Severity | Count |\n"
        report += f"|----------|-------|\n"
        report += f"| 🔴 Critical | {critical} |\n"
        report += f"| 🟠 High | {high} |\n"
        report += f"| 🟡 Medium | {medium} |\n"
        report += f"| 🔵 Low | {low} |\n"
        report += f"| ✅ Passed | {passed} |\n"
        report += f"| **Total** | **{total}** |\n"
        report += f"\n**Pass Rate**: {pass_rate:.1f}%\n"

        # Failed checks
        failed_results = [r for r in results if not r.passed]
        if failed_results:
            report += "\n## Failed Checks\n\n"
            for i, result in enumerate(failed_results, 1):
                emoji = {
                    ValidationSeverity.CRITICAL: "🔴",
                    ValidationSeverity.HIGH: "🟠",
                    ValidationSeverity.MEDIUM: "🟡",
                    ValidationSeverity.LOW: "🔵"
                }.get(result.severity, "⚪")

                report += f"### {i}. {emoji} {result.message}\n\n"
                report += f"**Severity**: {result.severity.value.upper()}\n\n"

                if result.details:
                    report += f"**Details**: {result.details}\n\n"

                if result.remediation:
                    report += f"**Remediation**:\n{result.remediation}\n\n"

                report += "---\n\n"

        # Passed checks
        passed_results = [r for r in results if r.passed]
        if passed_results:
            report += "\n## Passed Checks\n\n"
            for result in passed_results:
                report += f"- ✅ {result.message}\n"

        report += f"\n---\n\n**Validation Status**: "
        if critical > 0:
            report += "❌ FAILED (Critical issues found)"
        elif high > 0:
            report += "⚠️  WARNING (High priority issues found)"
        elif medium > 0 or low > 0:
            report += "⚡ REVIEW (Minor issues found)"
        else:
            report += "✅ PASSED (All checks passed)"

        return report

    def run(self, project_path: Path):
        """
        Main validation execution

        Args:
            project_path: Path to project to validate
        """
        logger.info(f"🚀 Running validation on: {project_path}")

        all_results = []

        # Validate FAGAM prohibition in all files
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.py', '.yaml', '.yml', '.txt']:
                results = self.validate_fagam_prohibition(file_path)
                all_results.extend(results)

        # Generate and display report
        report = self.generate_validation_report(all_results)
        print(report)

        logger.info("✅ Validation complete")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="AXIS Validation Bot")
    parser.add_argument(
        '--project-path',
        type=str,
        default='.',
        help="Path to project to validate"
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help="Enable strict validation mode"
    )

    args = parser.parse_args()

    bot = AxisValidationBot(strict_mode=args.strict)
    bot.run(Path(args.project_path))


if __name__ == "__main__":
    main()
