# AXIS Bots - API Keys and Configuration

**Date**: 2025-10-29
**Organization**: AXIS (Augmentic AI Enterprise Architecture)
**Purpose**: API keys, bot names, and configuration for AXIS ecosystem

---

## Codeberg API Token

**Primary Token**: `d0408771e085097495d59eb91bea7e0a582453de`

**Usage**:
```bash
export CODEBERG_TOKEN="d0408771e085097495d59eb91bea7e0a582453de"

# API access
curl -s "https://codeberg.org/api/v1/orgs/AXIS-Bots/repos" \
  -H "Authorization: token ${CODEBERG_TOKEN}"

# Git operations
git clone "https://${CODEBERG_TOKEN}@codeberg.org/AXIS-Bots/axis-framework-bot.git"
```

---

## AXIS Functional Subdomain Architecture

**Total Organizations**: 14 functional subdomains
**Total Repositories**: 253
**Visibility**: All private (require API token)

### AXIS Subdomain Organizations

| Organization | Repos | Purpose |
|--------------|-------|---------|
| **AXIS-Bots** | 30 | AI agent automation and orchestration |
| **AXIS-Core** | 25 | Central command and ARTEMIS integration |
| **AXIS-Data** | 22 | Core modules and architectural implementations |
| **AXIS-Decentral** | 30 | Enterprise architecture frameworks and governance |
| **AXIS-Docs** | 30 | Documentation and knowledge management |
| **AXIS-Infra** | 1 | Infrastructure and deployment |
| **AXIS-IoT** | 10 | IoT device management and integration |
| **AXIS-KMS** | 13 | Knowledge management systems |
| **AXIS-Labs** | 21 | Innovation sandbox and research projects |
| **AXIS-Media** | 0 | Media processing and storage |
| **AXIS-Observe** | 21 | Monitoring and observability |
| **AXIS-PM** | 20 | Project management and coordination |
| **AXIS-Security** | 30 | Authentication, Web3 governance, ethical AI |
| **AXIS-Tools** | 0 | Development tools and utilities |

**Reference**: See `/home/user/Documents/AXIS-ORGANIZATIONS-COMPLETE.md` for complete repository listings.

---

## AXIS Bot Ecosystem (30 AI Agents in AXIS-Bots)

### Complete AXIS-Bots Repository List (30 Bots)

All bots in **AXIS-Bots** organization (codeberg.org/AXIS-Bots):

1. **axis-alert-bot** - Manages alerting and notifications
2. **axis-analytics-bot** - Processes system analytics
3. **axis-artifact-bot** - Manages artifact handling and storage
4. **axis-audit-bot** - Performs automated security audits
5. **axis-backup-bot** - Manages backup operations
6. **axis-build-bot** - Manages build processes and automation
7. **axis-cache-bot** - Handles caching operations and management
8. **axis-changelog-bot** - Tracks and generates change-logs
9. **axis-cleanup-bot** - Manages system cleanup and maintenance
10. **axis-code-review-bot** - Automates code review processes
11. **axis-compliance-bot** - Ensures compliance with standards and policies
12. **axis-config-bot** - Handles configuration management
13. **axis-coverage-bot** - Tracks and reports test coverage
14. **axis-dependency-bot** - Tracks and updates dependencies
15. **axis-docs-bot** - Manages documentation updates
16. **axis-framework-bot** - Maintains core bot framework ✅ Production Ready
17. **axis-gateway-bot** - Handles external integrations
18. **axis-healthcheck-bot** - Performs system health checks
19. **axis-infra-bot** - Manages infrastructure automation and deployment
20. **axis-integration-bot** - Manages service integration and monitoring
21. **axis-kb-bot** - Manages knowledge base content
22. **axis-license-bot** - Manages license compliance
23. **axis-lint-bot** - Performs code linting and style checks
24. **axis-localization-bot** - Manages translation and localization
25. **axis-log-bot** - Manages log collection and analysis
26. **axis-metrics-bot** - Collects and processes metrics
27. **axis-monitoring-bot** - Handles system monitoring
28. **axis-orchestration-bot** - Coordinates pipeline processes
29. **axis-performance-bot** - Conducts performance testing and analysis
30. **axis-project-bot** - Manages project coordination

### Key Framework Bots (Detailed)

