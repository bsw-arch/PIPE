#!/bin/bash
# Deploy Zot container registry
# OCI-native registry for PIPE images

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-zot-registry}"
STORAGE_CLASS="${STORAGE_CLASS:-standard}"
STORAGE_SIZE="${STORAGE_SIZE:-100Gi}"

log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

# Create Zot configuration
create_zot_config() {
    log_info "Creating Zot configuration..."

    kubectl create configmap zot-config \
        --namespace="$NAMESPACE" \
        --from-file=config.json=/dev/stdin \
        --dry-run=client -o yaml <<'EOF' | kubectl apply -f -
{
  "distSpecVersion": "1.1.0",
  "storage": {
    "rootDirectory": "/var/lib/zot",
    "dedupe": true,
    "gc": true,
    "gcDelay": "1h",
    "gcInterval": "24h"
  },
  "http": {
    "address": "0.0.0.0",
    "port": "5000",
    "tls": {
      "cert": "/etc/zot/tls/tls.crt",
      "key": "/etc/zot/tls/tls.key"
    }
  },
  "log": {
    "level": "info",
    "output": "/var/log/zot/zot.log"
  },
  "extensions": {
    "search": {
      "enable": true
    },
    "scrub": {
      "enable": true,
      "interval": "24h"
    },
    "metrics": {
      "enable": true,
      "prometheus": {
        "path": "/metrics"
      }
    },
    "sync": {
      "enable": false
    },
    "ui": {
      "enable": true
    }
  }
}
EOF

    log_info "✓ Zot configuration created"
}

# Deploy Zot registry
deploy_zot() {
    log_info "Deploying Zot registry..."

    kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: zot-storage
  namespace: $NAMESPACE
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: $STORAGE_CLASS
  resources:
    requests:
      storage: $STORAGE_SIZE
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zot-registry
  namespace: $NAMESPACE
  labels:
    app: zot-registry
spec:
  replicas: 2
  selector:
    matchLabels:
      app: zot-registry
  template:
    metadata:
      labels:
        app: zot-registry
    spec:
      containers:
      - name: zot
        image: ghcr.io/project-zot/zot:latest
        ports:
        - containerPort: 5000
          name: registry
        - containerPort: 9090
          name: metrics
        volumeMounts:
        - name: zot-storage
          mountPath: /var/lib/zot
        - name: zot-config
          mountPath: /etc/zot/config.json
          subPath: config.json
        - name: zot-tls
          mountPath: /etc/zot/tls
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /v2/
            port: 5000
            scheme: HTTPS
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /v2/
            port: 5000
            scheme: HTTPS
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: zot-storage
        persistentVolumeClaim:
          claimName: zot-storage
      - name: zot-config
        configMap:
          name: zot-config
      - name: zot-tls
        secret:
          secretName: zot-tls
---
apiVersion: v1
kind: Service
metadata:
  name: zot-registry
  namespace: $NAMESPACE
  labels:
    app: zot-registry
spec:
  type: ClusterIP
  ports:
  - port: 5000
    targetPort: 5000
    protocol: TCP
    name: registry
  - port: 9090
    targetPort: 9090
    protocol: TCP
    name: metrics
  selector:
    app: zot-registry
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: zot-registry
  namespace: $NAMESPACE
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - zot.pipe.local
    secretName: zot-tls-ingress
  rules:
  - host: zot.pipe.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: zot-registry
            port:
              number: 5000
EOF

    log_info "✓ Zot registry deployed"
}

# Main
main() {
    log_info "Deploying Zot container registry..."

    # Create namespace if not exists
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    create_zot_config
    deploy_zot

    log_info "✓ Zot deployment complete"
    log_info "Registry available at: https://zot.pipe.local"
}

main "$@"
