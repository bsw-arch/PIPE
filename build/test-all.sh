#!/bin/bash
# Test All Containers - Master Test Script
# =========================================
# Runs basic tests on all PIPE Task Bot containers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
REGISTRY="${REGISTRY:-localhost:5000}"
TAG="${TAG:-latest}"

echo "🧪 PIPE Task Bot - Test All Containers"
echo "======================================="
echo "Registry: ${REGISTRY}"
echo "Tag: ${TAG}"
echo ""

# Containers to test
CONTAINERS=(
    "base"
    "task-bot"
    "task-scheduler"
    "task-executor"
)

# Track test results
SUCCESSFUL_TESTS=()
FAILED_TESTS=()

# Test each container
for container in "${CONTAINERS[@]}"; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Testing: ${container}"
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
        FAILED_TESTS+=("${container}")
        continue
    fi

    # Test 1: Python version
    echo "Test 1: Python version check..."
    if podman run --rm "${IMAGE_NAME}" python3 --version; then
        echo "✅ Python version test passed"
    else
        echo "❌ Python version test failed"
        FAILED_TESTS+=("${container}")
        continue
    fi

    # Test 2: Health check (basic import test)
    echo ""
    echo "Test 2: Health check..."
    if podman run --rm "${IMAGE_NAME}" python3 -c "import sys; sys.exit(0)"; then
        echo "✅ Health check passed"
    else
        echo "❌ Health check failed"
        FAILED_TESTS+=("${container}")
        continue
    fi

    # Test 3: Dependency imports (container-specific)
    echo ""
    echo "Test 3: Dependency imports..."
    case "${container}" in
        "base")
            if podman run --rm "${IMAGE_NAME}" python3 -c "import pydantic; print('✓ Pydantic imported')"; then
                echo "✅ Dependency test passed"
            else
                echo "❌ Dependency test failed"
                FAILED_TESTS+=("${container}")
                continue
            fi
            ;;
        "task-bot")
            if podman run --rm "${IMAGE_NAME}" python3 -c "import pydantic, requests, click, yaml, schedule"; then
                echo "✅ Dependency test passed"
            else
                echo "❌ Dependency test failed"
                FAILED_TESTS+=("${container}")
                continue
            fi
            ;;
        "task-scheduler")
            if podman run --rm "${IMAGE_NAME}" python3 -c "import pydantic, requests, yaml, schedule, croniter"; then
                echo "✅ Dependency test passed"
            else
                echo "❌ Dependency test failed"
                FAILED_TESTS+=("${container}")
                continue
            fi
            ;;
        "task-executor")
            if podman run --rm "${IMAGE_NAME}" python3 -c "import pydantic, requests, yaml"; then
                echo "✅ Dependency test passed"
            else
                echo "❌ Dependency test failed"
                FAILED_TESTS+=("${container}")
                continue
            fi
            ;;
    esac

    # Test 4: User check (non-root)
    echo ""
    echo "Test 4: Non-root user check..."
    USER_ID=$(podman run --rm "${IMAGE_NAME}" id -u)
    if [ "${USER_ID}" = "65532" ]; then
        echo "✅ Non-root user test passed (uid: ${USER_ID})"
    else
        echo "❌ Non-root user test failed (expected uid 65532, got ${USER_ID})"
        FAILED_TESTS+=("${container}")
        continue
    fi

    # All tests passed
    echo ""
    echo "✅ All tests passed for: ${container}"
    SUCCESSFUL_TESTS+=("${container}")
done

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Successful tests (${#SUCCESSFUL_TESTS[@]}):"
for test in "${SUCCESSFUL_TESTS[@]}"; do
    echo "  ✅ ${test}"
done

if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
    echo ""
    echo "Failed tests (${#FAILED_TESTS[@]}):"
    for test in "${FAILED_TESTS[@]}"; do
        echo "  ❌ ${test}"
    done
fi

echo ""
echo "Next steps:"
echo "  1. Push to registry: ./build/push-all.sh"
echo "  2. Deploy: docker-compose up -d"

# Exit with error if any tests failed
if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
    exit 1
fi
