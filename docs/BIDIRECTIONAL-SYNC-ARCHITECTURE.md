# Bidirectional Sync Architecture
## GitHub (SHA-1) ↔ Codeberg (SHA-256) Documentation Sync

**Date:** 2025-11-12
**Purpose:** Automated bidirectional synchronization between GitHub and Codeberg repositories
**Total Bots:** 185 across 8 domains

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    BIDIRECTIONAL SYNC SYSTEM                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐                    ┌──────────────────────┐
│   GitHub (SHA-1)     │                    │  Codeberg (SHA-256)  │
│  bsw-arch/bsw-arch   │◄──────────────────►│  ECO-Bots/*          │
│                      │    Conversion      │  AXIS-Bots/*         │
│  - Central docs      │    & Sync          │  IV-Bots/*           │
│  - Architecture      │                    │  PIPE-Bots/*         │
│  - 40-char commits   │                    │  - Individual bots   │
└──────────────────────┘                    │  - 64-char commits   │
                                            └──────────────────────┘
           │                                          │
           │                                          │
           ▼                                          ▼
  ┌────────────────┐                      ┌────────────────────┐
  │ SHA-1 Commits  │                      │  SHA-256 Commits   │
  │ (40 chars)     │                      │  (64 chars)        │
  └────────────────┘                      └────────────────────┘
           │                                          │
           │         ┌────────────────────┐          │
           └────────►│  Sync Controller   │◄─────────┘
                     │                    │
                     │ - Hash mapping     │
                     │ - Issue tracking   │
                     │ - Status monitoring│
                     └────────────────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Codeberg Issues    │
                     │ - Track per bot    │
                     │ - Link commits     │
                     │ - Automation labels│
                     └────────────────────┘
```

---

## Sync Directions

### Direction 1: GitHub → Codeberg (SHA-1 → SHA-256)

**Source:** https://github.com/bsw-arch/bsw-arch (SHA-1)
**Target:** 185 Codeberg bot repositories (SHA-256)

**Process:**
1. Clone GitHub repo (SHA-1 format)
2. Extract documentation for specific domain/bot
3. Clone Codeberg bot repo (SHA-256 format)
4. Apply documentation to bot wiki
5. Commit with SHA-256
6. Push to Codeberg
7. Create/update Codeberg issue with sync status

### Direction 2: Codeberg → GitHub (SHA-256 → SHA-1)

**Source:** 185 Codeberg bot repositories (SHA-256)
**Target:** https://github.com/bsw-arch/bsw-arch (SHA-1)

**Process:**
1. Clone Codeberg bot repo (SHA-256 format)
2. Extract bot-specific updates/improvements
3. Clone GitHub central repo (SHA-1 format)
4. Integrate bot updates into central docs
5. Commit with SHA-1
6. Push to GitHub
7. Update Codeberg issue with reverse sync status

---

## Hash Conversion Strategy

### Git Object Format Configuration

**GitHub (SHA-1):**
```bash
git config extensions.objectFormat sha1  # Default, no config needed
```

**Codeberg (SHA-256):**
```bash
git config extensions.objectFormat sha256  # Already configured
```

### Conversion Process

**No direct conversion needed!** Each repository maintains its own hash format:

1. **Separate working directories:**
   - `/tmp/sync/github/` - SHA-1 repos
   - `/tmp/sync/codeberg/` - SHA-256 repos

2. **Content-based sync:**
   - Sync by file content, not by commit hash
   - Track sync state by timestamp + content hash
   - Map relationships via issue tracking

3. **Commit metadata:**
   - Reference opposite platform in commit messages
   - Link GitHub commits in Codeberg issues
   - Link Codeberg issues in GitHub commits

---

## Issue Tracking System

### Codeberg Issue Structure

Each bot gets a tracking issue on its Codeberg repo:

**Title:** `[SYNC] Bidirectional documentation sync with GitHub`

**Labels:**
- `sync` - Automation sync task
- `documentation` - Documentation related
- `github-integration` - GitHub sync
- `automation` - Automated process

**Issue Body Template:**
```markdown
# Bidirectional Documentation Sync

**Bot:** {bot_name}
**Domain:** {domain}
**Status:** 🔄 Active

## Sync Configuration

- **GitHub Source:** https://github.com/bsw-arch/bsw-arch
- **Codeberg Target:** https://codeberg.org/{domain}-Bots/{bot_name}
- **Sync Frequency:** On-demand / Automated
- **Git Format:** GitHub (SHA-1) ↔ Codeberg (SHA-256)

## Sync Directions

### ✅ GitHub → Codeberg (Documentation Integration)

**Status:** Pending
**Last Sync:** Never
**Files Synced:** 0

Documentation to sync:
- [ ] Global architecture docs
- [ ] Domain-specific guides ({domain})
- [ ] Augmentic AI framework
- [ ] CAG+RAG implementation
- [ ] Knowledge base guides

### ⏸️ Codeberg → GitHub (Updates/Improvements)

**Status:** Not started
**Last Sync:** Never
**Files Synced:** 0

Bot improvements to sync back:
- [ ] Bot-specific documentation updates
- [ ] Wiki improvements
- [ ] Architecture refinements

## Sync History

| Date | Direction | Commit | Files | Status |
|------|-----------|--------|-------|--------|
| - | - | - | - | - |

## Automation

This issue is managed by the bidirectional sync automation system.

**Scripts:**
- `sync-github-to-codeberg.sh` - Push docs from GitHub
- `sync-codeberg-to-github.sh` - Pull updates to GitHub

**Last Updated:** {timestamp}
```

---

## Sync Controller Implementation

### Master Sync Script

**Location:** `/home/user/github/bsw-arch/bidirectional-sync.sh`

**Capabilities:**
1. Detect changes in either direction
2. Convert between SHA-1 and SHA-256 working directories
3. Create/update Codeberg issues
4. Track sync state
5. Handle conflicts
6. Report status

### Sync State Database

**Location:** `/tmp/sync-state.json`

```json
{
  "bots": {
    "ECO-Bots/eco-infra-bot": {
      "codeberg_repo": "git@codeberg.org:ECO-Bots/eco-infra-bot.git",
      "github_source": "https://github.com/bsw-arch/bsw-arch",
      "issue_number": 1,
      "last_sync_github_to_codeberg": "2025-11-12T12:00:00Z",
      "last_sync_codeberg_to_github": null,
      "github_last_commit": "abc123...",
      "codeberg_last_commit": "def456...",
      "status": "synced",
      "files_synced": 13
    }
  }
}
```

---

## Workflow Execution

### Initial Setup (All 185 Bots)

1. **Create Codeberg API token**
2. **Generate sync tracking issues** on all bot repos
3. **Initial GitHub → Codeberg sync**
   - Push architecture documentation
   - Update wikis
   - Link commits to issues
4. **Establish sync schedule**
   - Manual trigger initially
   - Automated later (GitHub Actions + Woodpecker CI)

### Ongoing Sync

#### When GitHub docs are updated:
```bash
./bidirectional-sync.sh github-to-codeberg --domain ECO --bot eco-infra-bot
```
- Detects changes in GitHub
- Syncs to Codeberg bot wiki
- Updates issue with new commit references
- Status: ✅ Synced

#### When bot wiki is improved:
```bash
./bidirectional-sync.sh codeberg-to-github --domain ECO --bot eco-infra-bot
```
- Detects wiki changes on Codeberg
- Extracts improvements
- Integrates into GitHub central repo
- Updates issue with reverse sync status
- Status: ✅ Reverse synced

---

## Conflict Resolution

### Conflict Types

1. **Same file modified in both places**
   - Manual review required
   - Create conflict issue
   - Human decision on merge strategy

2. **Structural changes**
   - Wiki reorganization on Codeberg
   - Directory changes on GitHub
   - Semi-automatic mapping

3. **Deletion conflicts**
   - File deleted in one place, modified in other
   - Preserve by default, flag for review

---

## API Integration

### Codeberg API (Forgejo)

**Base URL:** `https://codeberg.org/api/v1`

**Endpoints Used:**
- `POST /repos/{owner}/{repo}/issues` - Create tracking issue
- `PATCH /repos/{owner}/{repo}/issues/{index}` - Update issue
- `POST /repos/{owner}/{repo}/issues/{index}/comments` - Add sync log
- `GET /repos/{owner}/{repo}/commits` - Check for updates

**Authentication:**
```bash
curl -H "Authorization: token ${CODEBERG_TOKEN}" \
  https://codeberg.org/api/v1/repos/ECO-Bots/eco-infra-bot/issues
```

### GitHub API

**Base URL:** `https://api.github.com`

**Endpoints Used:**
- `GET /repos/bsw-arch/bsw-arch/commits` - Check for updates
- `GET /repos/bsw-arch/bsw-arch/contents/{path}` - Fetch file content

---

## Benefits

1. **Centralized Documentation** (GitHub)
   - Single source of truth for architecture
   - Easy to maintain globally
   - SHA-1 compatibility with existing tools

2. **Distributed Knowledge** (Codeberg)
   - Bot-specific context in each repo
   - SHA-256 security benefits
   - Native Codeberg wiki features

3. **Bidirectional Flow**
   - Best practices flow down (GitHub → Codeberg)
   - Bot improvements flow up (Codeberg → GitHub)
   - Continuous improvement loop

4. **Progress Tracking**
   - Codeberg issues show sync status
   - Clear history of changes
   - Automated status updates

5. **Hash Format Transparency**
   - No conversion overhead
   - Native git handling
   - Content-based sync

---

## Implementation Phases

### Phase 1: Foundation (Day 1)
- ✅ SSH keys configured
- ✅ Test repos cloned
- ✅ Sync scripts created
- ⏳ Codeberg API integration
- ⏳ Issue template creation

### Phase 2: Pilot (Day 1-2)
- Test with 5 bots (1 per major domain)
- Create tracking issues
- Execute GitHub → Codeberg sync
- Validate wiki integration
- Refine automation

### Phase 3: Rollout (Day 2-3)
- Parallel execution per domain
- ECO: 48 bots
- AXIS: 45 bots
- IV: 44 bots
- PIPE: 48 bots
- BU, BNI, BNP, DC: ~136 bots

### Phase 4: Reverse Sync (Day 3+)
- Implement Codeberg → GitHub flow
- Test with improved bot wikis
- Integrate improvements into central repo
- Establish bidirectional workflow

### Phase 5: Automation (Week 2+)
- GitHub Actions for GitHub side
- Woodpecker CI for Codeberg side
- Webhook-triggered syncs
- Scheduled consistency checks

---

## Technical Requirements

### Tools
- Git with SHA-1 and SHA-256 support ✅
- Codeberg SSH access ✅
- GitHub SSH access ✅
- Codeberg API token ⏳
- jq for JSON processing
- curl for API calls

### Storage
- `/tmp/sync/github/` - GitHub SHA-1 repos
- `/tmp/sync/codeberg/` - Codeberg SHA-256 repos
- `/tmp/sync-state.json` - Sync state tracking

### Network
- Access to github.com ✅
- Access to codeberg.org ✅
- API rate limits respected

---

**Status:** Architecture Complete - Ready for Implementation
**Next:** Create Codeberg API token and implement sync controller