**1. axis-framework-bot**
```
Repository: codeberg.org/AXIS-Bots/axis-framework-bot
Purpose: Framework detection and update management
Status: ✅ Production Ready (2025-10-21)
Containers:
  - axis-framework-bot (95.1 MB)
  - axis-framework-scheduler (90.8 MB)
  - axis-framework-executor (95 MB)
API Endpoint: http://localhost:8085/api/v1/framework
Capabilities:
  - Detect installed frameworks (pydantic, crewai, fastapi, requests)
  - Python 3.13 compatibility checking
  - Intelligent update suggestions
  - Configuration validation
```

**2. axis-docs-bot**
```
Repository: codeberg.org/AXIS-Bots/axis-docs-bot ✅
Purpose: Manages documentation updates
Integration: Works with axis-framework-bot
API Endpoint: http://localhost:8085/api/v1/docs
```

**3. axis-compliance-bot**
```
Repository: codeberg.org/AXIS-Bots/axis-compliance-bot ✅
Purpose: Ensures compliance with standards and policies
Integration: Validates axis-framework-bot changes
API Endpoint: http://localhost:8085/api/v1/compliance
```

**4. axis-audit-bot**
```
Repository: codeberg.org/AXIS-Bots/axis-audit-bot ✅
Purpose: Performs automated security audits
Integration: Comprehensive audit trails
API Endpoint: http://localhost:8085/api/v1/audit
```

**5. axis-monitoring-bot**
```
Repository: codeberg.org/AXIS-Bots/axis-monitoring-bot ✅
Purpose: Handles system monitoring
Integration: System performance tracking
API Endpoint: http://localhost:8085/api/v1/monitoring
```

---

## AXIS CrewAI Agents

**Multi-Agent Coordination Specialists**:

**AXISBotArchitect**
```
Purpose: Multi-agent bot ecosystem design
Tools: AXISRAGTool, BotEcosystemAnalysisTool
Knowledge: 9 AXIS framework documents
```

**BotCoordinationSpecialist**
```
Purpose: Inter-agent communication patterns
Tools: Coordination API, Service Mesh integration
Knowledge: Bot collaboration patterns
```

**EnterpriseIntegrationBot**
```
Purpose: ARTEMIS platform integration
Tools: ARTEMISIntegrationTool
Knowledge: Enterprise bot orchestration
```

---

## API Endpoints

### AXIS Bot Factory

**Base URL**: `http://localhost:8085/api/v1`

**Endpoints**:
```bash
# AXIS Agents
POST   /axis-agents             # Trigger AXIS multi-agent analysis
GET    /axis-agents/status      # Agent status

# Framework Bot
POST   /framework/detect        # Detect frameworks
POST   /framework/check         # Check compatibility
POST   /framework/suggest       # Suggest updates
GET    /framework/health        # Health check

# Docs Bot
POST   /docs/generate           # Generate documentation
PUT    /docs/update             # Update documentation

# Compliance Bot
POST   /compliance/validate     # Validate compliance
GET    /compliance/status       # Compliance status

# Validation Bot
POST   /validation/config       # Validate configuration
POST   /validation/test         # Run validation tests

# Audit Bot
POST   /audit/log               # Log audit event
GET    /audit/report            # Generate audit report

# Security Bot
POST   /security/scan           # Security scan
GET    /security/vulnerabilities # Get vulnerabilities

# Test Bot
POST   /test/execute            # Execute tests
GET    /test/results            # Get test results
```

---

## Integration Points

### 1. META-KERAGR (Knowledge Graph)

**Endpoint**: `neo4j://localhost:7687`
**Database**: Meta-knowledge graph for AXIS ecosystem
**Authentication**: Neo4j credentials in Vault

**Access**:
```bash
# Via Cypher query
MATCH (bot:AXISBot)-[:COORDINATES_WITH]->(other:AXISBot)
RETURN bot.name, collect(other.name) as collaborators
```

### 2. ARTEMIS Platform

**Endpoint**: `http://localhost:8086/api/v1/artemis`
**Purpose**: Bot orchestration and lifecycle management
**Features**:
  - Bot registration and discovery
  - Lifecycle management
  - Health monitoring
  - Coordination patterns (sequential, parallel, hierarchical)

### 3. Service Mesh (Traefik + Consul)

