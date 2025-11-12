# OpenTofu Module: K3s Cluster for PIPE Task Bot
# ================================================
# Provisions lightweight Kubernetes cluster with K3s

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

variable "cluster_name" {
  description = "Name of the K3s cluster"
  type        = string
  default     = "axis-k3s"
}

variable "node_count" {
  description = "Number of K3s nodes"
  type        = number
  default     = 1
}

variable "network_cidr" {
  description = "Network CIDR for the cluster"
  type        = string
  default     = "10.42.0.0/16"
}

variable "service_cidr" {
  description = "Service CIDR for the cluster"
  type        = string
  default     = "10.43.0.0/16"
}

variable "enable_traefik" {
  description = "Enable Traefik ingress controller"
  type        = bool
  default     = false
}

variable "enable_servicelb" {
  description = "Enable ServiceLB"
  type        = bool
  default     = true
}

variable "registry_config" {
  description = "Private registry configuration"
  type = object({
    mirrors = map(object({
      endpoint = list(string)
    }))
  })
  default = {
    mirrors = {
      "localhost:5000" = {
        endpoint = ["http://localhost:5000"]
      }
    }
  }
}

# K3s installation script
locals {
  k3s_install_script = <<-EOT
    #!/bin/bash
    set -e

    echo "Installing K3s cluster: ${var.cluster_name}"

    # Install K3s
    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server \
      --cluster-cidr=${var.network_cidr} \
      --service-cidr=${var.service_cidr} \
      ${var.enable_traefik ? "" : "--disable=traefik"} \
      ${var.enable_servicelb ? "" : "--disable=servicelb"} \
      --write-kubeconfig-mode=644" sh -

    # Wait for K3s to be ready
    echo "Waiting for K3s to be ready..."
    timeout 120 bash -c 'until kubectl get nodes; do sleep 5; done'

    # Configure private registry
    cat > /etc/rancher/k3s/registries.yaml <<EOF
    mirrors:
      ${jsonencode(var.registry_config.mirrors)}
    EOF

    # Restart K3s to apply registry config
    systemctl restart k3s

    echo "K3s cluster ${var.cluster_name} is ready!"
  EOT
}

# Install K3s
resource "null_resource" "k3s_install" {
  provisioner "local-exec" {
    command = local.k3s_install_script
    interpreter = ["/bin/bash", "-c"]
  }

  triggers = {
    cluster_name = var.cluster_name
    node_count   = var.node_count
  }
}

# Export kubeconfig
resource "null_resource" "export_kubeconfig" {
  depends_on = [null_resource.k3s_install]

  provisioner "local-exec" {
    command = <<-EOT
      mkdir -p ~/.kube
      sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config-${var.cluster_name}
      sudo chown $(id -u):$(id -g) ~/.kube/config-${var.cluster_name}
      echo "Kubeconfig exported to ~/.kube/config-${var.cluster_name}"
    EOT
  }
}

# Create axis-bots namespace
resource "null_resource" "create_namespace" {
  depends_on = [null_resource.export_kubeconfig]

  provisioner "local-exec" {
    command = <<-EOT
      export KUBECONFIG=~/.kube/config-${var.cluster_name}
      kubectl create namespace axis-bots --dry-run=client -o yaml | kubectl apply -f -
      kubectl label namespace axis-bots name=axis-bots --overwrite
    EOT
  }
}

# Configure OpenBao for Kubernetes auth
resource "null_resource" "configure_openbao_k8s" {
  depends_on = [null_resource.create_namespace]

  provisioner "local-exec" {
    command = <<-EOT
      export KUBECONFIG=~/.kube/config-${var.cluster_name}

      # Enable Kubernetes auth in OpenBao
      openbao auth enable kubernetes || true

      # Configure Kubernetes auth
      K8S_HOST=$(kubectl config view --raw --minify --flatten -o jsonpath='{.clusters[].cluster.server}')
      K8S_CA_CERT=$(kubectl config view --raw --minify --flatten -o jsonpath='{.clusters[].cluster.certificate-authority-data}' | base64 -d)

      openbao write auth/kubernetes/config \
        kubernetes_host="$K8S_HOST" \
        kubernetes_ca_cert="$K8S_CA_CERT"

      # Create role for PIPE Task Bot
      openbao write auth/kubernetes/role/pipe-task-bot \
        bound_service_account_names=pipe-task-bot \
        bound_service_account_namespaces=axis-bots \
        policies=pipe-task-bot \
        ttl=24h

      echo "OpenBao Kubernetes auth configured"
    EOT
  }
}

# Outputs
output "cluster_name" {
  description = "Name of the K3s cluster"
  value       = var.cluster_name
}

output "kubeconfig_path" {
  description = "Path to kubeconfig file"
  value       = "~/.kube/config-${var.cluster_name}"
}

output "cluster_info" {
  description = "Cluster information"
  value = {
    network_cidr = var.network_cidr
    service_cidr = var.service_cidr
    node_count   = var.node_count
  }
}

output "namespace" {
  description = "Kubernetes namespace for PIPE bots"
  value       = "axis-bots"
}
