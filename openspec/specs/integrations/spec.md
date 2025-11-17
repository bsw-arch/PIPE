# Infrastructure Integrations Specification

## Purpose
Define integration requirements for PIPE's open-source infrastructure stack.

## Requirements

### Requirement: OpenBao Secrets Management
The system SHALL use OpenBao for all secrets management.

#### Scenario: Kubernetes authentication
- GIVEN a bot runs in Kubernetes
- WHEN it needs to access secrets
- THEN it SHALL authenticate using service account JWT
- AND receive a time-limited token

#### Scenario: Secret retrieval
- GIVEN a bot needs a secret
- WHEN read_secret() is called
- THEN it SHALL retrieve the secret from OpenBao
- AND the secret SHALL be returned decrypted

#### Scenario: Dynamic certificate generation
- GIVEN a service needs TLS certificates
- WHEN generate_certificate() is called
- THEN OpenBao SHALL issue a certificate via PKI
- AND the certificate SHALL have configurable TTL

### Requirement: Zitadel Identity Management
The system SHALL use Zitadel for authentication and authorization.

#### Scenario: Service account authentication
- GIVEN a bot needs to authenticate
- WHEN get_access_token() is called
- THEN it SHALL receive an OAuth 2.0 token
- AND the token SHALL be valid for configured duration

#### Scenario: Token verification
- GIVEN a user or service token
- WHEN verify_token() is called
- THEN it SHALL validate the token with Zitadel
- AND return token claims if valid

#### Scenario: Permission checking
- GIVEN a user and required permission
- WHEN check_permission() is called
- THEN it SHALL verify the user has the permission
- AND return true if authorized

### Requirement: Cognee AI Memory
The system SHALL use Cognee for governance intelligence.

#### Scenario: Governance data ingestion
- GIVEN new governance data (domains, integrations, reviews)
- WHEN add_datapoints() is called
- THEN DataPoints SHALL be added to Cognee
- AND prepared for cognification

#### Scenario: Knowledge graph building
- GIVEN DataPoints have been added
- WHEN cognify_governance_data() is called
- THEN Cognee SHALL:
  - Extract entities and relationships
  - Generate embeddings
  - Build knowledge graph
  - Store in vector and graph stores

#### Scenario: Semantic search
- GIVEN a natural language query
- WHEN search_integrations() is called
- THEN Cognee SHALL:
  - Perform vector similarity search
  - Traverse graph relationships
  - Return contextually relevant results

#### Scenario: Pattern learning
- GIVEN historical integration decisions
- WHEN suggest_integration_path() is called
- THEN Cognee SHALL:
  - Find similar past integrations
  - Analyze success patterns
  - Suggest optimal approach
  - Return confidence score

### Requirement: PR-QUEST Interactive PR Review
The system SHALL use PR-QUEST for automated code review of integration PRs.

#### Scenario: PR analysis request
- GIVEN a valid GitHub PR URL
- WHEN requesting analysis
- THEN the system SHALL:
  - POST to PR-QUEST /api/analyze endpoint
  - Include PR URL and configuration
  - Receive analysis ID
  - Poll for results until complete

#### Scenario: LLM-powered clustering
- GIVEN PR-QUEST is analyzing a PR
- WHEN using LLM mode
- THEN PR-QUEST SHALL:
  - Fetch PR diff from GitHub
  - Parse unified diff format
  - Use LLM (GPT-4o-mini or configured model) to cluster related changes
  - Group by logical functionality
  - Return clustered changes with descriptions

#### Scenario: Risk detection
- GIVEN PR-QUEST completed clustering
- WHEN analyzing for risks
- THEN PR-QUEST SHALL:
  - Apply heuristic rules for common issues
  - Use LLM to identify security vulnerabilities
  - Detect breaking changes
  - Find integration anti-patterns
  - Return risk level (NONE, LOW, MODERATE, CRITICAL)

#### Scenario: Suggestion generation
- GIVEN risks detected in PR
- WHEN generating suggestions
- THEN PR-QUEST SHALL:
  - Use LLM to provide actionable fixes
  - Include code examples where applicable
  - Prioritize by impact
  - Link to relevant documentation

#### Scenario: Review step rendering
- GIVEN PR analysis completed
- WHEN human reviewer requests steps
- THEN PR-QUEST SHALL:
  - Return interactive review steps
  - Show diff sections with react-diff-view
  - Allow per-step notes
  - Track review progress

