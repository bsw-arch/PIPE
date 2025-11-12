#!/bin/bash
# SBOM Generation Script - Base Image
# ====================================
# Generates Software Bill of Materials using Syft

set -e

IMAGE_NAME=${1:-"localhost:5000/axis-task-bot-base:latest"}
OUTPUT_DIR=${2:-"../../../sbom/base"}

echo "🔍 Generating SBOM for: ${IMAGE_NAME}"
echo "📁 Output directory: ${OUTPUT_DIR}"
echo ""

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Generate SPDX format SBOM
echo "Generating SPDX SBOM..."
syft "${IMAGE_NAME}" \
  -o spdx-json \
  --file "${OUTPUT_DIR}/sbom.spdx.json"

# Generate CycloneDX format SBOM
echo "Generating CycloneDX SBOM..."
syft "${IMAGE_NAME}" \
  -o cyclonedx-json \
  --file "${OUTPUT_DIR}/sbom.cyclonedx.json"

# Generate human-readable package list
echo "Generating package list..."
syft "${IMAGE_NAME}" \
  -o table \
  --file "${OUTPUT_DIR}/packages.txt"

# Scan for vulnerabilities with Grype
echo ""
echo "🔒 Scanning for vulnerabilities..."
grype "${IMAGE_NAME}" \
  -o json \
  --file "${OUTPUT_DIR}/vulnerabilities.json"

# Create summary
echo ""
echo "📊 SBOM Summary:"
echo "----------------"
echo "Total packages: $(jq '.packages | length' "${OUTPUT_DIR}/sbom.spdx.json")"
echo ""

# Check vulnerabilities
VULN_COUNT=$(jq '.matches | length' "${OUTPUT_DIR}/vulnerabilities.json")
echo "Vulnerabilities found: ${VULN_COUNT}"

if [ "${VULN_COUNT}" -gt 0 ]; then
  echo "⚠️  WARNING: Vulnerabilities detected!"
  echo ""
  echo "Critical/High vulnerabilities:"
  jq -r '.matches[] | select(.vulnerability.severity == "Critical" or .vulnerability.severity == "High") | "\(.vulnerability.severity): \(.vulnerability.id) in \(.artifact.name)"' "${OUTPUT_DIR}/vulnerabilities.json"
else
  echo "✅ No vulnerabilities found!"
fi

echo ""
echo "✅ SBOM generation complete!"
echo ""
echo "Generated files:"
ls -lh "${OUTPUT_DIR}"
