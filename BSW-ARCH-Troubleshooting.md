# BSW-ARCH Troubleshooting & Monitoring Guide

**Document**: BSW-ARCH-Troubleshooting.md
**Version**: v3.0.0
**AppVM**: bsw-arch
**Last Updated**: 2025-09-21 11:45 UTC
**Status**: Production Implementation Complete
**Semantic Version**: v3.0.0 (Major: Production release, Minor: Core features, Patch: Documentation)

## BSW-ARCH Troubleshooting Overview

This comprehensive guide provides step-by-step troubleshooting procedures for the BSW-ARCH Enterprise Architecture AI Factory, covering common issues, monitoring strategies, and recovery procedures.

### BSW-ARCH System Health Indicators
```yaml
🟢 Healthy System:
├── Memory Usage: <60%
├── Swap Usage: <80%
├── Service Response: <100ms average
├── Container Status: All running
└── Service Health: 100% responding

🟡 Warning System:
├── Memory Usage: 60-75%
├── Swap Usage: 80-90%
├── Service Response: 100-500ms
├── Container Issues: 1-2 containers problematic
└── Service Health: 90-99% responding

🔴 Critical System:
├── Memory Usage: >75%
├── Swap Usage: >90%
├── Service Response: >500ms
├── Container Issues: 3+ containers down
└── Service Health: <90% responding
```

## BSW-ARCH Common Issues & Solutions

### Issue 1: Memory-Related Problems

#### Problem: JavaScript Heap Out of Memory
**Symptoms**: Node.js process crashes with heap limit exceeded
**Root Cause**: Large JSON serialization operations exceeding V8 heap limit

**Solution Steps**:
```bash
# 1. Check current memory status
free -h

# 2. Verify Node.js memory limits
echo $NODE_OPTIONS

# 3. If not set, apply BSW-ARCH memory optimization
export NODE_OPTIONS="--max-old-space-size=2048 --optimize-for-size"

# 4. Restart any Node.js processes
pkill -f node && echo "Node.js processes terminated"

# 5. Monitor for stability
tail -f /tmp/bsw-memory-alerts.log
```

#### Problem: Python Service Memory Leak
**Symptoms**: Continuous memory growth in specific service
**Detection**: Service appears repeatedly in memory alerts

**Solution Steps**:
```bash
# 1. Identify leaking service
grep "High service memory" /tmp/bsw-memory-alerts.log | tail -10

# 2. Apply immediate garbage collection
pgrep -f <service-name> | xargs kill -SIGUSR1

# 3. Monitor memory reduction
watch -n 5 "ps aux | grep <service-name> | grep -v grep"

# 4. If leak persists, restart service
pkill -f <service-name>
cd /home/user/Projects/EA/bsw-infrastructure/bsw-infra
python3 bsw-arch/services/<service-name>.py &

# 5. Verify recovery
curl http://localhost:<port>/health
```

#### Problem: High Swap Usage (>90%)
**Symptoms**: System sluggishness, high I/O wait times
**Root Cause**: Memory pressure causing excessive swapping

**Solution Steps**:
```bash
# 1. Check swap usage details
swapon --show
free -h

# 2. Clear system caches
echo 1 > /proc/sys/vm/drop_caches

# 3. Identify memory-heavy processes
ps aux --sort=-%mem | head -20

# 4. Apply container memory limits if not set
bash -c 'for container in $(podman ps --format="{{.Names}}"); do
  podman update --memory=256m $container 2>/dev/null || echo "Failed: $container"
done'

# 5. Start memory enforcement
python3 /home/user/Code/service-memory-enforcer.py &
```

### Issue 2: Service Communication Problems

#### Problem: Service Not Responding
**Symptoms**: HTTP timeouts, connection refused errors
**Detection**: Service health checks failing

**Solution Steps**:
```bash
# 1. Check service status
ps aux | grep -E "(python3.*bsw-arch|podman)"

# 2. Test service connectivity
curl -w "%{http_code}" http://localhost:<port>/health

# 3. Check service logs
journalctl --user -f | grep <service-name>

# 4. Verify port availability
ss -tlnp | grep <port>

# 5. Restart service if needed
pkill -f <service-name>
cd /home/user/Projects/EA/bsw-infrastructure/bsw-infra
python3 bsw-arch/services/<service-name>.py &
```

