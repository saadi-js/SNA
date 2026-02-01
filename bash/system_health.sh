#!/bin/bash
# system_health.sh
# Collects CPU, memory, and disk usage statistics
# Output: JSON format for easy parsing

# CPU Usage (1-minute load average and percentage)
cpu_load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
cpu_cores=$(nproc)
cpu_percent=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')

# Memory Usage
mem_info=$(free -m | grep Mem)
mem_total=$(echo $mem_info | awk '{print $2}')
mem_used=$(echo $mem_info | awk '{print $3}')
mem_free=$(echo $mem_info | awk '{print $4}')
mem_available=$(echo $mem_info | awk '{print $7}')
mem_percent=$(awk "BEGIN {printf \"%.2f\", ($mem_used/$mem_total)*100}")

# Disk Usage (root filesystem)
disk_info=$(df -h / | tail -1)
disk_total=$(echo $disk_info | awk '{print $2}')
disk_used=$(echo $disk_info | awk '{print $3}')
disk_available=$(echo $disk_info | awk '{print $4}')
disk_percent=$(echo $disk_info | awk '{print $5}' | tr -d '%')

# Output as JSON
cat <<EOF
{
  "cpu": {
    "load_1min": $cpu_load,
    "cores": $cpu_cores,
    "usage_percent": $cpu_percent
  },
  "memory": {
    "total_mb": $mem_total,
    "used_mb": $mem_used,
    "free_mb": $mem_free,
    "available_mb": $mem_available,
    "usage_percent": $mem_percent
  },
  "disk": {
    "total": "$disk_total",
    "used": "$disk_used",
    "available": "$disk_available",
    "usage_percent": $disk_percent
  }
}
EOF
