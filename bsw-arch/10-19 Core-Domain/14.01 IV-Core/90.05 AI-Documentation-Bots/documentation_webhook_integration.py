#!/usr/bin/env python3
"""
AI Documentation Bot Webhook Integration
Integrates domain documentation bots with Codeberg webhook handler
UK English spelling throughout
"""

from flask import Flask, request, jsonify
import sys
import os

# Add bots directory to path
sys.path.insert(0, os.path.dirname(__file__))

from axis_documentation_bot import AXISDocumentationBot
from pipe_documentation_bot import PIPEDocumentationBot
from iv_documentation_bot import IVDocumentationBot
from ecox_documentation_bot import ECOXDocumentationBot

import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize domain bots
DOMAIN_BOTS = {
    "AXIS": AXISDocumentationBot(),
    "PIPE": PIPEDocumentationBot(),
    "IV": IVDocumentationBot(),
    "ECOX": ECOXDocumentationBot()
}


def determine_domain_from_repository(repo_name: str) -> str:
    """Determine which domain a repository belongs to"""

    repo_lower = repo_name.lower()

    # AXIS patterns
    if any(keyword in repo_lower for keyword in [
        'axis', 'architecture', 'governance', 'togaf', 'archimate',
        'zachman', 'enterprise-arch', 'ea-'
    ]):
        return "AXIS"

    # PIPE patterns
    if any(keyword in repo_lower for keyword in [
        'pipe', 'infrastructure', 'devops', 'cicd', 'deployment',
        'terraform', 'opentofu', 'ansible', 'kubernetes', 'k3s'
    ]):
        return "PIPE"

    # IV patterns
    if any(keyword in repo_lower for keyword in [
        'iv', 'ai', 'ml', 'rag', 'llm', 'keragr', 'intelliverse',
        'embedding', 'vector', 'knowledge-graph'
    ]):
        return "IV"

    # ECOX patterns
    if any(keyword in repo_lower for keyword in [
        'ecox', 'eco', 'sustainability', 'esg', 'green', 'carbon'
    ]):
        return "ECOX"

    # Default to AXIS for architecture-related
    return "AXIS"


@app.route('/webhook/documentation', methods=['POST'])
def handle_documentation_webhook():
    """Handle incoming webhooks and route to appropriate documentation bot"""

    try:
        webhook_payload = request.json
        logger.info(f"Received documentation webhook: {json.dumps(webhook_payload, indent=2)[:500]}")

        # Extract repository info
        repository = webhook_payload.get('repository', {})
        repo_name = repository.get('name', '')
        repo_full_name = repository.get('full_name', '')

        if not repo_name:
            return jsonify({"error": "No repository name in webhook"}), 400

        # Determine domain
        domain = determine_domain_from_repository(repo_name)
        logger.info(f"Repository '{repo_name}' mapped to domain: {domain}")

        # Get appropriate bot
        bot = DOMAIN_BOTS.get(domain)
        if not bot:
            return jsonify({"error": f"No bot found for domain: {domain}"}), 404

        # Process webhook with domain bot
        result = bot.process_webhook_event(webhook_payload)

        # Log results
        logger.info(f"Documentation generation complete for {domain}")
        logger.info(f"Generated {len(result.get('documentation_generated', []))} documentation updates")

        # Return response
        response = {
            "status": "success",
            "domain": domain,
            "repository": repo_full_name,
            "timestamp": datetime.now().isoformat(),
            "documentation_updates": len(result.get('documentation_generated', [])),
            "result": result
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error processing documentation webhook: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/documentation/test', methods=['POST'])
def test_documentation_bot():
    """Test endpoint for documentation bot"""

    try:
        test_data = request.json
        domain = test_data.get('domain', 'AXIS')

        bot = DOMAIN_BOTS.get(domain)
        if not bot:
            return jsonify({"error": f"Unknown domain: {domain}"}), 400

        # Create test webhook payload
        test_webhook = {
            "repository": {
                "name": f"test-{domain.lower()}-repo",
                "full_name": f"bsw-arch/test-{domain.lower()}-repo"
            },
            "commits": [{
                "id": "test123",
                "message": "Test commit for documentation bot",
                "added": ["src/new_feature.py"],
                "modified": ["README.md"],
                "removed": []
            }]
        }

        result = bot.process_webhook_event(test_webhook)

        return jsonify({
            "status": "test_success",
            "domain": domain,
            "result": result
        }), 200

    except Exception as e:
        logger.error(f"Error in test endpoint: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/documentation/bots/status', methods=['GET'])
def bots_status():
    """Get status of all documentation bots"""

    status = {
        "timestamp": datetime.now().isoformat(),
        "bots": {}
    }

    for domain_name, bot in DOMAIN_BOTS.items():
        status["bots"][domain_name] = {
            "status": "active",
            "domain_standards": bot.domain_standards,
            "model": bot.model
        }

    return jsonify(status), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Documentation Bot Integration",
        "bots_loaded": len(DOMAIN_BOTS),
        "domains": list(DOMAIN_BOTS.keys())
    }), 200


if __name__ == '__main__':
    logger.info("Starting AI Documentation Bot Webhook Integration")
    logger.info(f"Loaded {len(DOMAIN_BOTS)} domain bots: {', '.join(DOMAIN_BOTS.keys())}")

    # Check for Anthropic API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        logger.warning("ANTHROPIC_API_KEY not set - bots will fail to generate documentation")

    app.run(host='0.0.0.0', port=8004, debug=True)
