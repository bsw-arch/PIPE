# OpenSpec Integration Guide

Complete guide to integrating OpenSpec API specification management into PIPE.

## What is OpenSpec?

OpenSpec is an AI-assisted specification management tool that uses a two-folder model (specs/ and changes/) to track API specifications and manage changes with AI agents. It's perfect for managing PIPE's domain integrations and API contracts.

## Why OpenSpec for PIPE?

- **Governance Alignment**: OpenSpec's review workflow matches PIPE's governance model
- **AI-Assisted**: Works with Claude Code and other AI tools
- **Change Tracking**: Clear audit trail of all API changes
- **Team Collaboration**: Multiple stakeholders can review specs
- **Version Control**: Git-based, integrates with existing workflow

## Installation

### Prerequisites

- Node.js ≥ 20.19.0
- Git repository initialized

### Step 1: Install OpenSpec

```bash
# Install globally
npm install -g @fission-ai/openspec@latest

# Verify installation
openspec --version
```

### Step 2: Initialize in PIPE Repository

```bash
# Navigate to PIPE directory
cd /path/to/PIPE

# Initialize OpenSpec
openspec init
```

During initialization, select the AI tools your team uses (Claude Code, Cursor, etc.).

This creates:
```
PIPE/
├── openspec/
│   ├── specs/          # Source of truth for specifications
│   ├── changes/        # Proposed changes (feature folders)
│   └── AGENTS.md       # AI agent instructions
├── .gitignore          # Updated to include openspec/changes/
└── package.json        # OpenSpec dependencies (optional)
```

## Architecture

```
┌─────────────────────────────────────────────┐
│  PIPE Domain APIs                           │
│  • BNI Authentication API                   │
│  • BNP Business Services API                │
│  • AXIS Compliance API                      │
│  • IV Innovation API                        │
└──────────────┬──────────────────────────────┘
               │
               │ Documented in
               ▼
┌─────────────────────────────────────────────┐
│  openspec/specs/                            │
│  ├── domains/                               │
│  │   ├── bni/                               │
│  │   │   └── authentication-api.yaml        │
│  │   ├── bnp/                               │
│  │   │   └── business-services-api.yaml     │
│  │   ├── axis/                              │
│  │   │   └── compliance-api.yaml            │
│  │   └── iv/                                │
│  │       └── innovation-api.yaml            │
│  ├── integrations/                          │
│  │   ├── bnp-bni-integration.yaml           │
│  │   └── iv-axis-integration.yaml           │
│  └── governance/                            │
│      └── integration-policies.yaml          │
└─────────────────────────────────────────────┘
               │
               │ Changes proposed in
               ▼
┌─────────────────────────────────────────────┐
│  openspec/changes/                          │
│  └── add-user-roles-endpoint/              │
│      ├── proposal.md                        │
│      ├── tasks.md                           │
│      ├── design.md                          │
│      └── spec-delta.yaml                    │
└─────────────────────────────────────────────┘
```

## Setup Workflow

### Step 1: Document Existing APIs

Create initial specifications for PIPE domains:

```bash
# Create directory structure
mkdir -p openspec/specs/domains/{bni,bnp,axis,iv}
mkdir -p openspec/specs/integrations
mkdir -p openspec/specs/governance
```

#### BNI Authentication API

Create `openspec/specs/domains/bni/authentication-api.yaml`:

```yaml
openapi: 3.0.0
info:
  title: BNI Authentication API
  version: 1.0.0
  description: Centralized authentication service for PIPE ecosystem

servers:
  - url: https://api.pipe.internal/bni/v1
    description: BNI authentication server

paths:
  /auth/login:
    post:
      summary: Authenticate user
      description: Authenticates user and returns JWT token
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                password_hash:
                  type: string
                  format: password
                domain:
                  type: string
                  description: Requesting domain (BNP, AXIS, IV)
              required:
                - username
                - password_hash
                - domain
      responses:
        '200':
          description: Authentication successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
                    description: JWT access token
                  expires_in:
                    type: integer
                    description: Token expiration in seconds
                  permissions:
                    type: array
                    items:
                      type: string
                    description: User permissions
        '401':
          description: Authentication failed

  /auth/validate:
    post:
      summary: Validate token
      description: Validates JWT token and returns user info
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                token:
                  type: string
              required:
                - token
      responses:
        '200':
          description: Token is valid
          content:
            application/json:
              schema:
                type: object
                properties:
                  valid:
                    type: boolean
                  username:
                    type: string
                  permissions:
                    type: array
                    items:
                      type: string
        '401':
          description: Token is invalid or expired

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    Error:
      type: object
      properties:
        error:
          type: string
        message:
          type: string
```

#### BNP Business Services API

Create `openspec/specs/domains/bnp/business-services-api.yaml`:

