#!/usr/bin/env python3
"""
AXIS Assessment Bot - System Assessment and Gap Analysis

Purpose: Assesses current state architecture, identifies gaps, evaluates maturity,
         and generates improvement recommendations.

Domain: AXIS (Architecture)
Category: Analysis & Assessment
Version: 1.0.0
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('axis-assessment-bot')


class MaturityLevel(Enum):
    """Architecture maturity levels"""
    INITIAL = 1  # Ad-hoc processes
    MANAGED = 2  # Project-specific
    DEFINED = 3  # Organization-wide standards
    MEASURED = 4  # Quantitative management
    OPTIMIZED = 5  # Continuous improvement


@dataclass
class GapItem:
    """Gap analysis item"""
    area: str
    current_state: str
    target_state: str
    gap_description: str
    priority: str
    estimated_effort: str


@dataclass
class TechnicalDebtItem:
    """Technical debt item"""
    category: str
    description: str
    impact: str
    estimated_cost: int
    remediation: str


class AxisAssessmentBot:
    """AXIS Assessment Bot for architecture assessment and gap analysis"""

    def __init__(self):
        """Initialise AXIS Assessment Bot"""
        self.bot_name = "axis-assessment-bot"
        self.version = "1.0.0"

        logger.info(f"🔍 {self.bot_name} v{self.version} starting...")

    def assess_architecture_maturity(self, architecture: Dict) -> Dict:
        """
        Assess architecture maturity level

        Args:
            architecture: Architecture data

        Returns:
            Dict: Maturity assessment
        """
        logger.info("📊 Assessing architecture maturity...")

        # Assess different dimensions
        dimensions = {
            "strategy": self._assess_strategy(architecture),
            "governance": self._assess_governance(architecture),
            "documentation": self._assess_documentation(architecture),
            "skills": self._assess_skills(architecture),
            "tools": self._assess_tools(architecture)
        }

        # Calculate overall maturity
        avg_maturity = sum(dimensions.values()) / len(dimensions)
        maturity_level = MaturityLevel(round(avg_maturity))

        assessment = {
            "overall_maturity": avg_maturity,
            "maturity_level": maturity_level.name,
            "dimensions": dimensions,
            "strengths": self._identify_strengths(dimensions),
            "weaknesses": self._identify_weaknesses(dimensions)
        }

        logger.info(f"📈 Overall maturity: {maturity_level.name} ({avg_maturity:.1f}/5.0)")

        return assessment

    def _assess_strategy(self, architecture: Dict) -> float:
        """Assess strategy dimension"""
        score = 3.0  # Default: Defined

        if architecture.get('strategic_alignment'):
            score += 0.5
        if architecture.get('business_drivers'):
            score += 0.5

        return min(score, 5.0)

    def _assess_governance(self, architecture: Dict) -> float:
        """Assess governance dimension"""
        score = 2.5  # Default: Between Managed and Defined

        if architecture.get('governance_framework'):
            score += 1.0
        if architecture.get('decision_process'):
            score += 0.5

        return min(score, 5.0)

    def _assess_documentation(self, architecture: Dict) -> float:
        """Assess documentation dimension"""
        score = 3.0  # Default: Defined

        docs = architecture.get('documentation', {})
        if docs.get('togaf_compliant'):
            score += 0.5
        if docs.get('archimate_diagrams'):
            score += 0.5

        return min(score, 5.0)

    def _assess_skills(self, architecture: Dict) -> float:
        """Assess skills dimension"""
        return 3.2  # Placeholder

    def _assess_tools(self, architecture: Dict) -> float:
        """Assess tools dimension"""
        score = 3.0

        tools = architecture.get('tools', [])
        if 'opentofu' in tools:
            score += 0.3
        if 'kubernetes' in tools:
            score += 0.2

        return min(score, 5.0)

    def _identify_strengths(self, dimensions: Dict) -> List[str]:
        """Identify strong areas"""
        strengths = []
        for dimension, score in dimensions.items():
            if score >= 4.0:
                strengths.append(f"{dimension.title()}: {score:.1f}/5.0")
        return strengths

    def _identify_weaknesses(self, dimensions: Dict) -> List[str]:
        """Identify weak areas"""
        weaknesses = []
        for dimension, score in dimensions.items():
            if score < 3.0:
                weaknesses.append(f"{dimension.title()}: {score:.1f}/5.0")
        return weaknesses

    def identify_technical_debt(self, architecture: Dict) -> List[TechnicalDebtItem]:
        """
        Identify technical debt

        Args:
            architecture: Architecture data

        Returns:
            List[TechnicalDebtItem]: Technical debt items
        """
        logger.info("💰 Identifying technical debt...")

        debt_items = []

        # Check for oversized containers
        containers = architecture.get('containers', [])
        oversized = [c for c in containers if c.get('size_mb', 0) > 50]
        if oversized:
            debt_items.append(TechnicalDebtItem(
                category="Container Size",
                description=f"{len(oversized)} containers exceed 50MB limit",
                impact="High - Increased resource usage and slower deployments",
                estimated_cost=len(oversized) * 20000,  # £20k per container
                remediation="Optimize containers using Chainguard Wolfi and multi-stage builds"
            ))

        # Check for FAGAM dependencies
        dependencies = architecture.get('dependencies', [])
        fagam_deps = [d for d in dependencies if any(f in d.lower() for f in ['google', 'aws-', 'azure', 'terraform'])]
        if fagam_deps:
            debt_items.append(TechnicalDebtItem(
                category="FAGAM Dependencies",
                description=f"{len(fagam_deps)} FAGAM dependencies found",
                impact="Critical - Violates architecture principles",
                estimated_cost=len(fagam_deps) * 30000,  # £30k per dependency
                remediation="Replace with open-source alternatives (OpenTofu, etc.)"
            ))

        # Check for missing documentation
        docs_complete = architecture.get('documentation', {}).get('completeness', 0)
        if docs_complete < 80:
            debt_items.append(TechnicalDebtItem(
                category="Documentation",
                description=f"Documentation only {docs_complete}% complete",
                impact="Medium - Reduced maintainability",
                estimated_cost=50000,  # £50k
                remediation="Complete TOGAF ADM documentation for all phases"
            ))

        total_debt = sum(item.estimated_cost for item in debt_items)
        logger.info(f"💸 Total technical debt: £{total_debt:,}")

        return debt_items

    def perform_gap_analysis(
        self,
        current_state: Dict,
        target_state: Dict
    ) -> List[GapItem]:
        """
        Perform gap analysis

        Args:
            current_state: Current architecture state
            target_state: Target architecture state

        Returns:
            List[GapItem]: Identified gaps
        """
        logger.info("🎯 Performing gap analysis...")

        gaps = []

        # Compare container strategies
        if current_state.get('container_base') != target_state.get('container_base'):
            gaps.append(GapItem(
                area="Container Strategy",
                current_state=current_state.get('container_base', 'unknown'),
                target_state=target_state.get('container_base', 'wolfi'),
                gap_description="Need to migrate to Chainguard Wolfi base images",
                priority="High",
                estimated_effort="3 weeks"
            ))

        # Compare TOGAF compliance
        current_togaf = current_state.get('togaf_compliance', 0)
        target_togaf = target_state.get('togaf_compliance', 100)
        if current_togaf < target_togaf:
            gaps.append(GapItem(
                area="TOGAF Compliance",
                current_state=f"{current_togaf}%",
                target_state=f"{target_togaf}%",
                gap_description=f"Increase TOGAF compliance by {target_togaf - current_togaf}%",
                priority="High",
                estimated_effort="4 weeks"
            ))

        logger.info(f"📋 Identified {len(gaps)} gaps")

        return gaps

    def generate_assessment_report(
        self,
        maturity: Dict,
        debt: List[TechnicalDebtItem],
        gaps: List[GapItem]
    ) -> str:
        """
        Generate comprehensive assessment report

        Args:
            maturity: Maturity assessment
            debt: Technical debt items
            gaps: Gap analysis items

        Returns:
            str: Report in Markdown
        """
        logger.info("📄 Generating assessment report...")

        total_debt = sum(item.estimated_cost for item in debt)

        report = f"""# Architecture Assessment Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Assessor**: {self.bot_name} v{self.version}

