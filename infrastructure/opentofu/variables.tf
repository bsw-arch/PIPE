# OpenTofu Variables for PIPE Infrastructure

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "log_level" {
  description = "Default log level for PIPE components"
  type        = string
  default     = "INFO"

  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR"], var.log_level)
    error_message = "Log level must be DEBUG, INFO, WARNING, or ERROR."
  }
}

variable "resource_quota_cpu" {
  description = "CPU resource quota for PIPE bots namespace"
  type        = string
  default     = "10"
}

variable "resource_quota_memory" {
  description = "Memory resource quota for PIPE bots namespace"
  type        = string
  default     = "20Gi"
}

variable "resource_quota_pods" {
  description = "Pod count quota for PIPE bots namespace"
  type        = string
  default     = "50"
}

variable "openbao_enabled" {
  description = "Enable OpenBao secrets management"
  type        = bool
  default     = true
}

variable "zitadel_enabled" {
  description = "Enable Zitadel IAM"
  type        = bool
  default     = true
}

variable "zot_enabled" {
  description = "Enable Zot container registry"
  type        = bool
  default     = true
}

variable "cilium_enabled" {
  description = "Enable Cilium CNI and network policies"
  type        = bool
  default     = true
}

variable "cosign_enforce" {
  description = "Enforce Cosign signature verification"
  type        = bool
  default     = true
}

variable "backup_enabled" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "backup_s3_bucket" {
  description = "S3 bucket for backups"
  type        = string
  default     = "pipe-backups"
}

variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
}

variable "monitoring_retention_days" {
  description = "Metrics retention period in days"
  type        = number
  default     = 15
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
