#!/bin/bash
# OpenBao Secrets Setup for PIPE Task Bot
# ========================================
# Configures OpenBao with secrets and policies

set -e

VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-}"

echo "🔐 Setting up OpenBao secrets for PIPE Task Bot"
echo "================================================"
echo "Vault Address: ${VAULT_ADDR}"
echo ""

# Check if OpenBao is accessible
if ! openbao status &>/dev/null; then
    echo "❌ Error: OpenBao is not accessible at ${VAULT_ADDR}"
    echo "Please ensure OpenBao is running and VAULT_ADDR is correct"
    exit 1
fi

echo "✅ OpenBao is accessible"
echo ""

# Enable KV secrets engine if not already enabled
echo "📦 Enabling KV secrets engine..."
openbao secrets enable -path=axis-bots kv-v2 2>/dev/null || echo "  (already enabled)"
echo ""

# Create policies
echo "📜 Creating OpenBao policies..."
openbao policy write pipe-artifact-bot - <<EOF
# PIPE Task Bot Policy
path "axis-bots/data/task-bot/*" {
  capabilities = ["read", "list"]
}

path "axis-bots/data/task-scheduler/*" {
  capabilities = ["read", "list"]
}

path "axis-bots/data/task-executor/*" {
  capabilities = ["read", "list"]
}

path "axis-bots/data/shared/*" {
  capabilities = ["read", "list"]
}

path "axis-bots/data/operational/*" {
  capabilities = ["create", "update", "read", "list"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
EOF

echo "✅ Policy 'pipe-artifact-bot' created"
echo ""

# Store secrets for Task Bot
echo "🔑 Storing Task Bot secrets..."
openbao kv put axis-bots/task-bot \
    keragr_url="http://meta-keragr:3108" \
    coordination_url="http://axis-coordination:3111" \
    api_key="$(openssl rand -base64 32)" \
    encryption_key="$(openssl rand -base64 32)" \
    log_level="INFO" \
    autonomous="true" \
    learning_enabled="true" \
    togaf_compliance="true"

echo "✅ Task Bot secrets stored"
echo ""

# Store secrets for Task Scheduler
echo "🔑 Storing Task Scheduler secrets..."
openbao kv put axis-bots/task-scheduler \
    scheduler_token="$(openssl rand -base64 32)" \
    cron_enabled="true" \
    max_concurrent_tasks="10"

echo "✅ Task Scheduler secrets stored"
echo ""

# Store secrets for Task Executor
echo "🔑 Storing Task Executor secrets..."
openbao kv put axis-bots/task-executor \
    executor_token="$(openssl rand -base64 32)" \
    worker_count="4" \
    max_retries="3"

echo "✅ Task Executor secrets stored"
echo ""

# Store shared secrets
echo "🔑 Storing shared secrets..."
openbao kv put axis-bots/shared \
    jwt_secret="$(openssl rand -base64 64)" \
    session_key="$(openssl rand -base64 32)" \
    encryption_salt="$(openssl rand -base64 16)"

echo "✅ Shared secrets stored"
echo ""

# Enable database secrets engine for dynamic credentials
echo "💾 Configuring dynamic database credentials..."
openbao secrets enable database 2>/dev/null || echo "  (already enabled)"

# Configure PostgreSQL connection (example)
openbao write database/config/axis-postgres \
    plugin_name=postgresql-database-plugin \
    allowed_roles="pipe-artifact-bot" \
    connection_url="postgresql://{{username}}:{{password}}@localhost:5432/axis?sslmode=disable" \
    username="vault" \
    password="vaultpass" 2>/dev/null || echo "  (already configured)"

# Create database role
openbao write database/roles/pipe-artifact-bot \
    db_name=axis-postgres \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h" 2>/dev/null || echo "  (already configured)"

echo "✅ Dynamic database credentials configured"
echo ""

# Enable PKI secrets engine for certificate generation
echo "🔐 Configuring PKI for certificate generation..."
openbao secrets enable pki 2>/dev/null || echo "  (already enabled)"

# Set TTL
openbao secrets tune -max-lease-ttl=87600h pki 2>/dev/null

# Generate root CA
openbao write -field=certificate pki/root/generate/internal \
    common_name="axis-bots.local" \
    ttl=87600h > /tmp/axis-ca.crt 2>/dev/null || echo "  (already configured)"

# Configure CA and CRL URLs
openbao write pki/config/urls \
    issuing_certificates="${VAULT_ADDR}/v1/pki/ca" \
    crl_distribution_points="${VAULT_ADDR}/v1/pki/crl" 2>/dev/null

# Create PKI role
openbao write pki/roles/pipe-artifact-bot \
    allowed_domains="axis-bots.local" \
    allow_subdomains=true \
    max_ttl="720h" 2>/dev/null || echo "  (already configured)"

echo "✅ PKI configured"
echo ""

# Enable Kubernetes auth method
echo "☸️  Configuring Kubernetes authentication..."
openbao auth enable kubernetes 2>/dev/null || echo "  (already enabled)"

# Note: Kubernetes auth config requires cluster details
# This will be configured by the OpenTofu module

echo "✅ Kubernetes auth enabled"
echo ""

# Create app role for CI/CD
echo "🤖 Configuring AppRole for CI/CD..."
openbao auth enable approle 2>/dev/null || echo "  (already enabled)"

openbao write auth/approle/role/ci-cd \
    secret_id_ttl=24h \
    token_num_uses=0 \
    token_ttl=1h \
    token_max_ttl=4h \
    policies="pipe-artifact-bot"

ROLE_ID=$(openbao read -field=role_id auth/approle/role/ci-cd/role-id)
SECRET_ID=$(openbao write -field=secret_id -f auth/approle/role/ci-cd/secret-id)

echo "✅ AppRole configured"
echo ""
echo "  Role ID: ${ROLE_ID}"
echo "  Secret ID: ${SECRET_ID}"
echo "  (Save these for CI/CD pipeline)"
echo ""

# Verify setup
echo "🔍 Verifying setup..."
echo ""

echo "Testing secret retrieval:"
openbao kv get -field=keragr_url axis-bots/task-bot && echo "  ✅ Can read task-bot secrets"
openbao kv get -field=scheduler_token axis-bots/task-scheduler && echo "  ✅ Can read scheduler secrets"
openbao kv get -field=executor_token axis-bots/task-executor && echo "  ✅ Can read executor secrets"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ OpenBao setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Configure Kubernetes auth: cd iac/opentofu && tofu apply"
echo "  2. Deploy with Helm: helm install pipe-artifact-bot iac/helm/charts/pipe-artifact-bot"
echo "  3. Or deploy with Ansible: ansible-playbook iac/ansible/playbooks/deploy-containers.yml"
echo ""
echo "Access secrets:"
echo "  openbao kv get axis-bots/task-bot"
echo "  openbao kv get axis-bots/task-scheduler"
echo "  openbao kv get axis-bots/task-executor"
echo ""
