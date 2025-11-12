# BSW Infrastructure CI/CD Pipeline

## Overview
This document describes the CI/CD pipeline configuration for BSW Infrastructure.

## Components

### Woodpecker CI Pipeline
- **Location:** `.woodpecker.yml`
- **Triggers:** Push to main/develop, Pull Requests
- **Stages:**
  1. Security Scan
  2. Infrastructure Validation
  3. Container Build
  4. Deployment Test
  5. Compliance Check
  6. Backup Test
  7. Environment Deployment
  8. Notification

### ArgoCD Applications
- **Location:** `argocd/`
- **Applications:**
  - `bsw-infrastructure`: Main infrastructure platform
  - `bsw-monitoring`: Observability stack
  - `bsw-security`: Security scanning
  - `bsw-backup`: Data protection

### Kubernetes Manifests
- **Location:** `kubernetes/`
- **Components:**
  - Monitoring dashboard deployment
  - Security scanner deployment
  - Backup system deployment
  - Network policies and RBAC

## Deployment Flow

```
Code Push → Woodpecker CI → Container Build → ArgoCD → Kubernetes → Production
```

## Usage

1. **Development Flow:**
   ```bash
   git checkout develop
   # Make changes
   git commit -m "feat: description"
   git push origin develop
   # CI/CD pipeline triggers automatically
   ```

2. **Production Flow:**
   ```bash
   git checkout main
   git merge develop
   git push origin main
   # Production deployment triggers
   ```

## Monitoring

- Pipeline status: Woodpecker CI dashboard
- Deployment status: ArgoCD dashboard
- Application health: Kubernetes dashboard