#### Scenario: Markdown export
- GIVEN completed PR review (automated or human)
- WHEN requesting export
- THEN PR-QUEST SHALL:
  - Generate markdown document
  - Include all clusters and analysis
  - Add reviewer notes
  - Format for governance records

#### Scenario: XP gamification
- GIVEN a reviewer completes thorough review
- WHEN awarding XP
- THEN PR-QUEST SHALL:
  - Calculate XP based on:
    - PR complexity (lines changed)
    - Review thoroughness (notes added)
    - Time to complete
  - Award XP to reviewer
  - Update leaderboard
  - Trigger achievements if applicable

#### Scenario: Result caching
- GIVEN a PR was analyzed previously
- AND PR content hasn't changed
- WHEN requesting re-analysis
- THEN PR-QUEST SHALL:
  - Check cache by PR SHA
  - Return cached results if valid
  - Skip LLM processing
  - Save API costs and time

### Requirement: PR-QUEST Deployment
PR-QUEST SHALL be deployed as a service in the PIPE infrastructure.

#### Scenario: Kubernetes deployment
- GIVEN Kubernetes cluster is available
- WHEN deploying PR-QUEST
- THEN the system SHALL:
  - Create pr-quest-service in pipe-system namespace
  - Expose on port 3000
  - Mount OPENAI_API_KEY from OpenBao
  - Set resource limits (1Gi memory, 500m CPU)
  - Configure health checks

#### Scenario: Service discovery
- GIVEN PR-QUEST service deployed
- WHEN PR Review Bot needs to connect
- THEN it SHALL:
  - Resolve pr-quest-service.pipe-system.svc.cluster.local
  - Connect over cluster network
  - Use Cilium network policies for security

#### Scenario: Fallback mode
- GIVEN PR-QUEST service is unavailable
- WHEN PR Review Bot attempts analysis
- THEN it SHALL:
  - Log service unavailable error
  - Fall back to basic diff parsing (no LLM)
  - Queue PR for retry
  - Notify administrators
  - Continue with degraded functionality

### Requirement: Zot Container Registry
The system SHALL use Zot for container image storage.

#### Scenario: Image storage
- GIVEN a built container image
- WHEN the image is pushed to registry
- THEN it SHALL be stored in Zot
- AND be available for signature verification

### Requirement: Cosign Image Signing
The system SHALL enforce image signature verification.

#### Scenario: Image signing
- GIVEN a container image
- WHEN the image is built
- THEN it SHALL be signed with Cosign
- AND the signature SHALL be verifiable

#### Scenario: Signature verification
- GIVEN a signed container image
- WHEN Kubernetes attempts to deploy it
- THEN the signature SHALL be verified
- AND deployment SHALL fail if signature is invalid

### Requirement: Cilium Network Security
The system SHALL use Cilium for zero-trust networking.

#### Scenario: Domain isolation
- GIVEN two domains want to communicate
- WHEN direct connection is attempted
- THEN Cilium SHALL block the traffic
- AND only allow hub-and-spoke through PIPE

#### Scenario: L7 policy enforcement
- GIVEN HTTP traffic between services
- WHEN Cilium inspects the traffic
- THEN it SHALL enforce HTTP-level policies
- AND block unauthorized endpoints

## Forbidden Technologies

The system SHALL NOT use these technologies:

### HashiCorp Vault
- ❌ MUST NOT be used for secrets management
- ✅ Use OpenBao instead

### HashiCorp Consul
- ❌ MUST NOT be used for service discovery
- ✅ Use Kubernetes native DNS instead

### HashiCorp Terraform
- ❌ MUST NOT be used for infrastructure as code
- ✅ Use OpenTofu instead

### Docker Desktop
- ❌ MUST NOT be used for container runtime
- ✅ Use Podman/Buildah instead
- Reason: Proprietary licensing (costs for companies >250 employees)

### Elastic Stack
- ❌ MUST NOT be used for log aggregation
- ✅ Use Loki instead
- Reason: Lighter weight, truly open-source (Apache 2.0 vs SSPL)

## Implementation Notes

- All integration clients are in `src/integrations/`
- Clients provide async Python interfaces
- Fallback implementations for when dependencies unavailable
- Comprehensive error handling and logging
- Singleton pattern for client instances
