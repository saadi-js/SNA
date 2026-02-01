#!/usr/bin/env python3
"""
Log Intelligence Module
Analyzes system and authentication logs for patterns.
"""

import re
from typing import Dict, Any, List
from ..utils.command_runner import CommandRunner


class LogAnalyzer:
    """Analyzes logs for security and system issues."""
    
    def __init__(self, command_runner: CommandRunner):
        self.runner = command_runner
    
    def collect_logs(self) -> str:
        """Collect authentication and system logs."""
        output = self.runner.run_bash_script("log_extract.sh")
        return output or ""
    
    def analyze(self, log_text: str) -> Dict[str, Any]:
        """Analyze logs for patterns and return structured data."""
        if not log_text:
            return {
                "failed_ssh_logins": 0,
                "authentication_failures": 0,
                "service_errors": [],
                "auth_warnings": 0,
                "permission_denied": 0,
                "segfaults": 0,
                "kernel_errors": 0,
                "sudo_misuse": 0,
                "service_restarts": 0
            }
        
        analysis = {
            "failed_ssh_logins": 0,
            "authentication_failures": 0,
            "service_errors": [],
            "auth_warnings": 0,
            "permission_denied": 0,
            "segfaults": 0,
            "kernel_errors": 0,
            "sudo_misuse": 0,
            "service_restarts": 0
        }
        
        known_services = [
            "apache2", "nginx", "mysql", "postgresql", "systemd", "ssh", "sshd",
            "cron", "rsyslog", "network", "dbus", "polkit", "systemd-logind"
        ]
        
        lines = log_text.split('\n')
        auth_section = False
        sys_section = False
        
        for line in lines:
            if not line.strip() or line.strip().startswith("==="):
                continue
            
            if "AUTHENTICATION LOG" in line:
                auth_section = True
                sys_section = False
                continue
            elif "SYSTEM ERROR LOG" in line:
                auth_section = False
                sys_section = True
                continue
            
            line_lower = line.lower()
            
            # Authentication patterns
            if auth_section:
                if "failed password" in line_lower or "authentication failure" in line_lower:
                    analysis["failed_ssh_logins"] += 1
                    analysis["authentication_failures"] += 1
                if "permission denied" in line_lower:
                    analysis["permission_denied"] += 1
                if "warning" in line_lower and ("auth" in line_lower or "ssh" in line_lower):
                    analysis["auth_warnings"] += 1
                if "sudo" in line_lower and ("failed" in line_lower or "incorrect" in line_lower):
                    analysis["sudo_misuse"] += 1
            
            # System patterns
            if sys_section:
                if "permission denied" in line_lower:
                    analysis["permission_denied"] += 1
                if "segfault" in line_lower or "segmentation fault" in line_lower:
                    analysis["segfaults"] += 1
                if "kernel" in line_lower and ("error" in line_lower or "fail" in line_lower):
                    analysis["kernel_errors"] += 1
                if "restart" in line_lower or "stopped" in line_lower:
                    if any(svc in line_lower for svc in known_services):
                        analysis["service_restarts"] += 1
                
                # Extract service names
                service_match = re.search(r'([a-z][a-z0-9-]+)\.service[:\s]', line_lower)
                if service_match:
                    service = service_match.group(1)
                    if service and service not in analysis["service_errors"]:
                        analysis["service_errors"].append(service)
                
                for service_name in known_services:
                    if service_name in line_lower and ("error" in line_lower or "fail" in line_lower):
                        if service_name not in analysis["service_errors"]:
                            analysis["service_errors"].append(service_name)
        
        analysis["service_errors"] = sorted(list(set(analysis["service_errors"])))
        return analysis
    
    def analyze_findings(self, log_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert log analysis into security/system findings."""
        findings = []
        
        failed_logins = log_analysis.get("failed_ssh_logins", 0)
        if failed_logins > 20:
            findings.append({
                "severity": "HIGH",
                "title": "Potential Brute Force Attack",
                "description": f"High number of failed SSH login attempts ({failed_logins}) detected.",
                "recommendation": "Review /var/log/auth.log and consider implementing Fail2Ban"
            })
        elif failed_logins > 10:
            findings.append({
                "severity": "MEDIUM",
                "title": "Authentication Failures Detected",
                "description": f"Multiple failed SSH login attempts ({failed_logins}) detected.",
                "recommendation": "Monitor authentication logs and review access patterns"
            })
        
        service_errors = log_analysis.get("service_errors", [])
        if len(service_errors) >= 1:
            service_list = ", ".join(service_errors[:5])
            findings.append({
                "severity": "MEDIUM",
                "title": "Service Stability Risk",
                "description": f"Service-related errors detected: {service_list}",
                "recommendation": f"Review service logs for {service_list} and check service status"
            })
        
        if log_analysis.get("kernel_errors", 0) >= 1:
            findings.append({
                "severity": "HIGH",
                "title": "Kernel-Level Issues Detected",
                "description": "Kernel errors detected in system logs.",
                "recommendation": "Investigate kernel errors immediately - may indicate hardware or driver issues"
            })
        
        if log_analysis.get("segfaults", 0) > 0:
            findings.append({
                "severity": "HIGH",
                "title": "Application Crashes Detected",
                "description": f"Segmentation faults detected ({log_analysis.get('segfaults', 0)}).",
                "recommendation": "Review application logs and check for memory corruption or compatibility issues"
            })
        
        if log_analysis.get("sudo_misuse", 0) > 5:
            findings.append({
                "severity": "MEDIUM",
                "title": "Sudo Misuse Detected",
                "description": f"Multiple failed sudo attempts ({log_analysis.get('sudo_misuse', 0)}) detected.",
                "recommendation": "Review sudo access patterns and user permissions"
            })
        
        return findings
