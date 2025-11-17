# OpenSpec Guide for PIPE

OpenSpec is a spec-driven development methodology that uses Gherkin-style requirements to guide AI-assisted development. This guide explains how to use OpenSpec with PIPE.

## Table of Contents

- [What is OpenSpec?](#what-is-openspec)
- [Project Structure](#project-structure)
- [Workflow](#workflow)
- [Writing Specifications](#writing-specifications)
- [Change Proposals](#change-proposals)
- [AI Assistant Integration](#ai-assistant-integration)
- [Best Practices](#best-practices)

## What is OpenSpec?

OpenSpec provides:

1. **Living Specifications**: Requirements written in executable Gherkin format
2. **Change Proposals**: Structured process for proposing and tracking changes
3. **AI Context**: Comprehensive project context for AI assistants
4. **Test-Driven Development**: Specs drive both implementation and testing

### Why OpenSpec for PIPE?

- **Complex Domain**: 9 domains, governance workflows, compliance tracking
- **AI Integration**: Cognee memory requires clear behavioral specifications
- **Infrastructure**: Multiple integrations (OpenBao, Zitadel, Cilium, etc.)
- **Team Collaboration**: Specs document the "why" behind decisions

## Project Structure

```
openspec/
├── project.md                  # Project context and overview
├── specs/                      # Behavioral specifications
│   ├── bots/spec.md           # Bot system requirements
│   ├── governance/spec.md     # Governance workflows
│   └── integrations/spec.md   # Infrastructure integrations
└── changes/                    # Change proposals
    └── example-add-memify-support/
        ├── proposal.md         # Full proposal document
        └── spec-changes.md     # Exact spec modifications
```

## Workflow

### 1. Understanding Existing Behavior

Before making changes, read the relevant spec:

```bash
# Read bot specifications
cat openspec/specs/bots/spec.md

# Read governance specifications
cat openspec/specs/governance/spec.md

# Read integration specifications
cat openspec/specs/integrations/spec.md
```

### 2. Proposing Changes

When you want to add or modify functionality:

**Step 1: Create proposal directory**
```bash
mkdir -p openspec/changes/your-feature-name/
```

**Step 2: Write proposal.md**
```markdown
# Change Proposal: Your Feature Name

## Metadata
- **Proposal ID**: CHANGE-XXX
- **Status**: Draft
- **Proposed By**: Your Name
- **Date**: YYYY-MM-DD
- **Affects**: openspec/specs/[affected-spec].md

## Summary
Brief description of the change

## Motivation
Why this change is needed

## Current Behavior
How it works now (with spec references)

## Proposed Behavior
How it should work (with new spec scenarios)

## Implementation Plan
Detailed steps

## Testing Plan
How to verify the change

## Risks and Mitigation
Potential issues and solutions
```

**Step 3: Document spec changes**

Create `spec-changes.md` with exact diffs:
```markdown
# Specification Changes: Your Feature Name

## Change 1: Add New Requirement

**Location:** After line X

**Add:**
```gherkin
### Requirement: Feature Name
The system SHALL ...

#### Scenario: Specific behavior
- GIVEN preconditions
- WHEN action occurs
- THEN expected outcomes
```
```

### 3. Review and Approval

1. Share proposal with team
2. Gather feedback
3. Update proposal based on feedback
4. Mark as "Approved" once consensus reached

### 4. Implementation

Once approved:

**Step 1: Update specifications**
```bash
# Apply changes from spec-changes.md
vim openspec/specs/[affected-spec].md
```

**Step 2: Implement the feature**
```bash
# Write code following the spec
vim src/...
```

**Step 3: Write tests**
```bash
# Tests should validate spec scenarios
vim tests/...
```

**Step 4: Verify against spec**
```bash
# Run tests
pytest tests/ -v

# Verify behavior matches spec
```

**Step 5: Commit**
```bash
git add openspec/specs/ src/ tests/
git commit -m "feat: implement [feature] per CHANGE-XXX"
```

### 5. Close Proposal

Update proposal status to "Implemented" and reference commit:
```markdown
## Status: Implemented

- **Implemented In**: commit hash
- **Date**: YYYY-MM-DD
```

## Writing Specifications

### Specification Format

Each spec file should have:

```markdown
# [System Name] Specification

## Purpose
One-sentence purpose statement

## Requirements

### Requirement: [Name]
The system SHALL/SHALL NOT [behavior].

#### Scenario: [Specific case]
- GIVEN [preconditions]
- WHEN [action]
- THEN [expected outcome]
- AND [additional outcome]

## Implementation Notes
- Technical details
- Architectural decisions
- Trade-offs made
```

### Gherkin Keywords

| Keyword | Purpose |
|---------|---------|
| **GIVEN** | Preconditions and context |
| **WHEN** | Action or event |
| **THEN** | Expected outcome |
| **AND** | Additional conditions/outcomes |
| **SHALL** | Mandatory requirement |
| **SHALL NOT** | Mandatory prohibition |
| **SHOULD** | Recommended behavior |

### Writing Good Scenarios

**❌ Bad: Too vague**
```gherkin
#### Scenario: Bot works
- WHEN bot runs
- THEN it should work correctly
```

**✅ Good: Specific and testable**
```gherkin
#### Scenario: Bot heartbeat monitoring
- GIVEN a bot is running
- WHEN 10 seconds elapse without heartbeat
- THEN the bot SHALL be marked as unhealthy
- AND an alert SHALL be triggered
```

**❌ Bad: Implementation details**
```gherkin
#### Scenario: Store in Redis
- WHEN data arrives
- THEN save to Redis with TTL of 300
```

**✅ Good: Behavioral requirement**
```gherkin
#### Scenario: Cache management
- GIVEN data has been processed
- WHEN the data is stored
- THEN it SHALL be cached for future requests
- AND the cache SHALL expire after configured TTL
```

## Change Proposals

### When to Create a Proposal

Create a proposal for:
- ✅ New features
- ✅ Breaking changes
- ✅ Architecture changes
- ✅ New integrations
- ✅ Security changes

No proposal needed for:
- ❌ Bug fixes (unless they change behavior)
- ❌ Documentation updates
- ❌ Code refactoring (without behavior change)
- ❌ Test additions

### Proposal Template

See `openspec/changes/example-add-memify-support/proposal.md` for a complete example.

Key sections:
1. **Metadata**: ID, status, author, date, affected specs
2. **Summary**: 1-2 sentence overview
3. **Motivation**: Why is this needed?
4. **Current Behavior**: How does it work now?
5. **Proposed Behavior**: How should it work?
6. **Implementation Plan**: Step-by-step approach
7. **Testing Plan**: Verification strategy
8. **Risks and Mitigation**: Potential issues
9. **Alternatives Considered**: Other approaches
10. **Success Criteria**: How to measure success

## AI Assistant Integration

### Using OpenSpec with AI

PIPE's OpenSpec structure provides optimal context for AI assistants.

**Before asking AI to make changes:**

1. Share the relevant spec:
```bash
cat openspec/specs/[relevant-spec].md
```

2. Share project context:
```bash
cat openspec/project.md
```

3. Ask AI to review current behavior:
```
"Review the bot lifecycle specification in openspec/specs/bots/spec.md.
I want to add a feature that does X. How does the current spec handle this?"
```

**When implementing a feature:**

```
"Implement the 'Bot heartbeat monitoring' scenario from
openspec/specs/bots/spec.md lines 45-52. Follow the spec exactly."
```

**When proposing changes:**

```
"I want to add Memify support to Cognee integration.
Create a change proposal following the format in
openspec/changes/example-add-memify-support/proposal.md"
```

### AI Workflow

1. **Analyze**: AI reads spec to understand current behavior
2. **Propose**: AI creates change proposal
3. **Review**: Human reviews and approves
4. **Implement**: AI implements following spec
5. **Test**: AI writes tests validating spec scenarios
6. **Verify**: Human verifies behavior matches spec

## Best Practices

### Specification Best Practices

1. **One Concept per Scenario**: Each scenario tests one specific behavior
2. **Testable**: Every scenario should be verifiable
3. **Implementation-Agnostic**: Describe behavior, not implementation
4. **Examples**: Include concrete examples in scenarios
5. **Version Control**: Keep specs in sync with code

### Change Proposal Best Practices

1. **Start Small**: Propose incremental changes
2. **Clear Motivation**: Explain the "why" thoroughly
3. **Document Alternatives**: Show you considered other approaches
4. **Identify Risks**: Be honest about potential issues
5. **Define Success**: Clear, measurable criteria

### Development Best Practices

1. **Spec First**: Update spec before implementing
2. **Test Against Spec**: Tests should validate spec scenarios
3. **Reference Specs**: In code comments, reference spec line numbers
4. **Keep in Sync**: Update spec when behavior changes
5. **Review Specs**: Include specs in code review

### Common Patterns

**Pattern 1: Adding a new integration**

1. Create proposal in `openspec/changes/add-[integration]-support/`
2. Add requirement to `openspec/specs/integrations/spec.md`
3. Implement client in `src/integrations/[integration]_client.py`
4. Add tests in `tests/integrations/test_[integration]_client.py`
5. Add example in `examples/[integration]/`

**Pattern 2: Enhancing governance**

1. Create proposal in `openspec/changes/enhance-governance-[feature]/`
2. Add scenarios to `openspec/specs/governance/spec.md`
3. Update `src/governance/governance_manager.py`
4. Add tests in `tests/governance/`
5. Update `examples/governance/`

**Pattern 3: New bot capability**

1. Create proposal in `openspec/changes/bot-[capability]/`
2. Add scenarios to `openspec/specs/bots/spec.md`
3. Update `src/bots/bot_base.py` or create new bot
4. Add tests in `tests/bots/`
5. Update bot examples

## Examples

### Example 1: Reading a Spec

```bash
# Understand how governance integration requests work
cat openspec/specs/governance/spec.md | grep -A 20 "Integration Request Workflow"
```

Output shows the exact requirements for integration approval workflow.

### Example 2: Proposing a Feature

See `openspec/changes/example-add-memify-support/` for a complete example of proposing Cognee Memify integration.

### Example 3: Implementing from Spec

```python
# From openspec/specs/integrations/spec.md lines 11-15:
# #### Scenario: Kubernetes authentication
# - GIVEN a bot runs in Kubernetes
# - WHEN it needs to access secrets
# - THEN it SHALL authenticate using service account JWT
# - AND receive a time-limited token

async def authenticate_kubernetes(self, jwt_path: str = None) -> bool:
    """
    Authenticate to OpenBao using Kubernetes service account.

    Implements: openspec/specs/integrations/spec.md:11-15
    """
    jwt_path = jwt_path or "/var/run/secrets/kubernetes.io/serviceaccount/token"

    with open(jwt_path, "r") as f:
        jwt = f.read().strip()

    # Authenticate and receive time-limited token
    url = f"{self.address}/v1/auth/kubernetes/login"
    payload = {"role": self.kubernetes_role, "jwt": jwt}

    async with session.post(url, json=payload) as response:
        if response.status == 200:
            data = await response.json()
            self.token = data["auth"]["client_token"]  # Time-limited token
            return True
    return False
```

### Example 4: Testing Against Spec

```python
# Test implements spec scenario
async def test_kubernetes_authentication():
    """
    Test Kubernetes authentication scenario.

    Verifies: openspec/specs/integrations/spec.md:11-15
    """
    client = OpenBaoClient()

    # GIVEN a bot runs in Kubernetes (mock JWT file)
    with patch('builtins.open', mock_open(read_data="test-jwt")):
        # WHEN it needs to access secrets
        result = await client.authenticate_kubernetes()

        # THEN it SHALL authenticate using service account JWT
        assert result is True

        # AND receive a time-limited token
        assert client.token is not None
        assert len(client.token) > 0
```

## Maintenance

### Keeping Specs Current

1. **During Development**: Update spec when behavior changes
2. **During Code Review**: Verify spec and code match
3. **Quarterly Review**: Review all specs for accuracy
4. **After Incidents**: Update specs if assumptions were wrong

### Deprecated Features

When removing features:

1. Mark scenarios as deprecated in spec:
```gherkin
#### Scenario: Old feature (DEPRECATED)
**Deprecated**: Use new feature instead (see line X)
**Removal Date**: YYYY-MM-DD

- GIVEN ...
- WHEN ...
- THEN ...
```

2. Create removal proposal
3. Update code and remove spec section

## Resources

- **OpenSpec Documentation**: See proposal for links
- **Example Proposal**: `openspec/changes/example-add-memify-support/`
- **Project Context**: `openspec/project.md`
- **Current Specs**: `openspec/specs/`

## Getting Help

- **Spec Questions**: Review `openspec/project.md` for context
- **Proposal Help**: Use example proposal as template
- **AI Assistance**: Share relevant spec with AI assistant
- **Team Review**: Create proposal and request feedback

---

**Last Updated**: 2025-01-17
**Applies To**: PIPE v1.0+
**Status**: Active
