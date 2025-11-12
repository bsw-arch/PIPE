#!/usr/bin/env python3
"""
PIPE Domain Documentation Bot
Protocol & Infrastructure Platform Engineering - DevOps/GitOps documentation
UK English spelling throughout
"""

from domain_documentation_bot import DomainDocumentationBot
import json


class PIPEDocumentationBot(DomainDocumentationBot):
    """PIPE domain documentation bot - Infrastructure & DevOps"""

    def __init__(self):
        pipe_standards = {
            "domain": "PIPE",
            "full_name": "Protocol & Infrastructure Platform Engineering",
            "uk_english": True,
            "include_badges": True,
            "versioning": "semver",
            "frameworks": ["DevOps", "GitOps", "SRE", "Platform Engineering"],
            "port_range": "5000-5299",
            "organizations": 13,
            "required_sections": [
                "Infrastructure Overview",
                "Deployment Architecture",
                "CI/CD Pipeline",
                "Infrastructure as Code",
                "Monitoring & Observability",
                "Security & Compliance",
                "Runbooks & Procedures"
            ],
            "terminology": {
                "infrastructure": "platform infrastructure",
                "deployment": "continuous deployment",
                "monitoring": "observability",
                "automation": "infrastructure automation"
            },
            "diagram_requirements": {
                "infrastructure_diagrams": "Mermaid deployment or C4 Container",
                "pipeline_diagrams": "Mermaid flowchart or sequenceDiagram",
                "network_diagrams": "Mermaid graph"
            },
            "iac_tools": ["OpenTofu", "Terraform", "Ansible", "Helm"],
            "cicd_tools": ["Woodpecker CI", "Forgejo Actions", "ArgoCD"],
            "observability_tools": ["Prometheus", "Grafana", "Loki", "Jaeger"],
            "metadata_requirements": {
                "deployment_tier": "Development|Staging|Production",
                "infrastructure_layer": "Compute|Network|Storage|Security",
                "automation_level": "Manual|Semi-Automated|Fully Automated",
                "sla_tier": "Standard|Enhanced|Critical"
            }
        }

        super().__init__("PIPE", pipe_standards)

    def generate_runbook(self, service_info: dict) -> str:
        """Generate operational runbook for infrastructure service"""

        runbook_prompt = f"""Generate an operational runbook for this PIPE infrastructure service:

Service Info:
{json.dumps(service_info, indent=2)}

Runbook Structure:
# {{Service Name}} Operational Runbook

## Service Overview
- Purpose and function
- Dependencies
- SLA requirements

## Architecture
- Component diagram (Mermaid)
- Infrastructure topology
- Network configuration

## Deployment
- Prerequisites
- Deployment steps (IaC commands)
- Rollback procedure

## Monitoring
- Health check endpoints
- Key metrics and thresholds
- Alert conditions

## Troubleshooting
### Common Issues
1. Issue: ...
   Symptoms: ...
   Resolution: ...

## Incident Response
- Escalation path
- Emergency contacts
- Recovery procedures

## Maintenance
- Backup procedures
- Update procedures
- Capacity planning

Use UK English. Include specific commands and configurations.
Focus on operational clarity for SRE teams."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=12000,
            messages=[{"role": "user", "content": runbook_prompt}]
        )

        return message.content[0].text

    def generate_cicd_pipeline_docs(self, pipeline_config: dict) -> str:
        """Generate CI/CD pipeline documentation"""

        pipeline_prompt = f"""Generate comprehensive CI/CD pipeline documentation for PIPE domain:

Pipeline Configuration:
{json.dumps(pipeline_config, indent=2)}

Documentation Requirements:
# {{Pipeline Name}} CI/CD Pipeline

## Pipeline Overview
- Purpose and scope
- Trigger conditions
- Execution environment

## Pipeline Stages
### 1. Build Stage
- Build tools and commands
- Artefact generation
- Build optimisations

### 2. Test Stage
- Unit tests
- Integration tests
- Security scanning (SAST, DAST)

### 3. Package Stage
- Container image building
- Package repository push
- Versioning strategy

### 4. Deploy Stage
- Deployment targets
- Deployment strategy (blue-green, canary, rolling)
- Infrastructure provisioning

## Pipeline Diagram
[Mermaid flowchart showing complete pipeline flow]

## Configuration
- Environment variables
- Secrets management (Vault integration)
- Pipeline parameters

## Monitoring
- Pipeline metrics
- Success/failure tracking
- Performance benchmarks

## Troubleshooting
Common pipeline failures and resolutions

Use UK English. Be specific with tool names and commands.
Include actual code examples."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=12000,
            messages=[{"role": "user", "content": pipeline_prompt}]
        )

        return message.content[0].text

    def generate_iac_documentation(self, iac_module: dict) -> str:
        """Generate Infrastructure as Code module documentation"""

        iac_prompt = f"""Generate IaC module documentation for this PIPE infrastructure component:

IaC Module:
{json.dumps(iac_module, indent=2)}

Documentation Structure:
# {{Module Name}} Infrastructure Module

## Module Purpose
What infrastructure does this module provision?

## Architecture
[Mermaid deployment diagram]

## Inputs
| Variable | Type | Description | Default | Required |
|----------|------|-------------|---------|----------|
| ... | ... | ... | ... | ... |

## Outputs
| Output | Type | Description | Sensitive |
|--------|------|-------------|-----------|
| ... | ... | ... | ... |

## Resources Created
- Resource type and configuration
- Dependencies
- Security considerations

## Usage Example
```hcl
module "{{module_name}}" {{
  source = "..."

  # Configuration
  ...
}}
```

## State Management
- Backend configuration
- State locking
- Remote state access

## Security
- IAM roles and policies
- Network security groups
- Encryption configurations

## Testing
- Validation commands
- Test scenarios
- Compliance checks

Use UK English. Target OpenTofu/Terraform users.
Include practical examples."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=10000,
            messages=[{"role": "user", "content": iac_prompt}]
        )

        return message.content[0].text


if __name__ == "__main__":
    bot = PIPEDocumentationBot()

    # Test runbook generation
    service_info = {
        "name": "Vault HA Cluster",
        "purpose": "Secrets management with high availability",
        "dependencies": ["Consul", "PostgreSQL"],
        "sla": "99.9% uptime",
        "endpoints": ["http://vault.local:8200/v1/sys/health"]
    }

    runbook = bot.generate_runbook(service_info)
    print("=== PIPE Runbook ===")
    print(runbook[:1000] + "..." if len(runbook) > 1000 else runbook)

    # Test pipeline docs
    pipeline_config = {
        "name": "BSW-PIPE-Deploy",
        "trigger": "push to main",
        "stages": ["build", "test", "security-scan", "deploy"],
        "tools": ["Woodpecker CI", "Trivy", "OpenTofu"]
    }

    pipeline_docs = bot.generate_cicd_pipeline_docs(pipeline_config)
    print("\n=== PIPE CI/CD Pipeline Docs ===")
    print(pipeline_docs[:1000] + "..." if len(pipeline_docs) > 1000 else pipeline_docs)
