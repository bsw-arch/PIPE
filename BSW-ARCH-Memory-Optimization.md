# BSW-ARCH Memory Optimization Guide

**Document**: BSW-ARCH-Memory-Optimization.md
**Version**: v3.0.0
**AppVM**: bsw-arch
**Last Updated**: 2025-09-21 11:45 UTC
**Status**: Production Implementation Complete
**Semantic Version**: v3.0.0 (Major: Production release, Minor: Core features, Patch: Documentation)

## BSW-ARCH Memory Management Overview

This document provides comprehensive guidance for memory optimization, leak prevention, and performance tuning within the BSW-ARCH Enterprise Architecture AI Factory environment.

### BSW-ARCH Memory Architecture
```
📊 Total System Memory: 7.9GB
├── Available Memory: 3.3GB (optimized)
├── BSW Services: 591.5MB (21 Python services)
├── Container Stack: 2.1GB (13 containers with limits)
├── System Overhead: 1.5GB (OS, Firefox, etc.)
└── Swap Usage: 892MB/1024MB (87% - monitored)
```

## BSW-ARCH Memory Optimization Results (2025-09-20)

### Before Optimization (Crisis State)
- ❌ **JavaScript heap out of memory error** (Node.js crash)
- ❌ **Memory usage**: 5.1GB/7.9GB (64.6% utilization)
- ❌ **Swap pressure**: 95.1% (975MB/1024MB)
- ❌ **Memory leaks**: 3 services with active leaks
- ❌ **Container limits**: 0/13 containers had memory limits
- ❌ **Service memory**: surgical-precision-monitoring 131MB→149MB growth

### After Optimization (Production Ready)
- ✅ **Memory stability**: No crashes, stable operation
- ✅ **Memory usage**: 4.5GB/7.9GB (57% utilization) - **600MB freed**
- ✅ **Swap pressure**: 87.2% (892MB/1024MB) - **83MB freed**
- ✅ **Memory leaks**: Successfully mitigated with automated GC
- ✅ **Container limits**: 13/13 containers with enforced limits
- ✅ **Service monitoring**: Real-time leak detection and prevention

## BSW-ARCH Memory Leak Prevention

### Memory Leak Detection System
**Location**: `/home/user/Code/bsw-memory-monitor.py`

```python
# BSW-ARCH Memory Monitoring Thresholds
MEMORY_THRESHOLD = 75      # Alert at 75% RAM usage
SWAP_THRESHOLD = 80        # Alert at 80% swap usage
SERVICE_THRESHOLD = 100    # Alert if service > 100MB
CHECK_INTERVAL = 30        # Check every 30 seconds
```

### Memory Leak Mitigation Tools
**Location**: `/home/user/Code/memory-leak-mitigation.py`

```python
# BSW-ARCH Leak Detection Parameters
LEAK_THRESHOLD_MB_PER_HOUR = 5.0    # 5MB/hour growth = leak
CRITICAL_MEMORY_LIMIT = 200         # 200MB = critical
MONITORING_INTERVAL = 60            # Check every minute
HISTORY_WINDOW = 30                 # Keep 30 minutes of history
```

### Service Memory Limits (Production)
```yaml
BSW-ARCH Service Memory Limits:
  surgical-precision-monitoring.py: 150MB  # Previously leaked to 149MB
  ai-ecosystem-dashboard.py: 120MB         # Previously leaked to 93MB
  crewai-domain-coordination.py: 100MB     # Previously leaked rapidly
  federated-learning-coordinator.py: 80MB  # Stable service
  keragr-federation-coordinator.py: 60MB   # Core service
  enhanced-keragr-federation.py: 40MB      # Lightweight service
```

## BSW-ARCH Container Memory Limits

### Container Resource Allocation
```yaml
BSW-ARCH Container Memory Limits:
  # Core Monitoring Stack
  bsw-grafana: 512MB              # Monitoring dashboard
  bsw-postgresql-pod: 384MB       # Database services
  bsw-prometheus-pod: 256MB       # Metrics collection

  # Domain Coordinators
  axis-coordinator: 128MB         # AXIS domain coordination
  pipe-coordinator: 128MB         # PIPE domain coordination
  iv-coordinator: 128MB           # IV domain coordination

  # Infrastructure Services
  bsw-arch-vault: 256MB          # Secret management
  bsw-arch-zot-registry: 192MB   # Container registry

  # MinIO Distributed Storage (5-node cluster)
  bsw-arch-minio-node-1: 256MB   # Storage node 1
  bsw-arch-minio-node-2: 256MB   # Storage node 2
  bsw-arch-minio-node-3: 256MB   # Storage node 3
  bsw-arch-minio-node-4: 256MB   # Storage node 4
  bsw-arch-minio-node-5: 256MB   # Storage node 5
```

### Container Limit Enforcement Commands
```bash
# Apply BSW-ARCH container memory limits
for coord in axis-coordinator pipe-coordinator iv-coordinator; do
  podman update --memory=128m $coord
done

for node in bsw-arch-minio-node-{1..5}; do
  podman update --memory=256m $node
done

podman update --memory=512m bsw-grafana
podman update --memory=384m bsw-postgresql-pod
podman update --memory=256m bsw-prometheus-pod bsw-arch-vault
podman update --memory=192m bsw-arch-zot-registry
```

## BSW-ARCH Memory Optimization Techniques

### 1. Garbage Collection Automation
**Manual GC Trigger**:
```bash
# Send garbage collection signal to specific service
kill -SIGUSR1 <service-pid>

# Example: Trigger GC for surgical-precision-monitoring
pgrep -f surgical-precision-monitoring.py | xargs kill -SIGUSR1
```