#### Problem: Slow Service Response (>500ms)
**Symptoms**: API calls timing out, dashboard loading slowly
**Root Cause**: Resource contention or memory pressure

**Solution Steps**:
```bash
# 1. Check system load
top -n 1 | head -5

# 2. Identify resource-heavy services
ps aux --sort=-%cpu | head -10

# 3. Check for memory pressure
cat /proc/meminfo | grep -E "(MemAvailable|SwapFree)"

# 4. Apply service priority adjustment
pgrep -f <slow-service> | xargs renice +5

# 5. Monitor response time improvement
while true; do
  curl -w "Response time: %{time_total}s\n" -o /dev/null -s http://localhost:<port>/health
  sleep 5
done
```

### Issue 3: Container-Related Problems

#### Problem: Container Memory Limit Exceeded
**Symptoms**: Container killed, service unavailable
**Detection**: OOMKilled status in container logs

**Solution Steps**:
```bash
# 1. Check container status
podman ps --all --format "table {{.Names}} {{.Status}}"

# 2. Inspect failed container
podman logs <container-name> | tail -20

# 3. Check current memory limit
podman inspect <container-name> | grep -A5 "Memory"

# 4. Increase memory limit
podman update --memory=<new-limit> <container-name>

# 5. Restart container
podman restart <container-name>

# 6. Monitor stability
podman stats <container-name>
```

#### Problem: Container Port Conflicts
**Symptoms**: Port already in use errors, services unreachable
**Root Cause**: Multiple services trying to bind to same port

**Solution Steps**:
```bash
# 1. Identify port conflicts
ss -tlnp | grep <port>

# 2. Find conflicting processes
lsof -i :<port>

# 3. Stop conflicting services
pkill -f <conflicting-process>

# 4. Restart container with port mapping
podman stop <container-name>
podman start <container-name>

# 5. Verify port binding
curl http://localhost:<port>/health
```

### Issue 4: Cross-Domain Communication Issues

#### Problem: KERAGR Federation Errors
**Symptoms**: Knowledge retrieval failures, domain coordination issues
**Root Cause**: Federation service connectivity problems

**Solution Steps**:
```bash
# 1. Check federation service status
curl http://localhost:3109/health  # Enhanced KERAGR Federation
curl http://localhost:3107/health  # KERAGR Federation Coordinator

# 2. Test domain connectivity
for domain in axis pipe iv; do
  echo "Testing $domain domain:"
  curl http://localhost:${domain}/health
done

# 3. Check federation logs
grep -i "federation" /tmp/bsw-memory-alerts.log

# 4. Restart federation services
pkill -f keragr-federation
cd /home/user/Projects/EA/bsw-infrastructure/bsw-infra
python3 bsw-arch/services/enhanced-keragr-federation.py &
python3 bsw-arch/services/keragr-federation-coordinator.py &

# 5. Verify federation recovery
curl http://localhost:3109/federation/status
```

## BSW-ARCH Monitoring Dashboard

### Real-Time System Monitoring
```bash
# BSW-ARCH System Health Dashboard
#!/bin/bash
echo "=== BSW-ARCH System Health Dashboard ==="
echo "Timestamp: $(date)"
echo ""

# Memory Status
echo "📊 Memory Status:"
free -h | grep -E "(Mem|Swap)"
echo ""

# Service Status
echo "🔧 Service Status:"
curl -s http://localhost:3111/health && echo " ✅ Cross-Domain Coordinator" || echo " ❌ Cross-Domain Coordinator"
curl -s http://localhost:3109/health && echo " ✅ KERAGR Federation" || echo " ❌ KERAGR Federation"
curl -s http://localhost:4600/health && echo " ✅ AI Dashboard" || echo " ❌ AI Dashboard"
echo ""

# Container Status
echo "🐳 Container Status:"
podman ps --format "table {{.Names}} {{.Status}}"
echo ""

# Recent Alerts
echo "🚨 Recent Alerts:"
tail -5 /tmp/bsw-memory-alerts.log
```

