#!/bin/bash
# Build All Containers - Master Build Script
# ===========================================
# Builds all PIPE Task Bot containers in correct order
# Generates SBOMs and validates sizes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
REGISTRY="${REGISTRY:-localhost:5000}"
TAG="${TAG:-latest}"

echo "🏗️  PIPE Task Bot - Build All Containers"
echo "=========================================="
echo "Registry: ${REGISTRY}"
echo "Tag: ${TAG}"
echo ""

# Build order (base first, then applications)
CONTAINERS=(
    "base"
    "task-bot"
    "task-scheduler"
    "task-executor"
)

# Track build results
SUCCESSFUL_BUILDS=()
FAILED_BUILDS=()

# Build each container
for container in "${CONTAINERS[@]}"; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Building: ${container}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    CONTAINER_DIR="${PROJECT_DIR}/containers/${container}"

    if [ ! -d "${CONTAINER_DIR}" ]; then
        echo "⚠️  Warning: Container directory not found: ${CONTAINER_DIR}"
        FAILED_BUILDS+=("${container}")
        continue
    fi

    # Build container
    if [ -f "${CONTAINER_DIR}/scripts/build.sh" ]; then
        cd "${CONTAINER_DIR}"

        # Determine image name
        if [ "${container}" = "base" ]; then
            IMAGE_NAME="${REGISTRY}/axis-task-bot-base"
        else
            IMAGE_NAME="${REGISTRY}/axis-${container}"
        fi

        # Build
        if ./scripts/build.sh "${IMAGE_NAME}" "${TAG}"; then
            echo "✅ Build successful: ${IMAGE_NAME}:${TAG}"
            SUCCESSFUL_BUILDS+=("${container}")
        else
            echo "❌ Build failed: ${container}"
            FAILED_BUILDS+=("${container}")
        fi
    else
        echo "⚠️  Warning: Build script not found: ${CONTAINER_DIR}/scripts/build.sh"
        FAILED_BUILDS+=("${container}")
    fi
done

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Build Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Successful builds (${#SUCCESSFUL_BUILDS[@]}):"
for build in "${SUCCESSFUL_BUILDS[@]}"; do
    echo "  ✅ ${build}"
done

if [ ${#FAILED_BUILDS[@]} -gt 0 ]; then
    echo ""
    echo "Failed builds (${#FAILED_BUILDS[@]}):"
    for build in "${FAILED_BUILDS[@]}"; do
        echo "  ❌ ${build}"
    done
fi

# Show total sizes
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💾 Container Sizes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

podman images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | grep -E "axis-task-bot|axis-task-"

# Calculate total size
TOTAL_SIZE=0
for container in "${SUCCESSFUL_BUILDS[@]}"; do
    if [ "${container}" = "base" ]; then
        IMAGE_NAME="${REGISTRY}/axis-task-bot-base:${TAG}"
    else
        IMAGE_NAME="${REGISTRY}/axis-${container}:${TAG}"
    fi

    SIZE=$(podman images "${IMAGE_NAME}" --format "{{.Size}}" | sed 's/MB//g' | tr -d ' ')
    if [ ! -z "${SIZE}" ]; then
        TOTAL_SIZE=$(echo "${TOTAL_SIZE} + ${SIZE}" | bc -l)
    fi
done

echo ""
echo "Total size: ${TOTAL_SIZE} MB"
echo "Target: < 30 MB"

if (( $(echo "${TOTAL_SIZE} < 30" | bc -l) )); then
    echo "✅ Size target met!"
else
    echo "⚠️  Warning: Total size exceeds target"
fi

echo ""
echo "Next steps:"
echo "  1. Generate SBOMs: ./build/generate-all-sboms.sh"
echo "  2. Test containers: ./build/test-all.sh"
echo "  3. Push to registry: ./build/push-all.sh"

# Exit with error if any builds failed
if [ ${#FAILED_BUILDS[@]} -gt 0 ]; then
    exit 1
fi