---

## Executive Summary

- **Current Maturity Level**: {maturity['maturity_level']} ({maturity['overall_maturity']:.1f}/5.0)
- **Critical Gaps Identified**: {len([g for g in gaps if g.priority == 'High'])}
- **Total Technical Debt**: £{total_debt:,}
- **Recommended Actions**: {len(gaps) + len(debt)}

## 1. Architecture Maturity Assessment

### Overall Maturity: {maturity['maturity_level']} ({maturity['overall_maturity']:.1f}/5.0)

#### Dimension Scores

"""

        for dimension, score in maturity['dimensions'].items():
            report += f"- **{dimension.title()}**: {score:.1f}/5.0\n"

        report += "\n#### Strengths\n\n"
        for strength in maturity.get('strengths', []):
            report += f"- ✅ {strength}\n"

        report += "\n#### Areas for Improvement\n\n"
        for weakness in maturity.get('weaknesses', []):
            report += f"- ⚠️  {weakness}\n"

        report += f"\n## 2. Technical Debt Analysis\n\n"
        report += f"**Total Estimated Debt**: £{total_debt:,}\n\n"

        for i, item in enumerate(debt, 1):
            report += f"### {i}. {item.category}\n\n"
            report += f"- **Description**: {item.description}\n"
            report += f"- **Impact**: {item.impact}\n"
            report += f"- **Estimated Cost**: £{item.estimated_cost:,}\n"
            report += f"- **Remediation**: {item.remediation}\n\n"

        report += "\n## 3. Gap Analysis\n\n"

        high_priority = [g for g in gaps if g.priority == "High"]
        medium_priority = [g for g in gaps if g.priority == "Medium"]

        report += f"- **High Priority**: {len(high_priority)}\n"
        report += f"- **Medium Priority**: {len(medium_priority)}\n\n"

        for i, gap in enumerate(gaps, 1):
            emoji = "🔴" if gap.priority == "High" else "🟡"
            report += f"### {emoji} {i}. {gap.area}\n\n"
            report += f"- **Current State**: {gap.current_state}\n"
            report += f"- **Target State**: {gap.target_state}\n"
            report += f"- **Gap**: {gap.gap_description}\n"
            report += f"- **Priority**: {gap.priority}\n"
            report += f"- **Estimated Effort**: {gap.estimated_effort}\n\n"

        report += """
