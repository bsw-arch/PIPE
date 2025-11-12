# PIPE Task Bot - Base Wolfi Image
## Ultra-Minimal Container Base (3-5 MB)

---

## 📦 What's Inside

This is the minimal Wolfi Linux base image for all PIPE Task Bot containers.

### Packages
- `wolfi-baselayout` - Minimal filesystem structure
- `ca-certificates` - SSL/TLS certificates
- `busybox` - Minimal Unix utilities
- `python-3.11` - Python runtime
- `python-3.11-base` - Python base libraries

**Total Size: ~3-5 MB**

---

## 🏗️ Building

### Prerequisites
```bash
# Install APKo
go install chainguard.dev/apko@latest

# Install Melange (for custom packages)
go install chainguard.dev/melange@latest

# Install SBOM tools
go install github.com/anchore/syft/cmd/syft@latest
go install github.com/anchore/grype/cmd/grype@latest
```

### Build with APKo
```bash
# Build base image
./scripts/build.sh

# Or specify custom name/tag
./scripts/build.sh localhost:5000/axis-base v1.0.0
```

### Build Custom Package with Melange
```bash
# Build APK package
melange build melange.yaml \
  --arch x86_64 \
  --signing-key melange.rsa

# Output: packages/x86_64/axis-task-bot-base-0.1.0-r0.apk
```

---

## 🔒 Security

### SBOM Generation
```bash
# Generate Software Bill of Materials
./sbom/generate.sh localhost:5000/axis-task-bot-base:latest

# Output files:
# - sbom.spdx.json (SPDX format)
# - sbom.cyclonedx.json (CycloneDX format)
# - packages.txt (human-readable)
# - vulnerabilities.json (CVE scan)
```

### Vulnerability Scanning
```bash
# Scan for CVEs
grype localhost:5000/axis-task-bot-base:latest

# Expected: 0 vulnerabilities (Wolfi is CVE-free)
```

### Signature Verification
```bash
# Sign with Cosign
cosign sign --key cosign.key localhost:5000/axis-task-bot-base:latest

# Verify
cosign verify --key cosign.pub localhost:5000/axis-task-bot-base:latest
```

---

## 🧪 Testing

### Quick Test
```bash
# Test Python
podman run --rm localhost:5000/axis-task-bot-base:latest python3 --version

# Expected: Python 3.11.x
```

### Size Verification
```bash
# Check image size
podman images localhost:5000/axis-task-bot-base --format "{{.Size}}"

# Expected: < 6 MB
```

### Health Check
```bash
# Run health check
podman run --rm localhost:5000/axis-task-bot-base:latest /app/health-check.sh

# Expected: exit code 0
```

---

## 📊 Configuration Files

### wolfi.yaml
Defines Wolfi OS packages to include in the image.

**Key settings:**
- Minimal package list
- Non-root user (uid 65532)
- Python 3.11 runtime

### apko.yaml
APKo build configuration for creating the container.

**Key features:**
- Multi-arch support (x86_64, aarch64)
- Security hardening
- OCI metadata

### melange.yaml
Custom package build configuration.

**Creates:**
- `axis-task-bot-base` - Runtime package
- `axis-task-bot-base-dev` - Development tools

---

## 🎯 Usage in Derived Images

### Dockerfile Example
```dockerfile
FROM localhost:5000/axis-task-bot-base:latest

WORKDIR /app

# Add application code
COPY agents/ /app/agents/

# Add minimal dependencies
RUN pip install --no-cache-dir \
    pydantic==2.5.0 \
    requests==2.31.0

USER nonroot

CMD ["python3", "-m", "agents.task_bot"]
```

### APKo Extension Example
```yaml
# task-bot/apko.yaml
contents:
  repositories:
    - https://packages.wolfi.dev/os
  packages:
    - axis-task-bot-base  # Our base package
    - python-requests      # Additional deps

# Inherits: Python, ca-certificates, etc
```

---

## 📈 Size Optimization Tips

### Current Size Breakdown
```
wolfi-baselayout:    ~500 KB
ca-certificates:     ~200 KB
busybox:             ~700 KB
python-3.11:         ~2-3 MB
Total:               ~3-5 MB
```

### To Reduce Further
1. **Remove busybox** if no shell commands needed
2. **Use python-3.11-base only** (smaller subset)
3. **Static linking** for critical dependencies
4. **Strip debug symbols** from binaries

---

## 🔄 Update Process

### Rebuild on Wolfi Updates
```bash
# Pull latest Wolfi packages
apko build apko.yaml latest output.tar --debug

# Regenerate SBOM
./sbom/generate.sh

# Verify no new CVEs
grype localhost:5000/axis-task-bot-base:latest
```

### Versioning
- `latest` - Current development
- `v1.x.x` - Stable releases
- `nightly` - Automated daily builds

---

## 🐛 Troubleshooting

### Image Too Large
```bash
# Analyze layers
podman history localhost:5000/axis-task-bot-base:latest

# Check what's included
podman run --rm -it localhost:5000/axis-task-bot-base:latest sh
ls -lhR /
```

### Build Failures
```bash
# Enable debug output
apko build apko.yaml output output.tar --debug

# Check APKo logs
cat /tmp/apko-*.log
```

### Missing Packages
```bash
# Search Wolfi packages
https://packages.wolfi.dev/os

# Check package dependencies
apk info python-3.11
```

---

## 📞 Support

For issues:
1. Check `apko.yaml` syntax
2. Verify Wolfi package availability
3. Review build logs
4. Open issue on Codeberg

---

**Target**: 3-5 MB base image
**Status**: Ready for building
**Security**: CVE-free Wolfi base
**SBOM**: Automated generation