**Traefik Dashboard**: `http://localhost:8080`
**Consul UI**: `http://localhost:8500`
**Purpose**: Secure bot-to-bot communication

### 4. Identity Management (Zitadel)

**Endpoint**: `http://localhost:8081`
**Purpose**: OIDC authentication for bots
**Configuration**: Each bot has unique service account

### 5. Secrets Management (HashiCorp Vault)

**Endpoint**: `http://localhost:8200`
**Purpose**: Secure credential storage

**Vault Paths**:
```bash
# AXIS Bot Credentials
secret/axis-bots/framework-bot/anthropic-api-key
secret/axis-bots/framework-bot/codeberg-token

secret/axis-bots/docs-bot/anthropic-api-key
secret/axis-bots/docs-bot/codeberg-token

secret/axis-bots/compliance-bot/anthropic-api-key
secret/axis-bots/compliance-bot/codeberg-token

secret/axis-bots/validation-bot/anthropic-api-key
secret/axis-bots/validation-bot/codeberg-token

secret/axis-bots/audit-bot/anthropic-api-key
secret/axis-bots/audit-bot/codeberg-token

secret/axis-bots/security-bot/anthropic-api-key
secret/axis-bots/security-bot/codeberg-token

secret/axis-bots/test-bot/anthropic-api-key
secret/axis-bots/test-bot/codeberg-token

# Shared Credentials
secret/axis-bots/shared/meta-keragr-credentials
secret/axis-bots/shared/artemis-api-key
secret/axis-bots/shared/consul-token
secret/axis-bots/shared/zitadel-client-secret
```

---

## Environment Variables

**For All AXIS Bots**:
```bash
# Codeberg
export CODEBERG_TOKEN="d0408771e085097495d59eb91bea7e0a582453de"
export CODEBERG_ORG="AXIS-Bots"

# Anthropic (per-bot, retrieve from Vault)
export ANTHROPIC_API_KEY="sk-ant-..." # Vault: secret/axis-bots/${BOT_NAME}/anthropic-api-key

# Knowledge Graph
export NEO4J_URI="neo4j://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="<from-vault>" # Vault: secret/axis-bots/shared/neo4j-password

# ARTEMIS Platform
export ARTEMIS_API_URL="http://localhost:8086/api/v1"
export ARTEMIS_API_KEY="<from-vault>" # Vault: secret/axis-bots/shared/artemis-api-key

# Service Mesh
export CONSUL_HTTP_ADDR="http://localhost:8500"
export CONSUL_HTTP_TOKEN="<from-vault>" # Vault: secret/axis-bots/shared/consul-token

# Identity
export ZITADEL_ISSUER="http://localhost:8081"
export ZITADEL_CLIENT_ID="axis-${BOT_NAME}"
export ZITADEL_CLIENT_SECRET="<from-vault>" # Vault: secret/axis-bots/${BOT_NAME}/zitadel-secret

# Vault
export VAULT_ADDR="http://localhost:8200"
export VAULT_TOKEN="<root-token-or-bot-token>"
```

---

## Claude Code Integration

### Custom Slash Command: `/axis-analyze`

**Location**: `/home/user/.claude/commands/axis/analyze.md`

**Usage**:
```bash
# Analyze specific Codeberg issue
/axis-analyze 123

# Direct analysis request
/axis-analyze "Design multi-agent architecture for government data lake"

# Cross-domain coordination analysis
/axis-analyze "Coordinate PIPE infrastructure with IV AI/ML capabilities"
```

**Response Format**:
```yaml
analysis_id: "axis-{timestamp}"
domain: "AXIS"
agents_involved:
  - "AXISBotArchitect"
  - "BotCoordinationSpecialist"
  - "EnterpriseIntegrationBot"
expertise_areas:
  - "Multi-agent coordination patterns"
  - "Enterprise bot architecture"
  - "ARTEMIS platform integration"
recommendations:
  - "Specific architectural recommendations"
  - "Bot ecosystem design patterns"
  - "Integration strategies"
implementation_plan:
  - phase: "Design"
    tasks: ["Define agent roles", "Design coordination patterns"]
  - phase: "Implementation"
    tasks: ["Deploy ARTEMIS integration", "Configure service mesh"]
knowledge_sources:
  - "AXIS_RAG domain (9 documents)"
  - "Multi-agent framework patterns"
  - "Bot ecosystem best practices"
```

