#!/usr/bin/env python3
"""
BSW AI Documentation Bot - Base Class
Generates domain-specific documentation using Claude AI
UK English spelling throughout
"""

import anthropic
import os
import re
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DomainDocumentationBot:
    """Base class for domain-specific documentation bots"""

    def __init__(self, domain_name: str, domain_standards: Dict):
        self.domain_name = domain_name
        self.domain_standards = domain_standards
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"

    def analyze_code_changes(self, files_changed: List[Dict]) -> Dict:
        """Analyse code changes to determine documentation updates needed"""

        analysis_prompt = f"""Analyse these code changes for {self.domain_name} domain and determine what documentation needs updating:

Files changed:
{json.dumps(files_changed, indent=2)}

Domain standards:
{json.dumps(self.domain_standards, indent=2)}

Identify:
1. What documentation files need updating (README.md, API docs, wiki pages)
2. What specific sections need changes
3. What new documentation is needed
4. Any compliance issues with domain standards

Return JSON format:
{{
    "readme_updates": [{{section: "...", reason: "...", priority: "high|medium|low"}}],
    "api_doc_updates": [{{endpoint: "...", changes_needed: "..."}}],
    "wiki_updates": [{{page: "...", section: "...", update_type: "new|modify|delete"}}],
    "compliance_issues": [{{issue: "...", severity: "critical|warning|info"}}]
}}"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": analysis_prompt}]
        )

        response_text = message.content[0].text

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))

        return {"error": "Could not parse analysis response"}

    def generate_readme_section(self, section_name: str, context: Dict) -> str:
        """Generate or update a specific README section"""

        section_prompt = f"""Generate UK English documentation for {self.domain_name} domain README.md section: {section_name}

Context:
{json.dumps(context, indent=2)}

Domain standards:
{json.dumps(self.domain_standards, indent=2)}

Requirements:
- UK English spelling (colour, initialise, organisation)
- Follow {self.domain_name} domain conventions
- Include badges where appropriate (build status, coverage, version)
- Use semantic versioning
- Include metadata headers
- Professional technical writing style
- Clear, concise, actionable content

Generate ONLY the section content, properly formatted in Markdown."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            messages=[{"role": "user", "content": section_prompt}]
        )

        return message.content[0].text

    def generate_api_documentation(self, endpoint_info: Dict) -> str:
        """Generate API documentation for an endpoint"""

        api_prompt = f"""Generate comprehensive API documentation for this {self.domain_name} endpoint:

Endpoint info:
{json.dumps(endpoint_info, indent=2)}

Domain standards:
{json.dumps(self.domain_standards, indent=2)}

Include:
- Endpoint description
- HTTP method and URL
- Request parameters (path, query, body)
- Request examples (curl, Python, JavaScript)
- Response format and examples
- Error codes and handling
- Rate limiting information
- Authentication requirements
- UK English spelling throughout

Format in Markdown suitable for API documentation."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            messages=[{"role": "user", "content": api_prompt}]
        )

        return message.content[0].text

    def generate_wiki_page(self, page_info: Dict) -> str:
        """Generate wiki page content"""

        wiki_prompt = f"""Generate comprehensive wiki page for {self.domain_name} domain:

Page info:
{json.dumps(page_info, indent=2)}

Domain standards:
{json.dumps(self.domain_standards, indent=2)}

Requirements:
- UK English spelling
- Clear structure with proper headings
- Include diagrams (Mermaid syntax) where helpful
- Code examples where relevant
- Links to related documentation
- Metadata and categorisation
- Professional technical writing

Generate complete wiki page in Markdown format."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=16384,
            messages=[{"role": "user", "content": wiki_prompt}]
        )

        return message.content[0].text

    def validate_documentation(self, doc_content: str, doc_type: str) -> Dict:
        """Validate documentation against domain standards"""

        validation_prompt = f"""Validate this {doc_type} documentation for {self.domain_name} domain compliance:

Documentation:
{doc_content}

Domain standards:
{json.dumps(self.domain_standards, indent=2)}

Check for:
1. UK English spelling (flag US spellings)
2. Domain-specific terminology compliance
3. Completeness (all required sections)
4. Technical accuracy
5. Formatting and structure
6. Metadata and badges
7. Links and references

Return JSON:
{{
    "valid": true|false,
    "score": 0-100,
    "issues": [{{type: "error|warning|info", message: "...", line: number}}],
    "suggestions": ["..."]
}}"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": validation_prompt}]
        )

        response_text = message.content[0].text

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))

        return {"error": "Could not parse validation response"}

    def process_webhook_event(self, webhook_payload: Dict) -> Dict:
        """Main entry point: process webhook event and generate documentation"""

        logger.info(f"Processing webhook for {self.domain_name} domain")

        # Extract files changed from webhook
        files_changed = self._extract_files_from_webhook(webhook_payload)

        if not files_changed:
            return {"status": "no_files_changed", "domain": self.domain_name}

        # Analyse what documentation needs updating
        analysis = self.analyze_code_changes(files_changed)

        results = {
            "domain": self.domain_name,
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "documentation_generated": []
        }

        # Generate README updates
        for update in analysis.get("readme_updates", []):
            if update.get("priority") in ["high", "medium"]:
                content = self.generate_readme_section(
                    update["section"],
                    {"files_changed": files_changed, "reason": update["reason"]}
                )
                results["documentation_generated"].append({
                    "type": "readme_section",
                    "section": update["section"],
                    "content": content[:500] + "..." if len(content) > 500 else content
                })

        # Generate API documentation updates
        for api_update in analysis.get("api_doc_updates", []):
            content = self.generate_api_documentation(api_update)
            results["documentation_generated"].append({
                "type": "api_documentation",
                "endpoint": api_update.get("endpoint"),
                "content": content[:500] + "..." if len(content) > 500 else content
            })

        # Generate wiki updates
        for wiki_update in analysis.get("wiki_updates", []):
            if wiki_update.get("update_type") in ["new", "modify"]:
                content = self.generate_wiki_page(wiki_update)
                results["documentation_generated"].append({
                    "type": "wiki_page",
                    "page": wiki_update.get("page"),
                    "content": content[:500] + "..." if len(content) > 500 else content
                })

        logger.info(f"Generated {len(results['documentation_generated'])} documentation updates")

        return results

    def _extract_files_from_webhook(self, webhook_payload: Dict) -> List[Dict]:
        """Extract changed files from webhook payload"""

        files = []

        # Handle Codeberg/Forgejo webhook format
        if "commits" in webhook_payload:
            for commit in webhook_payload["commits"]:
                for file_path in commit.get("added", []):
                    files.append({"path": file_path, "status": "added", "commit": commit["id"]})
                for file_path in commit.get("modified", []):
                    files.append({"path": file_path, "status": "modified", "commit": commit["id"]})
                for file_path in commit.get("removed", []):
                    files.append({"path": file_path, "status": "removed", "commit": commit["id"]})

        return files


if __name__ == "__main__":
    # Test example
    test_standards = {
        "uk_english": True,
        "include_badges": True,
        "versioning": "semver",
        "framework": "TOGAF"
    }

    bot = DomainDocumentationBot("AXIS", test_standards)

    test_webhook = {
        "commits": [{
            "id": "abc123",
            "added": ["src/new_service.py"],
            "modified": ["README.md"],
            "removed": []
        }]
    }

    result = bot.process_webhook_event(test_webhook)
    print(json.dumps(result, indent=2))