### Service Performance Monitoring
```python
# BSW-ARCH Service Performance Monitor
import requests
import time
from datetime import datetime

BSW_ARCH_SERVICES = {
    'Cross-Domain Coordinator': 'http://localhost:3111',
    'KERAGR Federation': 'http://localhost:3109',
    'AI Ecosystem Dashboard': 'http://localhost:4600',
    'AXIS Coordinator': 'http://localhost:4000',
    'PIPE Coordinator': 'http://localhost:5100',
    'IV Coordinator': 'http://localhost:6000'
}

def monitor_services():
    for name, url in BSW_ARCH_SERVICES.items():
        try:
            start_time = time.time()
            response = requests.get(f"{url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000

            status = "✅ HEALTHY" if response.status_code == 200 else "⚠️ WARNING"
            print(f"{status} {name}: {response_time:.1f}ms")
        except Exception as e:
            print(f"❌ FAILED {name}: {str(e)}")

if __name__ == "__main__":
    while True:
        print(f"\n📊 BSW-ARCH Service Monitor - {datetime.now().strftime('%H:%M:%S')}")
        monitor_services()
        time.sleep(30)
```

### Memory Trend Analysis
```bash
# BSW-ARCH Memory Trend Analysis
#!/bin/bash
echo "=== BSW-ARCH Memory Trend Analysis ==="

# Current memory usage
current_mem=$(free | awk '/^Mem:/{printf "%.1f", $3/1024/1024}')
total_mem=$(free | awk '/^Mem:/{printf "%.1f", $2/1024/1024}')
mem_percent=$(echo "scale=1; $current_mem / $total_mem * 100" | bc)

echo "Current Memory: ${current_mem}GB / ${total_mem}GB (${mem_percent}%)"

# Service memory breakdown
echo ""
echo "📊 Service Memory Breakdown:"
ps aux | grep "python3.*bsw-arch/services" | grep -v grep | \
  awk '{print $11 ": " $6/1024 "MB"}' | sort -k2 -nr

# Memory alerts in last hour
echo ""
echo "🚨 Memory Alerts (Last Hour):"
grep "$(date +'%Y-%m-%d %H')" /tmp/bsw-memory-alerts.log | wc -l | \
  xargs echo "Total alerts:"

# Top memory consuming services
echo ""
echo "🔝 Top Memory Services:"
ps aux --sort=-%mem | grep "python3.*bsw-arch" | head -5 | \
  awk '{print $11 ": " $4 "% CPU, " $6/1024 "MB"}'
```

## BSW-ARCH Emergency Procedures

### Emergency Response Playbook

#### EMERGENCY: System Memory Critical (>90%)
```bash
# EMERGENCY RESPONSE: BSW-ARCH Memory Critical
echo "🚨 EMERGENCY: BSW-ARCH Memory Critical Response"

# 1. IMMEDIATE: Clear system caches
echo 1 > /proc/sys/vm/drop_caches
echo "✅ System caches cleared"

# 2. IMMEDIATE: Apply garbage collection to all services
pgrep -f "python3.*bsw-arch" | xargs kill -SIGUSR1
echo "✅ Garbage collection triggered"

# 3. URGENT: Restart high-memory services
pkill -f surgical-precision-monitoring
pkill -f ai-ecosystem-dashboard
echo "✅ High-memory services restarted"

# 4. CRITICAL: Apply emergency container limits
for container in $(podman ps --format="{{.Names}}"); do
  podman update --memory=128m $container 2>/dev/null
done
echo "✅ Emergency container limits applied"

# 5. MONITOR: Start intensive monitoring
python3 /home/user/Code/service-memory-enforcer.py &
echo "✅ Emergency monitoring activated"

echo "🎯 Emergency response complete. Monitor system for 10 minutes."
```

