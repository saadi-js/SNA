#!/bin/bash
# log_extract.sh
# Extracts authentication and system error logs
# Prefers journalctl (systemd) if available, falls back to traditional log files
# Output: Clean text format for pattern matching

echo "=== AUTHENTICATION LOG ==="

# Try journalctl first (systemd systems)
if command -v journalctl >/dev/null 2>&1; then
    # Extract SSH-related authentication logs
    journalctl -u ssh -n 100 --no-pager 2>/dev/null | grep -i "auth\|password\|login\|failed" || \
    journalctl _SYSTEMD_UNIT=ssh.service -n 100 --no-pager 2>/dev/null || \
    journalctl -p err..warning -n 100 --no-pager 2>/dev/null | grep -i "auth\|ssh" || true
else
    # Fallback to traditional log files
    auth_log="/var/log/auth.log"
    if [ ! -f "$auth_log" ]; then
        auth_log="/var/log/secure"
    fi
    
    if [ -f "$auth_log" ] && [ -r "$auth_log" ]; then
        tail -n 200 "$auth_log" 2>/dev/null || echo "Could not read auth log"
    else
        echo "Authentication log not found or not readable"
    fi
fi

echo ""
echo "=== SYSTEM ERROR LOG ==="

# Try journalctl first (systemd systems)
if command -v journalctl >/dev/null 2>&1; then
    # Extract error-level messages with actual message text
    journalctl -p err -n 50 --no-pager 2>/dev/null | grep -v "^--" | \
    awk '{$1=$2=$3=$4=$5=""; print substr($0,6)}' | sed 's/^[[:space:]]*//' || \
    journalctl -p warning -n 50 --no-pager 2>/dev/null | grep -v "^--" | \
    awk '{$1=$2=$3=$4=$5=""; print substr($0,6)}' | sed 's/^[[:space:]]*//' || true
else
    # Fallback to traditional log files
    sys_log="/var/log/syslog"
    if [ ! -f "$sys_log" ]; then
        sys_log="/var/log/messages"
    fi
    
    if [ -f "$sys_log" ] && [ -r "$sys_log" ]; then
        grep -i "error\|fail\|critical\|warning" "$sys_log" 2>/dev/null | tail -n 100 || \
        tail -n 100 "$sys_log" 2>/dev/null || echo "Could not read system log"
    else
        echo "System log not found or not readable"
    fi
fi
