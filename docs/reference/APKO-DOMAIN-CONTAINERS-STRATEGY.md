# Apko Domain Containers Strategy

**Date**: 2025-10-29
**Purpose**: Minimal, secure apko containers for PIPE, IV, ECO, AXIS domains
**Goal**: Single persistent container per domain with all repos and tooling

---

## Executive Summary

Create **4 ultra-minimal apko containers** for domain-based repository management:

1. **PIPE** - DevOps pipelines and infrastructure
2. **IV** (IntelliVerse) - AI/ML research and memory
3. **ECO** (ECOX) - Value streams and sustainability
4. **AXIS** - Enterprise architecture (14 organizations, 253 repos)

**Benefits**:
- ✅ **Minimal size**: <50MB per container using Chainguard Wolfi
- ✅ **Persistent**: All repos and state preserved across reboots
- ✅ **Secure**: Distroless, minimal attack surface
- ✅ **Fast**: Quick startup, instant access to all repos
- ✅ **Isolated**: Each domain in separate container

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│               Qubes OS bsw-gov AppVM                      │
└──────────────────────┬───────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │      Podman Container        │
        │      Management              │
        └──┬──────┬──────┬──────┬─────┘
           │      │      │      │
    ┌──────▼──┐ ┌▼─────┐ ┌▼────┐ ┌▼────────┐
    │  PIPE   │ │  IV  │ │ ECO │ │  AXIS   │
    │Container│ │Cont. │ │Cont.│ │Container│
    │ (~40MB) │ │(~45MB│ │~40MB│ │ (~50MB) │
    └────┬────┘ └──┬───┘ └──┬──┘ └────┬────┘
         │         │        │         │
    ┌────▼─────────▼────────▼─────────▼────┐
    │  Persistent Volume: /rw/containers/   │
    │  ├── pipe/repos/ (all PIPE repos)    │
    │  ├── iv/repos/   (all IV repos)      │
    │  ├── eco/repos/  (all ECO repos)     │
    │  └── axis/repos/ (253 AXIS repos)    │
    └──────────────────────────────────────┘
```

---

## Domain Organization Structure

### AXIS Domain (Primary - 14 Organizations)

**Organizations**:
1. AXIS-Bots (30 repos)
2. AXIS-Core (25 repos)
3. AXIS-Data (22 repos)
4. AXIS-Decentral (30 repos)
5. AXIS-Docs (30 repos)
6. AXIS-Infra (1 repo)
7. AXIS-IoT (10 repos)
8. AXIS-KMS (13 repos)
9. AXIS-Labs (21 repos)
10. AXIS-Media (0 repos)
11. AXIS-Observe (21 repos)
12. AXIS-PM (20 repos)
13. AXIS-Security (30 repos)
14. AXIS-Tools (0 repos)

**Total**: 253 repositories

### PIPE Domain

**Codeberg Organization**: `codeberg.org/PIPE`
**Purpose**: DevOps pipelines, infrastructure, CI/CD
**Expected Repos**: 30-50 (infrastructure automation, Woodpecker, ArgoCD, container management)

### IV Domain (IntelliVerse)

**Codeberg Organization**: `codeberg.org/IntelliVerse` or `codeberg.org/IV`
**Purpose**: AI/ML research, memory systems, intelligent agents
**Expected Repos**: 20-40 (AI models, ML pipelines, knowledge graphs, memory systems)

### ECO Domain (ECOX)

**Codeberg Organization**: `codeberg.org/ECOX` or `codeberg.org/ECO`
**Purpose**: Value streams, sustainability, circular economy
**Expected Repos**: 15-30 (ESG metrics, carbon tracking, circular economy models)

---

## Apko Container Configurations

### 1. AXIS Domain Container

**File**: `/home/user/containers/apko/axis-domain.yaml`

```yaml
contents:
  repositories:
    - https://packages.wolfi.dev/os
  keyring:
    - https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
  packages:
    # Core system
    - wolfi-baselayout
    - ca-certificates-bundle

    # Git and version control (minimal)
    - git
    - git-lfs

    # Essential tools
    - bash
    - curl
    - jq
    - openssh-client

    # Python (for automation scripts)
    - python-3.13
    - py3.13-pip
    - py3.13-requests

    # Text processing
    - grep
    - sed
    - findutils
    - coreutils

accounts:
  groups:
    - groupname: axis
      gid: 1000
  users:
    - username: axis
      uid: 1000
      gid: 1000
      shell: /bin/bash
  run-as: axis

paths:
  - path: /home/axis
    type: directory
    uid: 1000
    gid: 1000
    permissions: 0o755
  - path: /repos
    type: directory
    uid: 1000
    gid: 1000
    permissions: 0o755
  - path: /scripts
    type: directory
    uid: 1000
    gid: 1000
    permissions: 0o755

entrypoint:
  command: /bin/bash

environment:
  DOMAIN: axis
  CODEBERG_TOKEN: d0408771e085097495d59eb91bea7e0a582453de

archs:
  - x86_64
```

### 2. PIPE Domain Container

**File**: `/home/user/containers/apko/pipe-domain.yaml`

```yaml
contents:
  repositories:
    - https://packages.wolfi.dev/os
  keyring:
    - https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
  packages:
    - wolfi-baselayout
    - ca-certificates-bundle
    - git
    - bash
    - curl
    - jq
    - openssh-client
    - python-3.13
    - py3.13-pip

    # DevOps specific tools
    - docker-cli  # If available in Wolfi
    - kubectl     # If available
    - helm        # If available

accounts:
  groups:
    - groupname: pipe
      gid: 1001
  users:
    - username: pipe
      uid: 1001
      gid: 1001
      shell: /bin/bash
  run-as: pipe

paths:
  - path: /home/pipe
    type: directory
    uid: 1001
    gid: 1001
    permissions: 0o755
  - path: /repos
    type: directory
    uid: 1001
    gid: 1001
    permissions: 0o755

entrypoint:
  command: /bin/bash

environment:
  DOMAIN: pipe
  CODEBERG_TOKEN: d0408771e085097495d59eb91bea7e0a582453de

archs:
  - x86_64
```

### 3. IV Domain Container

**File**: `/home/user/containers/apko/iv-domain.yaml`

```yaml
contents:
  repositories:
    - https://packages.wolfi.dev/os
  keyring:
    - https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
  packages:
    - wolfi-baselayout
    - ca-certificates-bundle
    - git
    - bash
    - curl
    - jq
    - openssh-client
    - python-3.13
    - py3.13-pip
    - py3.13-numpy
    - py3.13-pandas

    # AI/ML tools (if available)
    - py3.13-scikit-learn

accounts:
  groups:
    - groupname: iv
      gid: 1002
  users:
    - username: iv
      uid: 1002
      gid: 1002
      shell: /bin/bash
  run-as: iv

paths:
  - path: /home/iv
    type: directory
    uid: 1002
    gid: 1002
    permissions: 0o755
  - path: /repos
    type: directory
    uid: 1002
    gid: 1002
    permissions: 0o755

entrypoint:
  command: /bin/bash

environment:
  DOMAIN: iv
  CODEBERG_TOKEN: d0408771e085097495d59eb91bea7e0a582453de

archs:
  - x86_64
```

### 4. ECO Domain Container

**File**: `/home/user/containers/apko/eco-domain.yaml`

```yaml
contents:
  repositories:
    - https://packages.wolfi.dev/os
  keyring:
    - https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
  packages:
    - wolfi-baselayout
    - ca-certificates-bundle
    - git
    - bash
    - curl
    - jq
    - openssh-client
    - python-3.13
    - py3.13-pip

accounts:
  groups:
    - groupname: eco
      gid: 1003
  users:
    - username: eco
      uid: 1003
      gid: 1003
      shell: /bin/bash
  run-as: eco

paths:
  - path: /home/eco
    type: directory
    uid: 1003
    gid: 1003
    permissions: 0o755
  - path: /repos
    type: directory
    uid: 1003
    gid: 1003
    permissions: 0o755

entrypoint:
  command: /bin/bash

environment:
  DOMAIN: eco
  CODEBERG_TOKEN: d0408771e085097495d59eb91bea7e0a582453de

archs:
  - x86_64
```

---

## Build Scripts

### Master Build Script

**File**: `/home/user/containers/build-all-domains.sh`

```bash
#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APKO_DIR="${SCRIPT_DIR}/apko"
OUTPUT_DIR="${SCRIPT_DIR}/images"

mkdir -p "${OUTPUT_DIR}"

echo "═══════════════════════════════════════════════════"
echo "  Building All Domain Containers with apko"
echo "═══════════════════════════════════════════════════"
echo ""

# Check if apko is installed
if ! command -v apko &> /dev/null; then
    echo "❌ apko not found. Installing..."
    # Install apko
    wget https://github.com/chainguard-dev/apko/releases/latest/download/apko_$(uname -s)_$(uname -m) -O /tmp/apko
    chmod +x /tmp/apko
    sudo mv /tmp/apko /usr/local/bin/apko
fi

DOMAINS=("axis" "pipe" "iv" "eco")

for domain in "${DOMAINS[@]}"; do
    echo "───────────────────────────────────────────────────"
    echo "Building ${domain} domain container..."
    echo "───────────────────────────────────────────────────"

    apko build \
        "${APKO_DIR}/${domain}-domain.yaml" \
        "${domain}-domain:latest" \
        "${OUTPUT_DIR}/${domain}-domain.tar" \
        --arch x86_64

    # Load into podman
    podman load < "${OUTPUT_DIR}/${domain}-domain.tar"

    echo "✅ ${domain} domain container built and loaded"
    echo ""
done

echo "═══════════════════════════════════════════════════"
echo "  All Domain Containers Built Successfully!"
echo "═══════════════════════════════════════════════════"
echo ""
echo "Images:"
podman images | grep domain
```

---

## Persistent Storage Setup

### Directory Structure

**File**: `/home/user/containers/setup-persistent-storage.sh`

```bash
#!/bin/bash
set -e

BASE_DIR="/rw/containers/domains"

echo "Setting up persistent storage for domain containers..."

# Create base directory structure
sudo mkdir -p "${BASE_DIR}"/{axis,pipe,iv,eco}/{repos,cache,logs,config}

# Set ownership (match UIDs from apko configs)
sudo chown -R 1000:1000 "${BASE_DIR}/axis"
sudo chown -R 1001:1001 "${BASE_DIR}/pipe"
sudo chown -R 1002:1002 "${BASE_DIR}/iv"
sudo chown -R 1003:1003 "${BASE_DIR}/eco"

# Set permissions
sudo chmod -R 755 "${BASE_DIR}"

echo "✅ Persistent storage structure created:"
tree -L 3 "${BASE_DIR}"

# Create symlinks in user home for easy access
ln -sf "${BASE_DIR}/axis" ~/axis-repos
ln -sf "${BASE_DIR}/pipe" ~/pipe-repos
ln -sf "${BASE_DIR}/iv" ~/iv-repos
ln -sf "${BASE_DIR}/eco" ~/eco-repos

echo ""
echo "✅ Symlinks created in home directory:"
ls -la ~/*-repos
```

---

## Container Run Scripts

### AXIS Domain Container Runner

**File**: `/home/user/containers/run-axis.sh`

```bash
#!/bin/bash
set -e

DOMAIN="axis"
CONTAINER_NAME="${DOMAIN}-domain"
IMAGE="${DOMAIN}-domain:latest"
PERSIST_DIR="/rw/containers/domains/${DOMAIN}"

echo "Starting ${DOMAIN} domain container..."

podman run -d \
    --name "${CONTAINER_NAME}" \
    --hostname "${DOMAIN}-domain" \
    -v "${PERSIST_DIR}/repos:/repos:Z" \
    -v "${PERSIST_DIR}/cache:/home/${DOMAIN}/.cache:Z" \
    -v "${PERSIST_DIR}/logs:/var/log:Z" \
    -v "${PERSIST_DIR}/config:/home/${DOMAIN}/.config:Z" \
    -e CODEBERG_TOKEN="d0408771e085097495d59eb91bea7e0a582453de" \
    -e DOMAIN="${DOMAIN}" \
    --restart unless-stopped \
    "${IMAGE}" \
    sleep infinity

echo "✅ ${DOMAIN} container started: ${CONTAINER_NAME}"
echo ""
echo "Access with: podman exec -it ${CONTAINER_NAME} bash"
echo "View logs: podman logs -f ${CONTAINER_NAME}"
echo ""
echo "Repos location (host): ${PERSIST_DIR}/repos"
echo "Repos location (container): /repos"
```

### All Domains Runner

**File**: `/home/user/containers/run-all-domains.sh`

```bash
#!/bin/bash
set -e

DOMAINS=("axis" "pipe" "iv" "eco")

echo "═══════════════════════════════════════════════════"
echo "  Starting All Domain Containers"
echo "═══════════════════════════════════════════════════"
echo ""

for domain in "${DOMAINS[@]}"; do
    ./run-${domain}.sh
done

echo ""
echo "═══════════════════════════════════════════════════"
echo "  All Domain Containers Running"
echo "═══════════════════════════════════════════════════"
echo ""

podman ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
```

---

## Repository Cloning Automation

### Clone All AXIS Repos

**File**: `/home/user/containers/scripts/clone-all-axis-repos.sh`

```bash
#!/bin/bash
set -e

DOMAIN="axis"
CONTAINER_NAME="${DOMAIN}-domain"
TOKEN="d0408771e085097495d59eb91bea7e0a582453de"

# Array of all 14 AXIS organizations
AXIS_ORGS=(
    "AXIS-Bots"
    "AXIS-Core"
    "AXIS-Data"
    "AXIS-Decentral"
    "AXIS-Docs"
    "AXIS-Infra"
    "AXIS-IoT"
    "AXIS-KMS"
    "AXIS-Labs"
    "AXIS-Media"
    "AXIS-Observe"
    "AXIS-PM"
    "AXIS-Security"
    "AXIS-Tools"
)

echo "═══════════════════════════════════════════════════"
echo "  Cloning All AXIS Repositories (253 repos)"
echo "═══════════════════════════════════════════════════"
echo ""

# Execute inside container
podman exec -it "${CONTAINER_NAME}" bash -c "
    cd /repos

    for org in ${AXIS_ORGS[@]}; do
        echo \"Processing organization: \${org}\"

        # Create org directory
        mkdir -p \"\${org}\"
        cd \"\${org}\"

        # Get all repos for this org
        repos=\$(curl -s \"https://codeberg.org/api/v1/orgs/\${org}/repos\" \
            -H \"Authorization: token ${TOKEN}\" | \
            jq -r '.[].name')

        for repo in \${repos}; do
            if [ -d \"\${repo}\" ]; then
                echo \"  ✓ \${repo} (already exists, pulling)\"
                cd \"\${repo}\"
                git pull
                cd ..
            else
                echo \"  ⬇ Cloning \${repo}\"
                git clone \"https://${TOKEN}@codeberg.org/\${org}/\${repo}.git\"
            fi
        done

        cd /repos
        echo \"\"
    done

    echo \"\"
    echo \"✅ All AXIS repositories cloned\"
    echo \"\"
    du -sh /repos/*
"

echo ""
echo "✅ AXIS repository cloning complete"
echo "Location (host): /rw/containers/domains/axis/repos"
echo "Location (container): /repos"
```

### Clone Script for Other Domains

**File**: `/home/user/containers/scripts/clone-domain-repos.sh`

```bash
#!/bin/bash
set -e

DOMAIN="${1}"
CONTAINER_NAME="${DOMAIN}-domain"
TOKEN="d0408771e085097495d59eb91bea7e0a582453de"

if [ -z "${DOMAIN}" ]; then
    echo "Usage: $0 <domain>"
    echo "Available domains: pipe, iv, eco"
    exit 1
fi

case "${DOMAIN}" in
    pipe)
        ORG="PIPE"
        ;;
    iv)
        ORG="IntelliVerse"
        ;;
    eco)
        ORG="ECOX"
        ;;
    *)
        echo "Unknown domain: ${DOMAIN}"
        exit 1
        ;;
esac

echo "═══════════════════════════════════════════════════"
echo "  Cloning ${ORG} Repositories"
echo "═══════════════════════════════════════════════════"
echo ""

podman exec -it "${CONTAINER_NAME}" bash -c "
    cd /repos

    # Get all repos for this org
    repos=\$(curl -s \"https://codeberg.org/api/v1/orgs/${ORG}/repos\" \
        -H \"Authorization: token ${TOKEN}\" | \
        jq -r '.[].name')

    for repo in \${repos}; do
        if [ -d \"\${repo}\" ]; then
            echo \"  ✓ \${repo} (already exists, pulling)\"
            cd \"\${repo}\"
            git pull
            cd ..
        else
            echo \"  ⬇ Cloning \${repo}\"
            git clone \"https://${TOKEN}@codeberg.org/${ORG}/\${repo}.git\"
        fi
    done

    echo \"\"
    echo \"✅ All ${ORG} repositories cloned\"
    du -sh /repos/*
"
```

---

## Management Scripts

### Stop All Domains

**File**: `/home/user/containers/stop-all-domains.sh`

```bash
#!/bin/bash

DOMAINS=("axis" "pipe" "iv" "eco")

echo "Stopping all domain containers..."

for domain in "${DOMAINS[@]}"; do
    container="${domain}-domain"
    if podman ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        echo "Stopping ${container}..."
        podman stop "${container}"
    fi
done

echo "✅ All domain containers stopped"
```

### Start All Domains (Auto-start on Boot)

**File**: `/home/user/containers/autostart-domains.sh`

```bash
#!/bin/bash

# This script should be added to ~/.bashrc or systemd

DOMAINS=("axis" "pipe" "iv" "eco")

for domain in "${DOMAINS[@]}"; do
    container="${domain}-domain"

    if ! podman ps --format '{{.Names}}' | grep -q "^${container}$"; then
        if podman ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
            echo "Starting existing ${container}..."
            podman start "${container}"
        else
            echo "Creating and starting ${container}..."
            /home/user/containers/run-${domain}.sh
        fi
    else
        echo "✓ ${container} already running"
    fi
done
```

### Container Shell Access

**File**: `/home/user/containers/shell.sh`

```bash
#!/bin/bash

DOMAIN="${1:-axis}"
CONTAINER_NAME="${DOMAIN}-domain"

echo "Accessing ${DOMAIN} domain container..."
podman exec -it "${CONTAINER_NAME}" bash
```

---

## Claude Code Integration

### Custom Slash Command: Container Management

**File**: `/home/user/.claude/commands/domains/manage.md`

```markdown
---
description: Manage domain containers (AXIS, PIPE, IV, ECO)
model: haiku
---

# Domain Container Management

Manage all 4 domain containers from Claude Code.

## Start All Domains
\`\`\`bash
/home/user/containers/run-all-domains.sh
\`\`\`

## Stop All Domains
\`\`\`bash
/home/user/containers/stop-all-domains.sh
\`\`\`

## Access Domain Shell
\`\`\`bash
# Access AXIS domain
/home/user/containers/shell.sh axis

# Access other domains
/home/user/containers/shell.sh pipe
/home/user/containers/shell.sh iv
/home/user/containers/shell.sh eco
\`\`\`

## Clone All Repos
\`\`\`bash
# Clone all AXIS repos (253 repos)
/home/user/containers/scripts/clone-all-axis-repos.sh

# Clone other domain repos
/home/user/containers/scripts/clone-domain-repos.sh pipe
/home/user/containers/scripts/clone-domain-repos.sh iv
/home/user/containers/scripts/clone-domain-repos.sh eco
\`\`\`

## Check Status
\`\`\`bash
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
\`\`\`

## View Logs
\`\`\`bash
podman logs -f axis-domain
podman logs -f pipe-domain
podman logs -f iv-domain
podman logs -f eco-domain
\`\`\`
```

---

## Implementation Steps

### Day 1: Setup Infrastructure

```bash
# 1. Create directory structure
mkdir -p /home/user/containers/{apko,scripts,images}

# 2. Install apko
wget https://github.com/chainguard-dev/apko/releases/latest/download/apko_Linux_x86_64 -O /tmp/apko
chmod +x /tmp/apko
sudo mv /tmp/apko /usr/local/bin/apko

# 3. Setup persistent storage
/home/user/containers/setup-persistent-storage.sh
```

### Day 2: Build Containers

```bash
# 4. Create apko YAML files (copy from above)

# 5. Build all domain containers
cd /home/user/containers
./build-all-domains.sh
```

### Day 3: Start & Clone Repos

```bash
# 6. Start all containers
./run-all-domains.sh

# 7. Clone all AXIS repos (253 repos)
./scripts/clone-all-axis-repos.sh

# 8. Clone other domain repos
./scripts/clone-domain-repos.sh pipe
./scripts/clone-domain-repos.sh iv
./scripts/clone-domain-repos.sh eco
```

---

## Expected Results

### Container Sizes (Estimated)
- **axis-domain**: ~50MB (git + python + tools)
- **pipe-domain**: ~45MB (git + devops tools)
- **iv-domain**: ~55MB (git + python + ML libs)
- **eco-domain**: ~40MB (git + python)
- **Total**: ~190MB for all 4 containers

### Repository Storage
- **AXIS**: 253 repos × ~5MB avg = ~1.3GB
- **PIPE**: ~50 repos × ~5MB = ~250MB
- **IV**: ~40 repos × ~5MB = ~200MB
- **ECO**: ~30 repos × ~5MB = ~150MB
- **Total**: ~2GB for all repos

### Boot Time
- Container startup: <5 seconds per container
- Total ready time: <30 seconds for all 4 domains

---

## Advantages of This Approach

✅ **Persistent**: All repos preserved across reboots
✅ **Minimal**: Containers <50MB each using apko
✅ **Secure**: Chainguard Wolfi distroless base
✅ **Isolated**: Each domain in separate container
✅ **Fast**: Instant access to all 253+ repos
✅ **Organized**: Clear domain separation
✅ **Automated**: Single command to start/stop all
✅ **Scalable**: Easy to add new domains

---

**Status**: Complete Strategy Ready for Implementation ✅
**Next Step**: Create apko YAML files and build containers!
