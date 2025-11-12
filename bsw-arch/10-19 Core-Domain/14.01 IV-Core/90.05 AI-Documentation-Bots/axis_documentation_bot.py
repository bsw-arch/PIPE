#!/usr/bin/env python3
"""
AXIS Domain Documentation Bot
Architecture Governance - TOGAF/ArchiMate/Zachman compliance
UK English spelling throughout
"""

from domain_documentation_bot import DomainDocumentationBot
import json


class AXISDocumentationBot(DomainDocumentationBot):
    """AXIS domain documentation bot - Architecture Governance"""

    def __init__(self):
        axis_standards = {
            "domain": "AXIS",
            "full_name": "Architecture Excellence & Integration Standards",
            "uk_english": True,
            "include_badges": True,
            "versioning": "semver",
            "frameworks": ["TOGAF", "ArchiMate", "Zachman", "COBIT"],
            "port_range": "4000-4299",
            "organizations": 13,
            "required_sections": [
                "Architecture Overview",
                "TOGAF Compliance",
                "ArchiMate Models",
                "Governance Framework",
                "Integration Standards",
                "Quality Attributes",
                "Decision Records (ADRs)"
            ],
            "terminology": {
                "architecture": "enterprise architecture",
                "governance": "architecture governance",
                "standards": "architecture standards",
                "compliance": "standards compliance"
            },
            "diagram_requirements": {
                "architecture_diagrams": "ArchiMate or Mermaid C4",
                "flow_diagrams": "Mermaid flowchart or sequence",
                "deployment_diagrams": "Mermaid deployment"
            },
            "metadata_requirements": {
                "architecture_tier": "Strategic|Tactical|Operational",
                "togaf_phase": "Preliminary|A|B|C|D|E|F|G|H",
                "archimate_viewpoint": "Organisation|Application|Technology|Physical|Motivation|Strategy|Implementation",
                "maturity_level": "Initial|Managed|Defined|Quantitatively Managed|Optimising"
            }
        }

        super().__init__("AXIS", axis_standards)

    def generate_architecture_decision_record(self, decision_context: dict) -> str:
        """Generate Architecture Decision Record (ADR) in TOGAF format"""

        adr_prompt = f"""Generate an Architecture Decision Record (ADR) for AXIS domain in TOGAF format:

Decision Context:
{json.dumps(decision_context, indent=2)}

ADR Template Requirements:
# ADR-{{number}}: {{Title}}

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that we're seeing that is motivating this decision or change?

## Decision
What is the change that we're proposing and/or doing?

## TOGAF Phase
Which TOGAF ADM phase does this relate to?

## ArchiMate Viewpoint
Which ArchiMate viewpoint(s) are affected?

## Consequences
What becomes easier or more difficult to do because of this change?

## Alternatives Considered
What other options were evaluated?

## Compliance Impact
How does this affect architecture governance and standards compliance?

Use UK English spelling throughout. Be specific and technical."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            messages=[{"role": "user", "content": adr_prompt}]
        )

        return message.content[0].text

    def generate_archimate_diagram(self, component_info: dict) -> str:
        """Generate ArchiMate diagram in Mermaid syntax"""

        diagram_prompt = f"""Generate an ArchiMate-style diagram in Mermaid syntax for this AXIS component:

Component Info:
{json.dumps(component_info, indent=2)}

ArchiMate Layer Guidelines:
- Business Layer: Yellow (#FFFFB5)
- Application Layer: Light Blue (#B5FFFF)
- Technology Layer: Green (#C9E7B7)
- Physical Layer: Grey (#E8E8E8)
- Motivation Layer: Light Grey (#CCCCCC)
- Strategy Layer: Light Orange (#FFE0B5)
- Implementation & Migration Layer: Pink (#FFE0E0)

Generate Mermaid flowchart diagram representing ArchiMate concepts.
Use appropriate colours and layer separation.
Include relationships and dependencies.
UK English in all labels."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": diagram_prompt}]
        )

        return message.content[0].text

    def validate_togaf_compliance(self, documentation: str) -> dict:
        """Validate documentation for TOGAF compliance"""

        togaf_validation_prompt = f"""Validate this AXIS documentation for TOGAF ADM compliance:

Documentation:
{documentation}

Check for:
1. TOGAF phase identification (Preliminary, A-H, Requirements Management)
2. Architecture Building Blocks (ABBs) properly defined
3. Solution Building Blocks (SBBs) properly defined
4. Stakeholder concerns addressed
5. Architecture principles referenced
6. Viewpoints and views properly structured
7. Gap analysis present where appropriate
8. Migration planning considered

Return JSON:
{{
    "togaf_compliant": true|false,
    "identified_phase": "...",
    "abbs_defined": true|false,
    "sbbs_defined": true|false,
    "stakeholder_analysis": true|false,
    "architecture_principles": ["..."],
    "viewpoints_used": ["..."],
    "compliance_score": 0-100,
    "recommendations": ["..."]
}}"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": togaf_validation_prompt}]
        )

        response_text = message.content[0].text
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))

        return {"error": "Could not parse TOGAF validation response"}


if __name__ == "__main__":
    bot = AXISDocumentationBot()

    # Test ADR generation
    decision_context = {
        "title": "Adopt Microservices Architecture for Payment Processing",
        "problem": "Current monolithic payment system cannot scale to meet demand",
        "proposed_solution": "Migrate to microservices using domain-driven design",
        "togaf_phase": "C - Information Systems Architecture",
        "archimate_viewpoint": "Application"
    }

    adr = bot.generate_architecture_decision_record(decision_context)
    print("=== AXIS ADR ===")
    print(adr)
    print("\n=== TOGAF Validation ===")
    validation = bot.validate_togaf_compliance(adr)
    print(json.dumps(validation, indent=2))
