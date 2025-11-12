#!/usr/bin/env python3
"""
AXIS Documentation Bot - Architecture Documentation Generation

Purpose: Generates and maintains architecture documentation with TOGAF compliance,
         ArchiMate notation, and UK English standards.

Domain: AXIS (Architecture)
Category: Documentation & Knowledge Management
Version: 1.0.0
"""

import os
import sys
import yaml
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('axis-docs-bot')


class DocumentationType(Enum):
    """Documentation types supported"""
    ARCHITECTURE_VISION = "architecture-vision"
    BUSINESS_ARCHITECTURE = "business-architecture"
    INFORMATION_SYSTEMS = "information-systems"
    TECHNOLOGY_ARCHITECTURE = "technology-architecture"
    OPPORTUNITIES_SOLUTIONS = "opportunities-solutions"
    MIGRATION_PLANNING = "migration-planning"
    IMPLEMENTATION_GOVERNANCE = "implementation-governance"
    ARCHITECTURE_CHANGE = "architecture-change"
    REQUIREMENTS = "requirements"
    BLUEPRINT = "blueprint"


class NotationType(Enum):
    """Diagram notation types"""
    ARCHIMATE = "archimate"
    C4_MODEL = "c4"
    MERMAID = "mermaid"
    UML = "uml"


@dataclass
class DocumentMetadata:
    """Documentation metadata"""
    title: str
    version: str
    date: str
    author: str
    domain: str
    category: str
    togaf_phase: Optional[str] = None
    archimate_layer: Optional[str] = None


