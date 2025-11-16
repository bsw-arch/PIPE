# PIPE Infrastructure - OpenTofu Configuration
# This replaces HashiCorp Terraform with the open-source OpenTofu fork

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  # Remote backend for state management
  backend "s3" {
    bucket = "pipe-tofu-state"
    key    = "pipe/infrastructure.tfstate"
    region = "eu-central-1"

    # Optional: Use OpenBao for encryption
    # encrypt = true
    # kms_key_id = "openbao://transit/keys/tofu-state"
  }
}

# Provider Configuration
provider "kubernetes" {
  config_path = var.kubeconfig_path
}

provider "helm" {
  kubernetes {
    config_path = var.kubeconfig_path
  }
}

# Local Variables
locals {
  namespace_prefix = "pipe"
  common_labels = {
    "app.kubernetes.io/managed-by" = "opentofu"
    "app.kubernetes.io/part-of"    = "pipe-system"
    "environment"                   = var.environment
  }

  # Domain list from PIPE architecture
  domains = [
    "bni",
    "bnp",
    "axis",
    "iv",
    "ecox",
    "thrive",
    "dc",
    "bu",
    "pipe"
  ]
}

# Kubernetes Namespaces
resource "kubernetes_namespace" "pipe_system" {
  metadata {
    name = "${local.namespace_prefix}-system"

    labels = merge(local.common_labels, {
      "name" = "${local.namespace_prefix}-system"
      "tier" = "infrastructure"
    })

    annotations = {
      "description" = "PIPE system infrastructure namespace"
    }
  }
}

resource "kubernetes_namespace" "pipe_bots" {
  metadata {
    name = "${local.namespace_prefix}-bots"

    labels = merge(local.common_labels, {
      "name" = "${local.namespace_prefix}-bots"
      "tier" = "application"
    })

    annotations = {
      "description" = "PIPE bot deployments"
    }
  }
}

resource "kubernetes_namespace" "pipe_governance" {
  metadata {
    name = "${local.namespace_prefix}-governance"

    labels = merge(local.common_labels, {
      "name" = "${local.namespace_prefix}-governance"
      "tier" = "governance"
      "security" = "high"
    })

    annotations = {
      "description" = "PIPE governance and compliance"
    }
  }
}

resource "kubernetes_namespace" "pipe_monitoring" {
  metadata {
    name = "${local.namespace_prefix}-monitoring"

    labels = merge(local.common_labels, {
      "name" = "${local.namespace_prefix}-monitoring"
      "tier" = "observability"
    })

    annotations = {
      "description" = "PIPE monitoring and observability"
    }
  }
}

# Domain Namespaces
resource "kubernetes_namespace" "domains" {
  for_each = toset(local.domains)

  metadata {
    name = "${local.namespace_prefix}-domain-${each.key}"

    labels = merge(local.common_labels, {
      "name"   = "${local.namespace_prefix}-domain-${each.key}"
      "tier"   = "domain"
      "domain" = each.key
    })

    annotations = {
      "description" = "Domain namespace for ${upper(each.key)}"
    }
  }
}

# OpenBao Namespace
resource "kubernetes_namespace" "openbao" {
  metadata {
    name = "openbao-system"

    labels = merge(local.common_labels, {
      "name"     = "openbao-system"
      "tier"     = "security"
      "security" = "critical"
    })

    annotations = {
      "description" = "OpenBao secrets management"
    }
  }
}

# Zitadel Namespace
resource "kubernetes_namespace" "zitadel" {
  metadata {
    name = "zitadel-system"

    labels = merge(local.common_labels, {
      "name"     = "zitadel-system"
      "tier"     = "security"
      "security" = "critical"
    })

    annotations = {
      "description" = "Zitadel identity and access management"
    }
  }
}

# Zot Registry Namespace
resource "kubernetes_namespace" "zot" {
  metadata {
    name = "zot-registry"

    labels = merge(local.common_labels, {
      "name"     = "zot-registry"
      "tier"     = "infrastructure"
      "security" = "high"
    })

    annotations = {
      "description" = "Zot OCI container registry"
    }
  }
}

# Service Accounts
resource "kubernetes_service_account" "pipe_bot" {
  metadata {
    name      = "pipe-bot"
    namespace = kubernetes_namespace.pipe_bots.metadata[0].name

    labels = local.common_labels

    annotations = {
      "openbao.io/role" = "pipe-bot"
    }
  }
}

