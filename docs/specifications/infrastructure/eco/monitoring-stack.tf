# ECO Monitoring Stack - OpenTofu Configuration
# Prometheus, Grafana, Loki, AlertManager

# Monitoring namespace
resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"

    labels = {
      name              = "monitoring"
      "bsw.monitoring"  = "true"
      "bsw.fagam-free"  = "true"
    }
  }
}

# Prometheus ConfigMap
resource "kubernetes_config_map" "prometheus_config" {
  metadata {
    name      = "prometheus-config"
    namespace = kubernetes_namespace.monitoring.metadata[0].name
  }

  data = {
    "prometheus.yml" = <<-EOT
      global:
        scrape_interval: 15s
        evaluation_interval: 15s
        external_labels:
          cluster: 'bsw-arch-factory'
          environment: 'production'

      # Alerting configuration
      alerting:
        alertmanagers:
          - static_configs:
              - targets:
                  - alertmanager:9093

      # Load rules
      rule_files:
        - /etc/prometheus/rules/*.yml

      # Scrape configurations
      scrape_configs:
        # ECO Bots
        - job_name: 'eco-bots'
          kubernetes_sd_configs:
            - role: pod
              namespaces:
                names:
                  - eco-bots
          relabel_configs:
            - source_labels: [__meta_kubernetes_pod_label_domain]
              regex: ECO
              action: keep
            - source_labels: [__meta_kubernetes_pod_name]
              target_label: instance
            - source_labels: [__meta_kubernetes_pod_label_bsw_bot_name]
              target_label: bot_name
          scrape_interval: 15s
          scrape_timeout: 10s

        # AXIS Bots
        - job_name: 'axis-bots'
          kubernetes_sd_configs:
            - role: pod
              namespaces:
                names:
                  - axis-bots
          relabel_configs:
            - source_labels: [__meta_kubernetes_pod_label_domain]
              regex: AXIS
              action: keep
          scrape_interval: 30s

        # PIPE Bots
        - job_name: 'pipe-bots'
          kubernetes_sd_configs:
            - role: pod
              namespaces:
                names:
                  - pipe-bots
          relabel_configs:
            - source_labels: [__meta_kubernetes_pod_label_domain]
              regex: PIPE
              action: keep
          scrape_interval: 30s

        # IV Bots
        - job_name: 'iv-bots'
          kubernetes_sd_configs:
            - role: pod
              namespaces:
                names:
                  - iv-bots
          relabel_configs:
            - source_labels: [__meta_kubernetes_pod_label_domain]
              regex: IV
              action: keep
          scrape_interval: 30s

        # Kubernetes components
        - job_name: 'kubernetes-nodes'
          kubernetes_sd_configs:
            - role: node
          relabel_configs:
            - action: labelmap
              regex: __meta_kubernetes_node_label_(.+)

        - job_name: 'kubernetes-pods'
          kubernetes_sd_configs:
            - role: pod
          relabel_configs:
            - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
              regex: true
              action: keep
    EOT

    "alert_rules.yml" = <<-EOT
      groups:
        - name: eco_bots_alerts
          interval: 30s
          rules:
            # High CPU usage
            - alert: EcoBotHighCPU
              expr: container_cpu_usage_seconds_total{namespace="eco-bots"} > 0.8
              for: 5m
              labels:
                severity: warning
                domain: ECO
              annotations:
                summary: "ECO bot {{ $labels.pod }} high CPU usage"
                description: "CPU usage is {{ $value }}% for 5 minutes"

            # High memory usage
            - alert: EcoBotHighMemory
              expr: container_memory_usage_bytes{namespace="eco-bots"} / container_spec_memory_limit_bytes{namespace="eco-bots"} > 0.9
              for: 5m
              labels:
                severity: warning
                domain: ECO
              annotations:
                summary: "ECO bot {{ $labels.pod }} high memory usage"
                description: "Memory usage is {{ $value | humanizePercentage }} of limit"

            # Pod restart
            - alert: EcoBotRestarting
              expr: rate(kube_pod_container_status_restarts_total{namespace="eco-bots"}[15m]) > 0
              for: 5m
              labels:
                severity: critical
                domain: ECO
              annotations:
                summary: "ECO bot {{ $labels.pod }} restarting"
                description: "Pod has restarted {{ $value }} times in 15 minutes"

            # Container size check
            - alert: EcoBotContainerTooLarge
              expr: container_image_size_bytes{namespace="eco-bots"} > 52428800  # 50MB
              for: 1m
              labels:
                severity: warning
                domain: ECO
              annotations:
                summary: "ECO bot {{ $labels.pod }} container exceeds 50MB"
                description: "Container size is {{ $value | humanize }}B (limit: 50MB)"

            # Error rate
            - alert: EcoBotHighErrorRate
              expr: rate(bot_errors_total{namespace="eco-bots"}[5m]) > 0.05
              for: 2m
              labels:
                severity: critical
                domain: ECO
              annotations:
                summary: "ECO bot {{ $labels.pod }} high error rate"
                description: "Error rate is {{ $value | humanizePercentage }}"
    EOT
  }
}

# Prometheus Deployment
resource "kubernetes_deployment" "prometheus" {
  metadata {
    name      = "prometheus"
    namespace = kubernetes_namespace.monitoring.metadata[0].name

    labels = {
      app = "prometheus"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "prometheus"
      }
    }

    template {
      metadata {
        labels = {
          app = "prometheus"
        }
      }

      spec {
        service_account_name = "prometheus"

        container {
          name  = "prometheus"
          image = "prom/prometheus:v2.47.0"

          args = [
            "--config.file=/etc/prometheus/prometheus.yml",
            "--storage.tsdb.path=/prometheus",
            "--web.console.libraries=/usr/share/prometheus/console_libraries",
            "--web.console.templates=/usr/share/prometheus/consoles",
            "--web.enable-lifecycle",
          ]

          port {
            container_port = 9090
            name           = "web"
          }

          volume_mount {
            name       = "prometheus-config"
            mount_path = "/etc/prometheus"
          }

          volume_mount {
            name       = "prometheus-storage"
            mount_path = "/prometheus"
          }

          resources {
            requests = {
              cpu    = "500m"
              memory = "512Mi"
            }
            limits = {
              cpu    = "1"
              memory = "1Gi"
            }
          }
        }

        volume {
          name = "prometheus-config"

          config_map {
            name = kubernetes_config_map.prometheus_config.metadata[0].name
          }
        }

        volume {
          name = "prometheus-storage"

          persistent_volume_claim {
            claim_name = "prometheus-pvc"
          }
        }
      }
    }
  }
}

# Prometheus Service
resource "kubernetes_service" "prometheus" {
  metadata {
    name      = "prometheus"
    namespace = kubernetes_namespace.monitoring.metadata[0].name

    labels = {
      app = "prometheus"
    }
  }

  spec {
    selector = {
      app = "prometheus"
    }

    port {
      name        = "web"
      port        = 9090
      target_port = 9090
    }

    type = "ClusterIP"
  }
}

# Grafana ConfigMap
resource "kubernetes_config_map" "grafana_datasources" {
  metadata {
    name      = "grafana-datasources"
    namespace = kubernetes_namespace.monitoring.metadata[0].name
  }

  data = {
    "datasources.yaml" = <<-EOT
      apiVersion: 1

      datasources:
        - name: Prometheus
          type: prometheus
          access: proxy
          url: http://prometheus:9090
          isDefault: true
          editable: false

        - name: Loki
          type: loki
          access: proxy
          url: http://loki:3100
          editable: false
    EOT
  }
}

# Grafana Deployment
resource "kubernetes_deployment" "grafana" {
  metadata {
    name      = "grafana"
    namespace = kubernetes_namespace.monitoring.metadata[0].name

    labels = {
      app = "grafana"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "grafana"
      }
    }

    template {
      metadata {
        labels = {
          app = "grafana"
        }
      }

      spec {
        container {
          name  = "grafana"
          image = "grafana/grafana:10.1.0"

          port {
            container_port = 3000
            name           = "web"
          }

          env {
            name  = "GF_SECURITY_ADMIN_PASSWORD"
            value = "admin"  # Change in production
          }

          env {
            name  = "GF_INSTALL_PLUGINS"
            value = "grafana-piechart-panel"
          }

          volume_mount {
            name       = "grafana-datasources"
            mount_path = "/etc/grafana/provisioning/datasources"
          }

          resources {
            requests = {
              cpu    = "250m"
              memory = "256Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
          }
        }

        volume {
          name = "grafana-datasources"

          config_map {
            name = kubernetes_config_map.grafana_datasources.metadata[0].name
          }
        }
      }
    }
  }
}

# Grafana Service
resource "kubernetes_service" "grafana" {
  metadata {
    name      = "grafana"
    namespace = kubernetes_namespace.monitoring.metadata[0].name

    labels = {
      app = "grafana"
    }
  }

  spec {
    selector = {
      app = "grafana"
    }

    port {
      name        = "web"
      port        = 3000
      target_port = 3000
    }

    type = "LoadBalancer"
  }
}

# Outputs
output "prometheus_service" {
  description = "Prometheus service endpoint"
  value       = "${kubernetes_service.prometheus.metadata[0].name}.${kubernetes_namespace.monitoring.metadata[0].name}.svc.cluster.local:9090"
}

output "grafana_service" {
  description = "Grafana service endpoint"
  value       = "${kubernetes_service.grafana.metadata[0].name}.${kubernetes_namespace.monitoring.metadata[0].name}.svc.cluster.local:3000"
}