#### EMERGENCY: All Services Down
```bash
# EMERGENCY RESPONSE: BSW-ARCH Service Recovery
echo "🚨 EMERGENCY: BSW-ARCH Service Recovery"

# 1. Check system resources
free -h
echo ""

# 2. Restart core infrastructure
podman restart bsw-grafana bsw-postgresql-pod bsw-prometheus-pod
echo "✅ Core infrastructure restarted"

# 3. Restart domain coordinators
podman restart axis-coordinator pipe-coordinator iv-coordinator
echo "✅ Domain coordinators restarted"

# 4. Restart key services in order
cd /home/user/Projects/EA/bsw-infrastructure/bsw-infra
python3 bsw-arch/services/enhanced-keragr-federation.py &
sleep 10
python3 bsw-arch/services/crewai-domain-coordination.py &
sleep 10
python3 bsw-arch/services/ai-ecosystem-dashboard.py &
echo "✅ Core services restarted"

# 5. Verify recovery
sleep 30
curl http://localhost:3109/health && echo "✅ Federation OK" || echo "❌ Federation FAILED"
curl http://localhost:3110/health && echo "✅ CrewAI OK" || echo "❌ CrewAI FAILED"
curl http://localhost:4600/health && echo "✅ Dashboard OK" || echo "❌ Dashboard FAILED"
```

## BSW-ARCH Preventive Maintenance

### Daily Health Checks
```bash
# BSW-ARCH Daily Health Check Script
#!/bin/bash
echo "=== BSW-ARCH Daily Health Check - $(date) ==="

# Check 1: Memory usage
mem_usage=$(free | awk '/^Mem:/{printf "%.1f", $3/$2 * 100}')
if (( $(echo "$mem_usage > 70" | bc -l) )); then
  echo "⚠️ WARNING: Memory usage high ($mem_usage%)"
else
  echo "✅ Memory usage normal ($mem_usage%)"
fi

# Check 2: Service responsiveness
failed_services=0
for port in 3109 3110 4000 4600 5100 6000; do
  if ! curl -s http://localhost:$port/health > /dev/null; then
    echo "❌ Service on port $port not responding"
    ((failed_services++))
  fi
done

if [ $failed_services -eq 0 ]; then
  echo "✅ All services responding"
else
  echo "⚠️ WARNING: $failed_services services not responding"
fi

# Check 3: Container health
unhealthy_containers=$(podman ps --format="{{.Names}} {{.Status}}" | grep -v "Up" | wc -l)
if [ $unhealthy_containers -eq 0 ]; then
  echo "✅ All containers healthy"
else
  echo "⚠️ WARNING: $unhealthy_containers unhealthy containers"
fi

# Check 4: Recent memory alerts
recent_alerts=$(grep "$(date +'%Y-%m-%d')" /tmp/bsw-memory-alerts.log | wc -l)
if [ $recent_alerts -lt 10 ]; then
  echo "✅ Normal alert volume ($recent_alerts alerts today)"
else
  echo "⚠️ WARNING: High alert volume ($recent_alerts alerts today)"
fi

echo "=== Daily Health Check Complete ==="
```

### Weekly Maintenance Tasks
```bash
# BSW-ARCH Weekly Maintenance
echo "=== BSW-ARCH Weekly Maintenance ==="

# 1. Rotate log files
mv /tmp/bsw-memory-alerts.log /tmp/bsw-memory-alerts-$(date +%Y%m%d).log
touch /tmp/bsw-memory-alerts.log

# 2. Clean up old containers
podman system prune -f

# 3. Update container limits based on usage
echo "📊 Analyzing container memory usage patterns..."
for container in $(podman ps --format="{{.Names}}"); do
  usage=$(podman stats --no-stream $container | awk '{print $4}' | tail -n1)
  echo "$container: $usage"
done

# 4. Backup critical configurations
tar -czf bsw-arch-config-$(date +%Y%m%d).tar.gz \
  /home/user/Code/BSW-ARCH-*.md \
  /home/user/Code/bsw-*.py

echo "✅ Weekly maintenance complete"
```

---

**🎯 BSW-ARCH Troubleshooting: Comprehensive problem resolution and monitoring for the Enterprise Architecture AI Factory, ensuring 24/7 operational excellence.**