class AxisDocsBot:
    """AXIS Documentation Bot for architecture documentation generation"""

    def __init__(self, docs_path: Optional[str] = None):
        """
        Initialise AXIS Documentation Bot

        Args:
            docs_path: Path to documentation repository
        """
        self.docs_path = docs_path or os.getenv("DOCS_PATH", "/opt/documentation/docs")
        self.bot_domain = "AXIS"
        self.bot_name = "axis-docs-bot"
        self.version = "1.0.0"

        logger.info(f"🏗️  {self.bot_name} v{self.version} starting...")
        logger.info(f"📚 Documentation path: {self.docs_path}")

        # Verify documentation path exists
        if not Path(self.docs_path).exists():
            logger.warning(f"⚠️  Documentation path not found: {self.docs_path}")

    def generate_architecture_vision(
        self,
        project_name: str,
        stakeholders: List[str],
        business_goals: List[str],
        constraints: List[str]
    ) -> str:
        """
        Generate TOGAF Architecture Vision (Phase A)

        Args:
            project_name: Name of the architecture project
            stakeholders: List of key stakeholders
            business_goals: Business goals and drivers
            constraints: Architecture constraints

        Returns:
            str: Architecture vision document in Markdown
        """
        logger.info("📖 Generating Architecture Vision (TOGAF Phase A)")

        metadata = DocumentMetadata(
            title=f"Architecture Vision: {project_name}",
            version="1.0.0",
            date=datetime.now().strftime("%Y-%m-%d"),
            author="AXIS Documentation Bot",
            domain="AXIS",
            category="Architecture Vision",
            togaf_phase="Phase A"
        )

        doc = self._create_document_header(metadata)

        doc += f"""
## Executive Summary

This document presents the Architecture Vision for {project_name}, establishing the high-level
architecture approach and defining the scope of the architecture engagement.

## Business Context

### Stakeholders

"""
        for stakeholder in stakeholders:
            doc += f"- {stakeholder}\n"

        doc += "\n### Business Goals and Drivers\n\n"
        for i, goal in enumerate(business_goals, 1):
            doc += f"{i}. {goal}\n"

        doc += "\n### Architecture Constraints\n\n"
        for constraint in constraints:
            doc += f"- {constraint}\n"

        doc += """
## Architecture Principles

### 1. FAGAM Prohibition
**Principle**: No use of Facebook, Apple, Google, Amazon, Microsoft, or HashiCorp products.

**Rationale**: Maintain independence from proprietary platforms and ensure open-source compliance.

**Implications**:
- Use Codeberg instead of GitHub (for primary hosting)
- Use OpenTofu instead of Terraform
- Use OpenBao instead of HashiCorp Vault
- Use Chainguard Wolfi instead of proprietary base images

### 2. Container Efficiency
**Principle**: All containers must be <50MB in size.

**Rationale**: Minimise resource consumption, improve startup times, and reduce attack surface.

**Implications**:
- Use apko + Chainguard Wolfi base images
- Implement multi-stage builds
- Remove unnecessary dependencies

### 3. TOGAF Compliance
**Principle**: Architecture must comply with TOGAF 10 Enterprise Architecture Framework.

**Rationale**: Ensure industry-standard architecture methodology and documentation.

**Implications**:
- Follow ADM phases systematically
- Use ArchiMate 3.2 notation for diagrams
- Maintain architecture repository

### 4. UK English Standards
**Principle**: All documentation must use UK English spelling and grammar.

**Rationale**: Maintain consistency with organisational standards.

**Implications**:
- Use "favour" not "favor", "organise" not "organize"
- Follow UK date formats (DD/MM/YYYY)
- Use UK terminology throughout

## Architecture Vision

### Target Architecture Overview

```mermaid
graph TB
    subgraph "Bot Factory Architecture"
        PIPE[PIPE Domain<br/>48 Bots]
        AXIS[AXIS Domain<br/>45 Bots]
        IV[IV Domain<br/>44 Bots]
        ECO[ECO Domain<br/>48 Bots]
        BNI[BNI Domain<br/>37 Bots]
        BNP[BNP Domain<br/>37 Bots]
        BU[BU Domain<br/>42 Bots]
        DC[DC Domain<br/>30 Bots]
    end

    subgraph "Infrastructure"
        K8S[Kubernetes<br/>Orchestration]
        META[META-KERAGR<br/>Knowledge Graph]
        CICD[GitOps<br/>CI/CD]
    end

    PIPE --> K8S
    AXIS --> META
    IV --> META
    ECO --> K8S
    K8S --> CICD
```

### Architecture Scope

**In Scope**:
- 185 autonomous bots across 8 domains
- Container-based deployment (<50MB per container)
- Hybrid knowledge base (META-KERAGR)
- GitOps CI/CD pipeline
- Kubernetes orchestration

**Out of Scope**:
- Legacy system migration (Phase 2)
- FAGAM platform integration
- Traditional VM-based deployment

## Next Steps

1. **Phase B**: Business Architecture Development
2. **Phase C**: Information Systems Architecture
3. **Phase D**: Technology Architecture
4. **Phase E**: Opportunities and Solutions
5. **Phase F**: Migration Planning

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Enterprise Architect | | | |
| Technical Lead | | | |
| Project Sponsor | | | |

---

**Document Status**: ✅ Complete
**TOGAF Phase**: A - Architecture Vision
**Next Review**: {(datetime.now().strftime("%Y-%m-%d"))}
"""

        return doc

    def generate_mermaid_diagram(
        self,
        diagram_type: str,
        components: List[Dict[str, str]],
        relationships: List[Dict[str, str]]
    ) -> str:
        """
        Generate Mermaid diagram

        Args:
            diagram_type: Type of diagram (graph, flowchart, sequence)
            components: List of component definitions
            relationships: List of relationships between components

        Returns:
            str: Mermaid diagram code
        """
        logger.info(f"🎨 Generating {diagram_type} diagram")

        diagram = f"```mermaid\n{diagram_type} TB\n"

        # Add components
        for comp in components:
            comp_id = comp['id']
            comp_label = comp['label']
            diagram += f"    {comp_id}[{comp_label}]\n"

        diagram += "\n"

        # Add relationships
        for rel in relationships:
            source = rel['source']
            target = rel['target']
            label = rel.get('label', '')
            if label:
                diagram += f"    {source} -->|{label}| {target}\n"
            else:
                diagram += f"    {source} --> {target}\n"

        diagram += "```\n"

        return diagram

    def validate_uk_english(self, text: str) -> List[str]:
        """
        Validate UK English spelling

        Args:
            text: Text to validate

        Returns:
            List[str]: List of US spelling violations found
        """
        logger.info("🔍 Validating UK English spelling")

        # Common US -> UK spelling pairs
        us_spellings = {
            'favor': 'favour',
            'color': 'colour',
            'organize': 'organise',
            'analyze': 'analyse',
            'center': 'centre',
            'defense': 'defence',
            'license': 'licence',  # noun form
            'meter': 'metre',  # measurement
            'fiber': 'fibre',
            'traveled': 'travelled',
        }

        violations = []
        text_lower = text.lower()

        for us_word, uk_word in us_spellings.items():
            if us_word in text_lower:
                violations.append(f"Found US spelling '{us_word}', should be '{uk_word}'")

        if violations:
            logger.warning(f"⚠️  Found {len(violations)} UK English violations")
        else:
            logger.info("✅ UK English validation passed")

        return violations

    def _create_document_header(self, metadata: DocumentMetadata) -> str:
        """
        Create standard document header

        Args:
            metadata: Document metadata

        Returns:
            str: Document header in Markdown
        """
        header = f"""# {metadata.title}

**Version**: {metadata.version}
**Date**: {metadata.date}
**Author**: {metadata.author}
**Domain**: {metadata.domain}
**Category**: {metadata.category}
"""

        if metadata.togaf_phase:
            header += f"**TOGAF Phase**: {metadata.togaf_phase}\n"

        if metadata.archimate_layer:
            header += f"**ArchiMate Layer**: {metadata.archimate_layer}\n"

        header += "\n---\n"

        return header

    def save_documentation(self, content: str, filename: str) -> bool:
        """
        Save documentation to file

        Args:
            content: Documentation content
            filename: Output filename

        Returns:
            bool: True if saved successfully
        """
        try:
            output_path = Path(self.docs_path) / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"✅ Documentation saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Error saving documentation: {e}")
            return False

    def generate_bot_documentation(self, bot_config: Dict) -> str:
        """
        Generate documentation for a bot

        Args:
            bot_config: Bot configuration dictionary

        Returns:
            str: Bot documentation in Markdown
        """
        logger.info(f"📝 Generating documentation for {bot_config.get('name', 'unknown')}")

        bot_name = bot_config.get('name', 'Unknown Bot')
        bot_domain = bot_config.get('domain', 'Unknown')
        bot_purpose = bot_config.get('purpose', 'Not specified')
        bot_category = bot_config.get('category', 'General')

        metadata = DocumentMetadata(
            title=f"{bot_name} - Technical Specification",
            version="1.0.0",
            date=datetime.now().strftime("%Y-%m-%d"),
            author="AXIS Documentation Bot",
            domain=bot_domain,
            category=bot_category
        )

        doc = self._create_document_header(metadata)

        doc += f"""
## Overview

**Bot Name**: {bot_name}
**Domain**: {bot_domain}
**Category**: {bot_category}
**Purpose**: {bot_purpose}

## Responsibilities

"""
        responsibilities = bot_config.get('responsibilities', [])
        for resp in responsibilities:
            doc += f"- {resp}\n"

        doc += "\n## Technical Specifications\n\n"

        # Container specs
        doc += "### Container\n\n"
        doc += "```yaml\n"
        doc += f"name: {bot_name}\n"
        doc += f"domain: {bot_domain}\n"
        doc += "base_image: cgr.dev/chainguard/wolfi-base:latest\n"
        doc += "max_size: 50MB\n"
        doc += "```\n\n"

        # Dependencies
        doc += "### Dependencies\n\n"
        dependencies = bot_config.get('dependencies', [])
        for dep in dependencies:
            doc += f"- {dep}\n"

        doc += "\n### API Endpoints\n\n"
        endpoints = bot_config.get('endpoints', [])
        for endpoint in endpoints:
            doc += f"- `{endpoint.get('method', 'GET')} {endpoint.get('path', '/')}`"
            doc += f" - {endpoint.get('description', '')}\n"

        doc += "\n## Deployment\n\n"
        doc += "```bash\n"
        doc += f"# Build container\n"
        doc += f"docker build -t {bot_name}:1.0.0 .\n\n"
        doc += f"# Deploy to Kubernetes\n"
        doc += f"kubectl apply -f deployments/{bot_name}.yaml\n"
        doc += "```\n"

        return doc

    def run(self):
        """Main bot execution"""
        logger.info("🚀 AXIS Documentation Bot running...")

        # Example: Generate architecture vision
        vision = self.generate_architecture_vision(
            project_name="BSW-Arch Bot Factory",
            stakeholders=[
                "Enterprise Architecture Team",
                "Development Team",
                "Operations Team",
                "Business Stakeholders"
            ],
            business_goals=[
                "Deploy 185 autonomous bots across 8 domains",
                "Achieve <50MB container sizes",
                "Maintain FAGAM prohibition compliance",
                "Implement TOGAF 10 architecture framework"
            ],
            constraints=[
                "No FAGAM dependencies allowed",
                "Container size limit: 50MB",
                "UK English documentation only",
                "TOGAF 10 compliance required"
            ]
        )

        # Validate UK English
        violations = self.validate_uk_english(vision)
        if violations:
            logger.warning("⚠️  UK English violations found:")
            for violation in violations:
                logger.warning(f"  - {violation}")

        logger.info("✅ AXIS Documentation Bot completed successfully")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AXIS Documentation Bot")
    parser.add_argument(
        '--docs-path',
        type=str,
        default=os.getenv("DOCS_PATH", "/opt/documentation/docs"),
        help="Path to documentation repository"
    )
    parser.add_argument(
        '--generate',
        type=str,
        choices=['vision', 'architecture', 'blueprint'],
        help="Generate specific documentation type"
    )
    parser.add_argument(
        '--output',
        type=str,
        help="Output file path"
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help="Validate UK English spelling"
    )

    args = parser.parse_args()

    # Create bot instance
    bot = AxisDocsBot(docs_path=args.docs_path)

    # Run bot
    bot.run()


if __name__ == "__main__":
    main()
