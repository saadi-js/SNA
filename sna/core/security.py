#!/usr/bin/env python3
"""
Security Module
Collects and analyzes security configuration.
"""

import json
import sys
from typing import Dict, Any, List
from ..utils.command_runner import CommandRunner


class SecurityCollector:
    """Collects security configuration data."""
    
    def __init__(self, command_runner: CommandRunner):
        self.runner = command_runner
    
    def collect_ssh_config(self) -> Dict[str, Any]:
        """Collect SSH configuration security checks."""
        output = self.runner.run_bash_script("ssh_check.sh")
        if not output:
            return {}
        
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            print(f"Error parsing SSH config JSON: {e}", file=sys.stderr)
            return {}
    
    def analyze_ssh_risks(self, ssh_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze SSH configuration for security risks."""
        findings = []
        
        if ssh_config.get("root_login_enabled") == "yes":
            findings.append({
                "severity": "HIGH",
                "title": "SSH Root Login Enabled",
                "description": "Root login via SSH is enabled. This is a significant security risk.",
                "recommendation": "Disable root SSH login by setting 'PermitRootLogin no' in /etc/ssh/sshd_config"
            })
        
        if ssh_config.get("password_auth_enabled") == "yes":
            findings.append({
                "severity": "MEDIUM",
                "title": "SSH Password Authentication Enabled",
                "description": "Password authentication is enabled. Key-based authentication is more secure.",
                "recommendation": "Consider disabling password authentication and using SSH keys only"
            })
        
        return findings