```yaml
openapi: 3.0.0
info:
  title: BNP Business Services API
  version: 1.0.0
  description: Core business services (CRM, Analytics, Invoicing)

servers:
  - url: https://api.pipe.internal/bnp/v1
    description: BNP services server

paths:
  /services/request:
    post:
      summary: Request a business service
      description: Request CRM, analytics, or invoicing service
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                service:
                  type: string
                  enum: [analytics, crm, invoicing]
                request_id:
                  type: string
                parameters:
                  type: object
              required:
                - service
                - request_id
      responses:
        '200':
          description: Service request received
          content:
            application/json:
              schema:
                type: object
                properties:
                  request_id:
                    type: string
                  status:
                    type: string
                    enum: [processing, completed]
                  data:
                    type: object
        '403':
          description: Unauthorized domain

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### Step 2: Configure OpenSpec for PIPE

Create `openspec/config.yaml`:

```yaml
# OpenSpec configuration for PIPE

# Specification sources
spec_sources:
  - path: specs/domains/**/*.yaml
    type: openapi
  - path: specs/integrations/**/*.yaml
    type: openapi
  - path: specs/governance/**/*.yaml
    type: custom

# Change management
change_workflow:
  required_approvers: 2
  auto_archive_on_merge: true
  validation_on_apply: true

# Governance integration
governance:
  enabled: true
  review_pipeline: true
  compliance_check: true

# AI agent configuration
ai_agents:
  - claude-code
  - cursor
  - codebuddy

# Validation rules
validation:
  breaking_changes:
    warn: true
    block: false
  versioning:
    enforce_semver: true
```

### Step 3: Add Slash Commands

OpenSpec automatically configures slash commands when you run `openspec init`. Available commands:

- `/openspec:proposal` - Create a new change proposal
- `/openspec:apply` - Apply an approved change
- `/openspec:archive` - Archive a completed change
- `/openspec:validate` - Validate spec changes
- `/openspec:diff` - Show spec differences

## Usage Workflow

### Creating a Change Proposal

**Scenario**: Add user roles endpoint to BNI API

```bash
# Use AI assistant with slash command
/openspec:proposal "Add user roles management endpoint to BNI authentication API"
```

Or manually:

```bash
# Create change directory
mkdir -p openspec/changes/add-user-roles

# Create proposal
cat > openspec/changes/add-user-roles/proposal.md << 'EOF'
# Add User Roles Management

## Goal
Add endpoints to BNI authentication API for managing user roles.

## Motivation
- Domains need fine-grained permission control
- Current system only supports basic auth
- Need role-based access control (RBAC)

## Proposed Changes
1. Add POST /auth/roles - Create role
2. Add GET /auth/roles - List roles
3. Add PUT /auth/roles/{id} - Update role
4. Add DELETE /auth/roles/{id} - Delete role
5. Add POST /auth/users/{id}/roles - Assign role to user

## Impact
- Breaking change: No
- New endpoints: 5
- Affected domains: All (BNP, AXIS, IV)
EOF

# Create tasks
cat > openspec/changes/add-user-roles/tasks.md << 'EOF'
# Implementation Tasks

- [ ] Update OpenAPI spec with new endpoints
- [ ] Implement role management in BNI bot
- [ ] Add database schema for roles
- [ ] Update authentication logic
- [ ] Add unit tests
- [ ] Update integration examples
- [ ] Document role permissions
- [ ] Update governance policies
- [ ] Request governance approval
EOF

# Create spec delta
cat > openspec/changes/add-user-roles/spec-delta.yaml << 'EOF'
# Changes to openspec/specs/domains/bni/authentication-api.yaml

add:
  paths:
    /auth/roles:
      post:
        summary: Create role
        # ... full spec ...
      get:
        summary: List roles
        # ... full spec ...

    /auth/roles/{id}:
      put:
        summary: Update role
        # ... full spec ...
      delete:
        summary: Delete role
        # ... full spec ...

    /auth/users/{id}/roles:
      post:
        summary: Assign role to user
        # ... full spec ...
EOF
```

### Reviewing Changes

The change proposal goes through PIPE's governance review:

```python
# examples/openspec_governance_review.py

async def review_spec_change():
    """Review OpenSpec change through governance."""
    governance = GovernanceManager()

    # Create integration review for spec change
    review = await governance.request_integration(
        source_domain="BNI",
        target_domain="ALL",  # Affects all domains
        integration_type="api_change",
        purpose="Add user roles management to BNI API",
        metadata={
            "openspec_change": "add-user-roles",
            "breaking_change": False,
            "new_endpoints": 5
        }
    )

    # Assign reviewers
    governance.review_pipeline.assign_reviewers(
        review["review_id"],
        ["architect@pipe.com", "security@pipe.com"]
    )

    # Reviewers approve
    governance.review_pipeline.approve_review(
        review["review_id"],
        "architect@pipe.com"
    )

    governance.review_pipeline.approve_review(
        review["review_id"],
        "security@pipe.com"
    )

    # Final approval
    await governance.approve_integration(
        review["integration_id"],
        reviewer="admin@pipe.com",
        notes="User roles spec approved"
    )

    print("✓ Spec change approved - ready to apply")
