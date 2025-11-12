#!/bin/bash
# Push All Containers - Master Push Script
# =========================================
# Pushes all PIPE Task Bot containers to registry

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
REGISTRY="${REGISTRY:-localhost:5000}"
TAG="${TAG:-latest}"

echo "📤 PIPE Task Bot - Push All Containers"
echo "======================================="
echo "Registry: ${REGISTRY}"
echo "Tag: ${TAG}"
echo ""

# Containers to push
CONTAINERS=(
    "base"
    "task-bot"
    "task-scheduler"
    "task-executor"
)

# Track push results
SUCCESSFUL_PUSHES=()
FAILED_PUSHES=()

# Push each container
for container in "${CONTAINERS[@]}"; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Pushing: ${container}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Determine image name
    if [ "${container}" = "base" ]; then
        IMAGE_NAME="${REGISTRY}/axis-task-bot-base:${TAG}"
    else
        IMAGE_NAME="${REGISTRY}/axis-${container}:${TAG}"
    fi

    # Check if image exists
    if ! podman images "${IMAGE_NAME}" --format "{{.Repository}}" | grep -q "axis"; then
        echo "⚠️  Warning: Image not found: ${IMAGE_NAME}"
        echo "Please build the image first: ./build/build-all.sh"
        FAILED_PUSHES+=("${container}")
        continue
    fi

    # Push to registry
    echo "Pushing ${IMAGE_NAME}..."
    if podman push "${IMAGE_NAME}"; then
        echo "✅ Push successful: ${IMAGE_NAME}"
        SUCCESSFUL_PUSHES+=("${container}")
    else
        echo "❌ Push failed: ${container}"
        FAILED_PUSHES+=("${container}")
    fi
done

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Push Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Successful pushes (${#SUCCESSFUL_PUSHES[@]}):"
for push in "${SUCCESSFUL_PUSHES[@]}"; do
    echo "  ✅ ${push}"
done

if [ ${#FAILED_PUSHES[@]} -gt 0 ]; then
    echo ""
    echo "Failed pushes (${#FAILED_PUSHES[@]}):"
    for push in "${FAILED_PUSHES[@]}"; do
        echo "  ❌ ${push}"
    done
fi

echo ""
echo "All images pushed to: ${REGISTRY}"

# Exit with error if any pushes failed
if [ ${#FAILED_PUSHES[@]} -gt 0 ]; then
    exit 1
fi