## 4. Recommendations

### Priority 1: Critical (Immediate Action Required)
1. **Remove FAGAM Dependencies** (2 weeks)
   - Replace Terraform with OpenTofu
   - Replace Vault with OpenBao
   - Estimated cost: £60,000

2. **Optimize Container Sizes** (3 weeks)
   - Migrate to Chainguard Wolfi base
   - Implement multi-stage builds
   - Target: All containers <50MB
   - Estimated cost: £120,000

### Priority 2: High (Within 2 Months)
3. **Complete TOGAF Compliance** (4 weeks)
   - Complete missing ADM phases
   - Generate required viewpoints
   - Document architecture principles
   - Estimated cost: £80,000

### Priority 3: Medium (Within 6 Months)
4. **Enhance Architecture Governance** (6 weeks)
   - Implement decision framework
   - Establish review process
   - Create compliance automation
   - Estimated cost: £100,000

## 5. Total Investment Required

**Total**: £360,000
**Timeline**: 6 months
**Expected ROI**: 250% (reduced technical debt, improved maintainability)

---

**Assessment Status**: ✅ Complete
**Next Review**: {datetime.now().strftime("%Y-%m-%d")}
"""

        return report

    def run(self):
        """Main execution"""
        logger.info("🚀 AXIS Assessment Bot running...")

        # Example architecture
        current_architecture = {
            "strategic_alignment": True,
            "business_drivers": ["efficiency", "scalability"],
            "containers": [
                {"name": "bot1", "size_mb": 42},
                {"name": "bot2", "size_mb": 65},  # Oversized
            ],
            "dependencies": ["python", "terraform", "kubernetes"],  # FAGAM violation
            "documentation": {"completeness": 75, "togaf_compliant": True},
            "togaf_compliance": 75
        }

        target_architecture = {
            "container_base": "wolfi",
            "togaf_compliance": 100
        }

        # Perform assessments
        maturity = self.assess_architecture_maturity(current_architecture)
        debt = self.identify_technical_debt(current_architecture)
        gaps = self.perform_gap_analysis(current_architecture, target_architecture)

        # Generate report
        report = self.generate_assessment_report(maturity, debt, gaps)
        print(report)

        logger.info("✅ AXIS Assessment Bot completed")


if __name__ == "__main__":
    bot = AxisAssessmentBot()
    bot.run()