resource "kubernetes_service_account" "pipe_governance" {
  metadata {
    name      = "pipe-governance"
    namespace = kubernetes_namespace.pipe_governance.metadata[0].name

    labels = local.common_labels

    annotations = {
      "openbao.io/role" = "pipe-governance"
    }
  }
}

# ConfigMaps
resource "kubernetes_config_map" "pipe_config" {
  metadata {
    name      = "pipe-config"
    namespace = kubernetes_namespace.pipe_bots.metadata[0].name

    labels = local.common_labels
  }

  data = {
    "config.yaml" = templatefile("${path.module}/templates/config.yaml.tpl", {
      environment = var.environment
      log_level   = var.log_level
      domains     = local.domains
    })
  }
}

# Secrets (placeholder - actual secrets from OpenBao)
resource "kubernetes_secret" "pipe_tls" {
  metadata {
    name      = "pipe-tls"
    namespace = kubernetes_namespace.pipe_bots.metadata[0].name

    labels = local.common_labels

    annotations = {
      "openbao.io/managed" = "true"
    }
  }

  type = "kubernetes.io/tls"

  data = {
    "tls.crt" = ""  # Populated by OpenBao
    "tls.key" = ""  # Populated by OpenBao
  }

  lifecycle {
    ignore_changes = [data]
  }
}

# Network Policies (Cilium)
resource "kubernetes_network_policy" "pipe_default_deny" {
  metadata {
    name      = "default-deny-all"
    namespace = kubernetes_namespace.pipe_bots.metadata[0].name

    labels = local.common_labels
  }

  spec {
    pod_selector {}

    policy_types = ["Ingress", "Egress"]
  }
}

resource "kubernetes_network_policy" "pipe_hub_access" {
  metadata {
    name      = "pipe-hub-access"
    namespace = kubernetes_namespace.pipe_bots.metadata[0].name

    labels = local.common_labels
  }

  spec {
    pod_selector {
      match_labels = {
        "app" = "integration-hub-bot"
      }
    }

    policy_types = ["Ingress", "Egress"]

    ingress {
      from {
        namespace_selector {
          match_labels = {
            "tier" = "domain"
          }
        }
      }

      ports {
        protocol = "TCP"
        port     = "8080"
      }
    }

    egress {
      to {
        namespace_selector {
          match_labels = {
            "tier" = "domain"
          }
        }
      }

      ports {
        protocol = "TCP"
        port     = "8080"
      }
    }

    # Allow DNS
    egress {
      to {
        namespace_selector {
          match_labels = {
            "name" = "kube-system"
          }
        }
      }

      ports {
        protocol = "UDP"
        port     = "53"
      }
    }
  }
}

# Resource Quotas
resource "kubernetes_resource_quota" "pipe_bots" {
  metadata {
    name      = "pipe-bots-quota"
    namespace = kubernetes_namespace.pipe_bots.metadata[0].name

    labels = local.common_labels
  }

  spec {
    hard = {
      "requests.cpu"    = var.resource_quota_cpu
      "requests.memory" = var.resource_quota_memory
      "pods"            = var.resource_quota_pods
    }
  }
}

# Limit Ranges
resource "kubernetes_limit_range" "pipe_bots" {
  metadata {
    name      = "pipe-bots-limits"
    namespace = kubernetes_namespace.pipe_bots.metadata[0].name

    labels = local.common_labels
  }

  spec {
    limit {
      type = "Container"

      default = {
        cpu    = "500m"
        memory = "512Mi"
      }

      default_request = {
        cpu    = "100m"
        memory = "128Mi"
      }

      max = {
        cpu    = "2000m"
        memory = "2Gi"
      }

      min = {
        cpu    = "50m"
        memory = "64Mi"
      }
    }
  }
}

# Outputs
output "namespaces" {
  description = "Created Kubernetes namespaces"
  value = {
    system      = kubernetes_namespace.pipe_system.metadata[0].name
    bots        = kubernetes_namespace.pipe_bots.metadata[0].name
    governance  = kubernetes_namespace.pipe_governance.metadata[0].name
    monitoring  = kubernetes_namespace.pipe_monitoring.metadata[0].name
    openbao     = kubernetes_namespace.openbao.metadata[0].name
    zitadel     = kubernetes_namespace.zitadel.metadata[0].name
    zot         = kubernetes_namespace.zot.metadata[0].name
    domains     = [for ns in kubernetes_namespace.domains : ns.metadata[0].name]
  }
}

output "service_accounts" {
  description = "Created service accounts"
  value = {
    bot        = kubernetes_service_account.pipe_bot.metadata[0].name
    governance = kubernetes_service_account.pipe_governance.metadata[0].name
  }
}
