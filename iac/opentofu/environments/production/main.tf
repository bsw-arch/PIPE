# OpenTofu Production Environment - PIPE Task Bot
# ================================================
# Complete production infrastructure with K3s + OpenBao + Registry

terraform {
  required_version = ">= 1.6.0"

  backend "local" {
    path = "terraform.tfstate"
  }

  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "cluster_name" {
  description = "K3s cluster name"
  type        = string
  default     = "axis-prod"
}

variable "node_count" {
  description = "Number of cluster nodes"
  type        = number
  default     = 3
}

variable "registry_url" {
  description = "Container registry URL"
  type        = string
  default     = "localhost:5000"
}

variable "openbao_addr" {
  description = "OpenBao server address"
  type        = string
  default     = "http://localhost:8200"
}

# Module: K3s Cluster
module "k3s_cluster" {
  source = "../../modules/k3s-cluster"

  cluster_name  = var.cluster_name
  node_count    = var.node_count
  enable_traefik = false
  enable_servicelb = true

  registry_config = {
    mirrors = {
      (var.registry_url) = {
        endpoint = ["http://${var.registry_url}"]
      }
    }
  }
}

# Deploy Helm chart
resource "null_resource" "deploy_helm_chart" {
  depends_on = [module.k3s_cluster]

  provisioner "local-exec" {
    command = <<-EOT
      export KUBECONFIG=${module.k3s_cluster.kubeconfig_path}

      # Add helm repo (if needed)
      # helm repo add axis https://helm.axis-bots.local

      # Install/upgrade chart
      helm upgrade --install pipe-build-bot \
        ../../../helm/charts/pipe-build-bot \
        --namespace ${module.k3s_cluster.namespace} \
        --create-namespace \
        --values ../../../helm/values/production.yaml \
        --set global.registry=${var.registry_url} \
        --set openbao.address=${var.openbao_addr} \
        --wait \
        --timeout 5m

      echo "Helm chart deployed successfully"
    EOT
  }

  triggers = {
    cluster_name = var.cluster_name
    timestamp    = timestamp()
  }
}

# Verify deployment
resource "null_resource" "verify_deployment" {
  depends_on = [null_resource.deploy_helm_chart]

  provisioner "local-exec" {
    command = <<-EOT
      export KUBECONFIG=${module.k3s_cluster.kubeconfig_path}

      echo "Waiting for pods to be ready..."
      kubectl wait --for=condition=ready pod \
        -l app.kubernetes.io/name=pipe-build-bot \
        -n ${module.k3s_cluster.namespace} \
        --timeout=300s

      echo ""
      echo "Deployment Status:"
      kubectl get pods -n ${module.k3s_cluster.namespace}

      echo ""
      echo "Services:"
      kubectl get svc -n ${module.k3s_cluster.namespace}

      echo ""
      echo "Container Sizes:"
      kubectl get pods -n ${module.k3s_cluster.namespace} -o json | \
        jq -r '.items[].spec.containers[] | "\(.name): \(.image)"'
    EOT
  }
}

# Outputs
output "cluster_name" {
  description = "K3s cluster name"
  value       = module.k3s_cluster.cluster_name
}

output "kubeconfig_path" {
  description = "Path to kubeconfig"
  value       = module.k3s_cluster.kubeconfig_path
}

output "namespace" {
  description = "Kubernetes namespace"
  value       = module.k3s_cluster.namespace
}

output "cluster_info" {
  description = "Cluster information"
  value       = module.k3s_cluster.cluster_info
}

output "deployment_commands" {
  description = "Useful kubectl commands"
  value = <<-EOT
    # Set kubeconfig
    export KUBECONFIG=${module.k3s_cluster.kubeconfig_path}

    # View pods
    kubectl get pods -n ${module.k3s_cluster.namespace}

    # View logs
    kubectl logs -n ${module.k3s_cluster.namespace} -l app.kubernetes.io/name=pipe-build-bot

    # Port forward
    kubectl port-forward -n ${module.k3s_cluster.namespace} svc/pipe-build-bot 8080:8080

    # Execute shell
    kubectl exec -n ${module.k3s_cluster.namespace} -it deployment/pipe-build-bot-task-bot -- sh

    # View secrets (from OpenBao)
    kubectl get secrets -n ${module.k3s_cluster.namespace}
  EOT
}
