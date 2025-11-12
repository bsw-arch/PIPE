# OpenBao Policy for PIPE Task Bot
# =================================
# Defines access permissions for task bot services

# Allow reading task bot secrets
path "axis-bots/data/task-bot/*" {
  capabilities = ["read", "list"]
}

# Allow reading scheduler secrets
path "axis-bots/data/task-scheduler/*" {
  capabilities = ["read", "list"]
}

# Allow reading executor secrets
path "axis-bots/data/task-executor/*" {
  capabilities = ["read", "list"]
}

# Allow reading shared secrets
path "axis-bots/data/shared/*" {
  capabilities = ["read", "list"]
}

# Allow writing operational data (for learning/metrics)
path "axis-bots/data/operational/*" {
  capabilities = ["create", "update", "read", "list"]
}

# Allow dynamic database credentials
path "database/creds/pipe-task-bot" {
  capabilities = ["read"]
}

# Allow PKI certificate generation
path "pki/issue/pipe-task-bot" {
  capabilities = ["create", "update"]
}

# Allow token self-renewal
path "auth/token/renew-self" {
  capabilities = ["update"]
}

# Allow token lookup
path "auth/token/lookup-self" {
  capabilities = ["read"]
}

# Allow reading metadata
path "axis-bots/metadata/*" {
  capabilities = ["read", "list"]
}