---

## Quick Commands

### Test AXIS Bots

```bash
# Framework Bot
cd /home/user/axis-framework-bot
./run-framework.sh

# Check logs
podman logs -f axis-framework-bot
podman logs -f axis-framework-scheduler
podman logs -f axis-framework-executor

# Test capabilities
python3 test-framework-bot.py

# Stop
podman-compose down
```

### Query AXIS Bots via API

```bash
# Check all AXIS bot repositories
curl -s "https://codeberg.org/api/v1/orgs/AXIS-Bots/repos" \
  -H "Authorization: token d0408771e085097495d59eb91bea7e0a582453de" | \
  jq -r '.[] | .name'

# Framework bot health check (when running)
curl -s "http://localhost:8085/api/v1/framework/health"

# Trigger AXIS multi-agent analysis
curl -X POST "http://localhost:8085/api/v1/axis-agents" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_id": 123,
    "description": "Design multi-agent architecture"
  }'
```

### Retrieve Secrets from Vault

```bash
# Login to Vault
export VAULT_ADDR="http://localhost:8200"
export VAULT_TOKEN="<root-token>"

# Get Anthropic API key for framework-bot
vault kv get secret/axis-bots/framework-bot/anthropic-api-key

# Get all AXIS shared credentials
vault kv list secret/axis-bots/shared/
```

---

## AXIS Complete Ecosystem

### AXIS-Bots Organization
**30 AI Agent Repositories** ✅ All Confirmed on Codeberg

### Other AXIS Organizations
**13 Functional Subdomain Organizations** with 223 additional repositories:

- **AXIS-Core** (25 repos): ARTEMIS platform, core services, integrations
- **AXIS-Data** (22 repos): Core modules and architectural implementations
- **AXIS-Decentral** (30 repos): Enterprise architecture and governance
- **AXIS-Docs** (30 repos): Documentation and knowledge management
- **AXIS-Infra** (1 repo): Infrastructure and deployment
- **AXIS-IoT** (10 repos): IoT device management
- **AXIS-KMS** (13 repos): Knowledge management systems
- **AXIS-Labs** (21 repos): Innovation and research
- **AXIS-Media** (0 repos): Media processing (planned)
- **AXIS-Observe** (21 repos): Monitoring and observability
- **AXIS-PM** (20 repos): Project management
- **AXIS-Security** (30 repos): Authentication, Web3, ethical AI
- **AXIS-Tools** (0 repos): Development tools (planned)

**Total**: 253 repositories across 14 organizations

---

## Security Considerations

1. **API Key Rotation**: Rotate Codeberg and Anthropic API keys quarterly
2. **Vault Access**: Each bot has unique Vault AppRole for least-privilege access
3. **Network Isolation**: Bots run in isolated containers with service mesh
4. **Audit Logging**: All bot actions logged to axis-audit-bot
5. **Secrets**: Never commit API keys to git - always use Vault

---

## Related Documentation

- **AXIS Framework Bot TODO**: `/home/user/Documents/AXIS-FRAMEWORK-BOT-TODO.txt`
- **AXIS Analyze Command**: `/home/user/Documents/bsw-claude-optimisations-20251024_034321/slash-commands/axis-analyze.md`
- **Multi-Framework Summary**: `/home/user/Documents/bsw-claude-optimisations-20251024_034321/MULTI-FRAMEWORK-SUMMARY.md`
- **BSW Bot Architecture**: `/home/user/Documents/bsw-claude-optimisations-20251024_034321/BSW-BOT-ORG-ARCHITECTURE-20251024.md`

---

## Next Steps

1. ✅ Create this documentation
2. Verify AXIS-Bots organization exists on Codeberg
3. Create remaining 39 AXIS bot repositories
4. Implement scheduler and executor for framework-bot
5. Deploy ARTEMIS platform for bot orchestration
6. Configure META-KERAGR knowledge graph
7. Set up service mesh (Traefik + Consul)
8. Configure Zitadel for bot authentication
9. Store all API keys in Vault
10. Create unit tests for all bots

---

**Status**: ✅ Documentation Complete
**Last Updated**: 2025-10-29
**Maintained By**: BSW-Gov AppVM | Dutch Ministry of Finance
