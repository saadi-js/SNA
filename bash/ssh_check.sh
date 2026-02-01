#!/bin/bash
# ssh_check.sh
# Checks SSH configuration for security settings
# Output: JSON format for easy parsing

ssh_config="/etc/ssh/sshd_config"

# Check if SSH config file exists
if [ ! -f "$ssh_config" ]; then
    cat <<EOF
{
  "ssh_config_exists": false,
  "root_login_enabled": "unknown",
  "password_auth_enabled": "unknown",
  "error": "SSH config file not found"
}
EOF
    exit 0
fi

# Check PermitRootLogin setting
# Default is "prohibit-password" which is safer than "yes"
root_login_setting=$(grep -i "^PermitRootLogin" "$ssh_config" 2>/dev/null | tail -1 | awk '{print $2}' | tr -d ' ')
if [ -z "$root_login_setting" ]; then
    root_login_setting="default_prohibit-password"
    root_login_enabled="no"
elif [ "$root_login_setting" = "yes" ]; then
    root_login_enabled="yes"
else
    root_login_enabled="no"
fi

# Check PasswordAuthentication setting
# Default is "yes" on many systems
password_auth_setting=$(grep -i "^PasswordAuthentication" "$ssh_config" 2>/dev/null | tail -1 | awk '{print $2}' | tr -d ' ')
if [ -z "$password_auth_setting" ]; then
    password_auth_setting="default_yes"
    password_auth_enabled="yes"
elif [ "$password_auth_setting" = "yes" ]; then
    password_auth_enabled="yes"
else
    password_auth_enabled="no"
fi

# Check if SSH service is running
ssh_running=$(systemctl is-active sshd 2>/dev/null || systemctl is-active ssh 2>/dev/null || echo "unknown")

# Output as JSON
cat <<EOF
{
  "ssh_config_exists": true,
  "ssh_service_running": "$ssh_running",
  "root_login_enabled": "$root_login_enabled",
  "root_login_setting": "$root_login_setting",
  "password_auth_enabled": "$password_auth_enabled",
  "password_auth_setting": "$password_auth_setting"
}
EOF
