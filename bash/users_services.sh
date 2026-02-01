#!/bin/bash
# users_services.sh
# Collects logged-in users and basic service status
# Output: JSON format for easy parsing

# Logged-in users (excluding system users like daemon, nobody)
logged_users=$(who | awk '{print $1}' | sort -u | grep -vE '^(daemon|nobody|root)$' | tr '\n' ',' | sed 's/,$//')
if [ -z "$logged_users" ]; then
    logged_users="none"
fi

# Count of logged-in users
user_count=$(who 2>/dev/null | wc -l)
user_count=$(echo "$user_count" | tr -d '\n\r ' | head -1)
if [ -z "$user_count" ] || [ "$user_count" = "" ]; then
    user_count=0
fi

# Root login status (check if root is logged in)
root_logged_in=$(who 2>/dev/null | grep -c "^root" 2>/dev/null)
if [ -z "$root_logged_in" ] || [ "$root_logged_in" = "" ]; then
    root_logged_in=0
fi
# Ensure it's a clean number (remove any whitespace/newlines)
root_logged_in=$(echo "$root_logged_in" | tr -d '\n\r ' | head -1)

# Basic running services (systemd)
if command -v systemctl >/dev/null 2>&1; then
    # Get active services (excluding system services)
    active_services=$(systemctl list-units --type=service --state=running --no-pager 2>/dev/null | \
        grep -E '\.service' | \
        awk '{print $1}' | \
        grep -vE '^(systemd|dbus|NetworkManager|systemd-)' | \
        head -20 | \
        tr '\n' ',' | sed 's/,$//')
    
    if [ -z "$active_services" ]; then
        active_services="none"
    fi
    
    # Count total active services
    service_count=$(systemctl list-units --type=service --state=running --no-pager 2>/dev/null | grep -c '\.service' 2>/dev/null || echo "0")
    service_count=$(echo "$service_count" | tr -d '\n\r ' | head -1)
    if [ -z "$service_count" ] || [ "$service_count" = "" ]; then
        service_count=0
    fi
else
    active_services="systemctl_not_available"
    service_count=0
fi

# Output as JSON
cat <<EOF
{
  "users": {
    "logged_in_count": $user_count,
    "logged_in_users": "$logged_users",
    "root_logged_in": $root_logged_in
  },
  "services": {
    "active_count": $service_count,
    "active_services": "$active_services"
  }
}
EOF
