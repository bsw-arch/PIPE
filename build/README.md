# Build Scripts - PIPE Task Bot

Automated build, test, and deployment scripts for all PIPE Task Bot containers.

---

## 📋 Available Scripts

### build-all.sh
Builds all containers in the correct order (base → applications).

```bash
# Build with defaults
./build/build-all.sh

# Build with custom registry and tag
REGISTRY=myregistry.com TAG=v1.0.0 ./build/build-all.sh
```

**Features:**
- Builds in dependency order (base first)
- Validates image sizes against targets
- Tracks successful and failed builds
- Shows total platform size

**Output:**
- Container images in local registry
- Build summary with sizes
- Total size validation (<30 MB target)

---

### generate-all-sboms.sh
Generates Software Bill of Materials for all containers.

```bash
# Generate SBOMs
./build/generate-all-sboms.sh

# Generate for specific registry/tag
REGISTRY=myregistry.com TAG=v1.0.0 ./build/generate-all-sboms.sh
```

**Features:**
- Generates SPDX and CycloneDX format SBOMs
- Scans for vulnerabilities with Grype
- Creates human-readable package lists
- Tracks vulnerability count across all containers

**Output:**
- `sbom/base/` - Base image SBOM
- `sbom/task-bot/` - Task bot SBOM
- `sbom/task-scheduler/` - Scheduler SBOM
- `sbom/task-executor/` - Executor SBOM

Each directory contains:
- `sbom.spdx.json` - SPDX format
- `sbom.cyclonedx.json` - CycloneDX format
- `packages.txt` - Human-readable list
- `vulnerabilities.json` - CVE scan results

---

### test-all.sh
Runs comprehensive tests on all containers.

```bash
# Test all containers
./build/test-all.sh

# Test specific registry/tag
REGISTRY=myregistry.com TAG=v1.0.0 ./build/test-all.sh
```

**Tests performed:**
1. Python version check
2. Health check (import test)
3. Dependency imports (container-specific)
4. Non-root user validation (uid 65532)

**Features:**
- Validates each container independently
- Checks security settings
- Verifies dependencies load correctly
- Tracks test results per container

---

### push-all.sh
Pushes all containers to the registry.

```bash
# Push to default registry (localhost:5000)
./build/push-all.sh

# Push to custom registry
REGISTRY=myregistry.com TAG=v1.0.0 ./build/push-all.sh
```

**Features:**
- Verifies images exist before pushing
- Pushes all containers in order
- Tracks successful and failed pushes
- Provides summary report

---

## 🔄 Complete Workflow

### Development Workflow
```bash
# 1. Build all containers
./build/build-all.sh

# 2. Test all containers
./build/test-all.sh

# 3. Generate SBOMs
./build/generate-all-sboms.sh

# 4. Review results
cat sbom/*/vulnerabilities.json
```

### Release Workflow
```bash
# 1. Build with version tag
REGISTRY=myregistry.com TAG=v1.0.0 ./build/build-all.sh

# 2. Test
REGISTRY=myregistry.com TAG=v1.0.0 ./build/test-all.sh

# 3. Generate SBOMs
REGISTRY=myregistry.com TAG=v1.0.0 ./build/generate-all-sboms.sh

# 4. Push to registry
REGISTRY=myregistry.com TAG=v1.0.0 ./build/push-all.sh
```

---

## 📊 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REGISTRY` | `localhost:5000` | Container registry URL |
| `TAG` | `latest` | Image tag |

### Examples

```bash
# Local development
./build/build-all.sh

# Production registry
REGISTRY=registry.axis.org ./build/build-all.sh

# Specific version
TAG=v1.2.3 ./build/build-all.sh

# Both
REGISTRY=registry.axis.org TAG=v1.2.3 ./build/build-all.sh
```

---

## 🎯 Build Targets

### Size Targets
- **Base**: 3-5 MB
- **Task Bot**: 6-8 MB
- **Task Scheduler**: 5-7 MB
- **Task Executor**: 6-8 MB
- **Total Platform**: <30 MB

### Security Targets
- **CVE Count**: 0 (Wolfi is CVE-free)
- **User**: Non-root (uid 65532)
- **Attack Surface**: Minimal packages only

---

## 🔍 Troubleshooting

### Build Failures

```bash
# Check individual container build
cd containers/base
./scripts/build.sh

# View build logs
podman images --all
podman history localhost:5000/axis-task-bot-base:latest
```

### SBOM Generation Failures

```bash
# Check if Syft is installed
syft --version

# Install if missing
go install github.com/anchore/syft/cmd/syft@latest

# Check if Grype is installed
grype --version

# Install if missing
go install github.com/anchore/grype/cmd/grype@latest
```

### Test Failures

```bash
# Run individual container test
podman run --rm localhost:5000/axis-task-bot:latest python3 --version

# Check logs
podman logs <container-id>

# Run interactively
podman run -it --rm localhost:5000/axis-task-bot:latest /bin/sh
```

### Push Failures

```bash
# Check registry is accessible
curl http://localhost:5000/v2/_catalog

# Login to registry (if required)
podman login myregistry.com

# Check image exists
podman images | grep axis
```

---

## 📁 Output Structure

```
axis-task-bot/
├── build/
│   ├── build-all.sh          # This builds containers
│   ├── generate-all-sboms.sh # This generates SBOMs
│   ├── test-all.sh           # This tests containers
│   ├── push-all.sh           # This pushes to registry
│   └── README.md             # This file
├── sbom/
│   ├── base/
│   │   ├── sbom.spdx.json
│   │   ├── sbom.cyclonedx.json
│   │   ├── packages.txt
│   │   └── vulnerabilities.json
│   ├── task-bot/
│   ├── task-scheduler/
│   └── task-executor/
└── containers/
    ├── base/
    ├── task-bot/
    ├── task-scheduler/
    └── task-executor/
```

---

## 🚀 CI/CD Integration

These scripts are designed to work in CI/CD pipelines:

```yaml
# Woodpecker CI example
pipeline:
  build:
    image: docker.io/library/docker:latest
    commands:
      - ./build/build-all.sh

  test:
    image: docker.io/library/docker:latest
    commands:
      - ./build/test-all.sh

  sbom:
    image: docker.io/library/docker:latest
    commands:
      - ./build/generate-all-sboms.sh

  push:
    image: docker.io/library/docker:latest
    commands:
      - ./build/push-all.sh
    when:
      branch: main
```

---

**Status**: Ready for use
**Automation**: Complete build→test→SBOM→push workflow
**Target**: <30 MB total platform size
**Security**: SBOM + CVE scanning + non-root