```

### Applying Changes

Once approved:

```bash
# Apply the change
/openspec:apply add-user-roles

# Or manually
cd openspec/changes/add-user-roles
# Merge spec-delta.yaml into specs/domains/bni/authentication-api.yaml
```

### Archiving Changes

After implementation is complete:

```bash
# Archive the change
/openspec:archive add-user-roles

# This moves the change folder to openspec/archive/
```

## Integration with PIPE Governance

Create `src/governance/openspec_validator.py`:

```python
"""Validates OpenSpec changes against PIPE governance policies."""

import yaml
from pathlib import Path
from typing import Dict, List, Any


class OpenSpecValidator:
    """Validates OpenSpec changes for governance compliance."""

    def __init__(self, openspec_dir: Path = Path("openspec")):
        self.openspec_dir = openspec_dir
        self.specs_dir = openspec_dir / "specs"
        self.changes_dir = openspec_dir / "changes"

    def validate_change(self, change_name: str) -> Dict[str, Any]:
        """
        Validate a proposed spec change.

        Returns:
            Validation result with issues and recommendations
        """
        change_dir = self.changes_dir / change_name

        if not change_dir.exists():
            return {
                "valid": False,
                "errors": [f"Change directory not found: {change_name}"]
            }

        issues = []
        warnings = []

        # Check required files
        required_files = ["proposal.md", "tasks.md", "spec-delta.yaml"]
        for filename in required_files:
            if not (change_dir / filename).exists():
                issues.append(f"Missing required file: {filename}")

        # Validate spec delta
        spec_delta_file = change_dir / "spec-delta.yaml"
        if spec_delta_file.exists():
            with open(spec_delta_file) as f:
                spec_delta = yaml.safe_load(f)

            # Check for breaking changes
            if self._has_breaking_changes(spec_delta):
                warnings.append(
                    "Breaking changes detected - requires special approval"
                )

            # Check versioning
            if not self._has_version_bump(spec_delta):
                warnings.append(
                    "API version should be bumped for changes"
                )

        return {
            "valid": len(issues) == 0,
            "errors": issues,
            "warnings": warnings,
            "requires_governance_approval": True
        }

    def _has_breaking_changes(self, spec_delta: Dict) -> bool:
        """Check if spec delta contains breaking changes."""
        # Deleting paths/endpoints is breaking
        if "delete" in spec_delta and "paths" in spec_delta["delete"]:
            return True

        # Removing required fields is breaking
        if "modify" in spec_delta:
            for path in spec_delta.get("modify", {}).values():
                if "required" in str(path):
                    return True

        return False

    def _has_version_bump(self, spec_delta: Dict) -> bool:
        """Check if version was bumped."""
        if "modify" in spec_delta and "info" in spec_delta["modify"]:
            return "version" in spec_delta["modify"]["info"]
        if "add" in spec_delta and "info" in spec_delta["add"]:
            return "version" in spec_delta["add"]["info"]
        return False

    def list_pending_changes(self) -> List[str]:
        """List all pending changes."""
        if not self.changes_dir.exists():
            return []

        return [
            d.name
            for d in self.changes_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
```

## Best Practices

### 1. Spec Organization
```
openspec/specs/
├── domains/          # One folder per domain
│   ├── bni/
│   ├── bnp/
│   ├── axis/
│   └── iv/
├── integrations/     # Cross-domain integration specs
└── governance/       # Governance policies as specs
```

### 2. Change Naming
- Use kebab-case: `add-user-roles`
- Be descriptive: `fix-auth-timeout-issue`
- Include ticket: `PIPE-123-add-analytics`

### 3. Proposal Format
```markdown
# Title

## Goal
Clear statement of what's changing

## Motivation
Why is this change needed?

## Proposed Changes
Bulleted list of specific changes

## Impact
- Breaking changes: Yes/No
- Affected domains: List
- Migration required: Yes/No
```

### 4. Always Validate
```bash
# Before applying
openspec validate add-user-roles

# Check for breaking changes
openspec diff add-user-roles
```

## Troubleshooting

### "Change not found"
```bash
# List all changes
ls openspec/changes/

# Ensure change directory exists
cd openspec/changes/your-change
```

### "Validation failed"
```bash
# Check what's missing
openspec validate your-change

# Ensure all required files present
ls openspec/changes/your-change/
# Should show: proposal.md, tasks.md, spec-delta.yaml
```

### "Merge conflict"
```bash
# Manually resolve in spec-delta.yaml
# Then re-validate
openspec validate your-change
```

## Next Steps

- [Cognee Integration](./COGNEE_INTEGRATION.md)
- [MCP Integration](./MCP_INTEGRATION.md)
- [Return to Architecture Overview](./AI_INTEGRATION_ARCHITECTURE.md)
