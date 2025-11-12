# ECO Bot Infrastructure - OpenTofu Configuration
# IMPORTANT: This uses OpenTofu, NOT Terraform
# FAGAM-compliant infrastructure provisioning

terraform {
  required_version = ">= 1.6.0"  # OpenTofu version

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }

  # Backend configuration - use local or S3-compatible storage
  backend "s3" {
    # Use MinIO or other S3-compatible storage
    # NOT AWS S3 (FAGAM prohibition)
    endpoint = "https://minio.example.com"
    bucket   = "eco-bots-tfstate"
    key      = "eco/terraform.tfstate"
    region   = "us-east-1"  # Required but ignored for MinIO

    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
    force_path_style            = true
  }
}

# Provider configuration
provider "kubernetes" {
  config_path = "~/.kube/config"
}

# Variables
variable "namespace" {
  description = "Kubernetes namespace for ECO bots"
  type        = string
  default     = "eco-bots"
}

variable "bot_count" {
  description = "Number of ECO bots to deploy"
  type        = number
  default     = 48
}

variable "container_size_limit" {
  description = "Maximum container size in MB"
  type        = number
  default     = 50
}

variable "resource_tier" {
  description = "Resource tier: small, medium, large"
  type        = string
  default     = "medium"

  validation {
    condition     = contains(["small", "medium", "large"], var.resource_tier)
    error_message = "Resource tier must be small, medium, or large."
  }
}

# Resource limits based on tier
locals {
  resource_limits = {
    small = {
      cpu    = "100m"
      memory = "128Mi"
    }
    medium = {
      cpu    = "250m"
      memory = "256Mi"
    }
    large = {
      cpu    = "500m"
      memory = "512Mi"
    }
  }

  current_limits = local.resource_limits[var.resource_tier]
}

# Namespace
resource "kubernetes_namespace" "eco_bots" {
  metadata {
    name = var.namespace

    labels = {
      domain            = "ECO"
      "bsw.domain"      = "ECO"
      "bsw.bot-factory" = "true"
      "bsw.fagam-free"  = "true"
    }

    annotations = {
      "description"           = "ECO domain bots - Infrastructure and operations"
      "bsw.opentofu-managed" = "true"
      "bsw.no-terraform"     = "true"
    }
  }
}

# Resource quota for namespace
resource "kubernetes_resource_quota" "eco_quota" {
  metadata {
    name      = "eco-resource-quota"
    namespace = kubernetes_namespace.eco_bots.metadata[0].name
  }

  spec {
    hard = {
      "requests.cpu"    = "24"      # 48 bots * 0.5 CPU max
      "requests.memory" = "24Gi"    # 48 bots * 512Mi max
      "limits.cpu"      = "48"      # 48 bots * 1 CPU max
      "limits.memory"   = "48Gi"    # 48 bots * 1Gi max
      "pods"            = "100"
      "services"        = "50"
      "persistentvolumeclaims" = "48"
    }
  }
}

# Limit range for containers
resource "kubernetes_limit_range" "eco_limits" {
  metadata {
    name      = "eco-container-limits"
    namespace = kubernetes_namespace.eco_bots.metadata[0].name
  }

  spec {
    limit {
      type = "Container"

      default = {
        cpu    = local.current_limits.cpu
        memory = local.current_limits.memory
      }

      default_request = {
        cpu    = "50m"
        memory = "64Mi"
      }

      max = {
        cpu    = "1"
        memory = "1Gi"
      }

      min = {
        cpu    = "50m"
        memory = "64Mi"
      }
    }
  }
}

# Network policy - allow monitoring
resource "kubernetes_network_policy" "eco_monitoring" {
  metadata {
    name      = "eco-monitoring-policy"
    namespace = kubernetes_namespace.eco_bots.metadata[0].name
  }

  spec {
    pod_selector {
      match_labels = {
        domain = "ECO"
      }
    }

    policy_types = ["Ingress", "Egress"]

    ingress {
      from {
        namespace_selector {
          match_labels = {
            name = "monitoring"
          }
        }
      }

      ports {
        protocol = "TCP"
        port     = "8000"  # Metrics port
      }
    }

    egress {
      # Allow DNS
      to {
        namespace_selector {
          match_labels = {
            name = "kube-system"
          }
        }
      }

      ports {
        protocol = "UDP"
        port     = "53"
      }
    }

    egress {
      # Allow HTTPS
      ports {
        protocol = "TCP"
        port     = "443"
      }
    }
  }
}

# ConfigMap for ECO bots
resource "kubernetes_config_map" "eco_config" {
  metadata {
    name      = "eco-config"
    namespace = kubernetes_namespace.eco_bots.metadata[0].name
  }

  data = {
    "DOCS_REPO_URL"        = "https://github.com/bsw-arch/bsw-arch.git"
    "DOCS_PATH"            = "/opt/documentation/docs"
    "BOT_DOMAIN"           = "ECO"
    "METRICS_PORT"         = "8000"
    "LOG_LEVEL"            = "INFO"
    "FAGAM_CHECK_ENABLED"  = "true"
    "CONTAINER_SIZE_LIMIT" = tostring(var.container_size_limit)
  }
}

# Outputs
output "namespace" {
  description = "ECO bots namespace"
  value       = kubernetes_namespace.eco_bots.metadata[0].name
}

output "resource_limits" {
  description = "Applied resource limits"
  value       = local.current_limits
}

output "quota" {
  description = "Namespace resource quota"
  value       = kubernetes_resource_quota.eco_quota.spec[0].hard
}