### 2. Node.js Memory Protection
**Global Configuration**:
```bash
# BSW-ARCH Node.js Memory Limits (in ~/.bashrc)
export NODE_OPTIONS="--max-old-space-size=2048 --optimize-for-size"

# Prevents JavaScript heap out of memory errors
# Limits heap to 2GB with memory optimization
```

### 3. Python Memory Optimization
**Service-Level Optimization**:
```python
# BSW-ARCH Python Memory Configuration
import gc
gc.set_threshold(700, 10, 10)  # Aggressive garbage collection

# Memory-optimized dictionary for service data
class MemoryOptimizedDict(dict):
    def __init__(self, max_size=1000):
        super().__init__()
        self.max_size = max_size

    def _cleanup_old_entries(self):
        # Remove 20% of oldest entries when at capacity
        items_to_remove = int(len(self) * 0.2)
        # ... cleanup logic
```

### 4. Service Memory Enforcement
**Automatic Enforcement**:
```python
# BSW-ARCH Service Memory Enforcer
def enforce_service_limit(pid, service_name, current_memory):
    limit = SERVICE_LIMITS.get(service_name, 200)

    if current_memory > limit:
        # Apply graduated enforcement
        os.kill(pid, signal.SIGUSR1)  # Trigger GC

        if current_memory > limit * 1.5:
            os.setpriority(os.PRIO_PROCESS, pid, 10)  # Lower priority

    return enforcement_result
```

## BSW-ARCH Memory Monitoring Dashboard

### Real-Time Monitoring Commands
```bash
# BSW-ARCH Memory Status Check
free -h | grep -E "(Mem|Swap)"

# BSW-ARCH Service Memory Usage
ps aux | grep "python3.*bsw-arch/services" | awk '{print $11, $6/1024 "MB"}'

# BSW-ARCH Container Memory Usage
podman stats --no-stream --format "{{.Name}}: {{.MemUsage}}"

# BSW-ARCH Memory Alert Log
tail -f /tmp/bsw-memory-alerts.log
```

### Memory Performance Metrics
```bash
# BSW-ARCH Memory Efficiency Calculation
echo "scale=2; $(free | awk '/^Mem:/{print $3}') / $(free | awk '/^Mem:/{print $2}') * 100" | bc
# Target: <60% sustained memory usage

# BSW-ARCH Service Efficiency Score
python3 -c "
total_services = 21
total_memory_mb = 591.5
baseline_per_service = 20
efficiency = (baseline_per_service * total_services) / total_memory_mb * 100
print(f'Service Efficiency: {efficiency:.1f}%')
"
```

## BSW-ARCH Memory Troubleshooting

### Common Memory Issues

#### Issue 1: High Swap Usage (>90%)
**Symptoms**: System sluggishness, high I/O wait
**Solution**:
```bash
# BSW-ARCH Swap Pressure Relief
echo 1 > /proc/sys/vm/drop_caches  # Clear page cache
python3 /home/user/Code/memory-leak-mitigation.py &  # Start enforcer
```

#### Issue 2: Service Memory Leak
**Symptoms**: Continuous memory growth in specific service
**Solution**:
```bash
# BSW-ARCH Memory Leak Response
pgrep -f <service-name> | xargs kill -SIGUSR1  # Trigger GC
python3 /home/user/Code/service-memory-enforcer.py &  # Auto-enforcement
```

#### Issue 3: Container Memory Pressure
**Symptoms**: Container OOM kills, service disruption
**Solution**:
```bash
# BSW-ARCH Container Memory Recovery
podman update --memory=<new-limit> <container-name>
podman restart <container-name>
```

### BSW-ARCH Memory Alert Codes
```
🧹 GC: Garbage collection triggered
🔧 ENFORCEMENT: Memory limit enforcement applied
🚨 CRITICAL: Service over critical memory threshold
⚠️  WARNING: Approaching memory limits
✅ OK: Memory usage within normal range
📊 MONITOR: Regular monitoring checkpoint
```

## BSW-ARCH Memory Optimization Best Practices

### 1. Proactive Monitoring
- Monitor memory usage every 30 seconds
- Set alerts at 75% RAM, 80% swap
- Track service memory growth rates

### 2. Container Resource Management
- Always set memory limits on containers
- Use graduated limits based on service criticality
- Monitor container memory efficiency

### 3. Service Lifecycle Management
- Implement automatic garbage collection
- Set service memory thresholds
- Use memory-optimized data structures

### 4. System-Level Optimization
- Configure aggressive GC for Python services
- Set Node.js heap limits
- Implement swap pressure monitoring

## BSW-ARCH Memory Optimization Maintenance

### Daily Tasks
```bash
# BSW-ARCH Daily Memory Check
/home/user/Code/bsw-memory-monitor.py --daily-report

# Check for new memory leaks
grep "LEAK DETECTED" /tmp/bsw-memory-alerts.log | tail -10

# Verify container limits
podman inspect --format="{{.Name}}: {{.HostConfig.Memory}}" $(podman ps -q)
```

### Weekly Tasks
```bash
# BSW-ARCH Weekly Memory Analysis
python3 -c "
import psutil
memory = psutil.virtual_memory()
swap = psutil.swap_memory()
print(f'Weekly Memory Report:')
print(f'RAM Usage: {memory.percent}%')
print(f'Swap Usage: {swap.percent}%')
print(f'Available: {memory.available/1024**3:.1f}GB')
"
```

### Monthly Tasks
- Review service memory trends
- Optimize container resource allocation
- Update memory limits based on usage patterns
- Performance tuning and optimization review

---

**🎯 BSW-ARCH Memory Optimization: Ensuring stable, efficient operation of the Enterprise Architecture AI Factory through proactive memory management and leak prevention.**