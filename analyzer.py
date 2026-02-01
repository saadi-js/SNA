#!/usr/bin/env python3
"""
AI-Assisted Linux Server Health & Log Analyzer
Main analyzer script that orchestrates data collection and analysis.
"""

import json
import subprocess
import sys
import os
import re
import argparse
import platform
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Import AI engine
try:
    from ai_engine import AIEngine
except ImportError:
    AIEngine = None
    print("Warning: ai_engine.py not found. AI recommendations will be disabled.", file=sys.stderr)


class SystemAnalyzer:
    """Main analyzer class that collects and analyzes system data."""
    
    def __init__(self, bash_dir: str = "bash"):
        self.bash_dir = Path(bash_dir)
        self.data = {}
        self.analysis = {}
        self.is_windows = platform.system() == "Windows"
        self.bash_cmd = self._find_bash_command()
        
        # Check if we're on Windows without bash/WSL
        if self.is_windows and not self.bash_cmd:
            print("\n" + "="*60, file=sys.stderr)
            print("WARNING: This tool is designed for Linux systems.", file=sys.stderr)
            print("="*60, file=sys.stderr)
            print("\nYou are running on Windows. This tool requires:", file=sys.stderr)
            print("  1. A Linux system (Ubuntu/Debian recommended), OR", file=sys.stderr)
            print("  2. Windows Subsystem for Linux (WSL) installed", file=sys.stderr)
            print("\nTo use WSL:", file=sys.stderr)
            print("  1. Install WSL: wsl --install", file=sys.stderr)
            print("  2. Run this tool from within WSL:", file=sys.stderr)
            print("     wsl", file=sys.stderr)
            print("     cd /mnt/c/Users/user/SNA", file=sys.stderr)
            print("     python analyzer.py", file=sys.stderr)
            print("\n" + "="*60 + "\n", file=sys.stderr)
    
    def _find_bash_command(self) -> Optional[str]:
        """Find the bash command to use for executing scripts."""
        if not self.is_windows:
            # On Linux/Unix, bash should be available
            if shutil.which("bash"):
                return "bash"
            return None
        
        # On Windows, try to find bash
        # Try WSL bash first
        if shutil.which("wsl"):
            return "wsl"
        # Try Git Bash
        if shutil.which("bash"):
            return "bash"
        # Try common Git Bash paths
        git_bash_paths = [
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
        ]
        for path in git_bash_paths:
            if os.path.exists(path):
                return path
        
        return None
        
    def run_bash_script(self, script_name: str) -> Optional[str]:
        """Execute a bash script and return its output."""
        script_path = self.bash_dir / script_name
        if not script_path.exists():
            print(f"Error: Script {script_name} not found at {script_path}", file=sys.stderr)
            return None
        
        # Check if we have bash available
        if not self.bash_cmd:
            print(f"Error: Cannot execute {script_name} - bash not found.", file=sys.stderr)
            print("This tool requires a Linux system or WSL on Windows.", file=sys.stderr)
            return None
        
        try:
            # Build command based on platform
            if self.is_windows:
                if self.bash_cmd == "wsl":
                    # Use WSL to run the script
                    # Convert Windows path to WSL path
                    wsl_path = str(script_path).replace("\\", "/")
                    # Convert C:\Users\... to /mnt/c/Users/...
                    if wsl_path.startswith("C:"):
                        wsl_path = "/mnt/c" + wsl_path[2:]
                    elif wsl_path.startswith("c:"):
                        wsl_path = "/mnt/c" + wsl_path[2:]
                    
                    cmd = ["wsl", "bash", wsl_path]
                else:
                    # Use Git Bash or other bash
                    cmd = [self.bash_cmd, str(script_path)]
            else:
                # On Linux, make executable and run directly
                try:
                    os.chmod(script_path, 0o755)
                except (OSError, PermissionError):
                    # If chmod fails, try running with bash explicitly
                    pass
                cmd = [self.bash_cmd, str(script_path)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False
            )
            if result.returncode != 0:
                print(f"Warning: {script_name} returned non-zero exit code", file=sys.stderr)
                if result.stderr:
                    print(f"Error: {result.stderr}", file=sys.stderr)
            return result.stdout
        except subprocess.TimeoutExpired:
            print(f"Error: {script_name} timed out", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error running {script_name}: {e}", file=sys.stderr)
            return None
    
    def collect_system_health(self) -> Dict[str, Any]:
        """
        Collect CPU, memory, and disk usage.
        
        This method preserves the original CPU monitoring logic while expanding
        to include memory and disk metrics. The CPU collection uses the same
        approach as the original script (top command parsing) but is now executed
        via a bash script for better modularity and consistency.
        """
        output = self.run_bash_script("system_health.sh")
        if not output:
            return {}
        
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            print(f"Error parsing system health JSON: {e}", file=sys.stderr)
            return {}
    
    def collect_users_services(self) -> Dict[str, Any]:
        """Collect logged-in users and service information."""
        output = self.run_bash_script("users_services.sh")
        if not output:
            return {}
        
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            print(f"Error parsing users/services JSON: {e}", file=sys.stderr)
            return {}
    
    def collect_ssh_config(self) -> Dict[str, Any]:
        """Collect SSH configuration security checks."""
        output = self.run_bash_script("ssh_check.sh")
        if not output:
            return {}
        
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            print(f"Error parsing SSH config JSON: {e}", file=sys.stderr)
            return {}
    
    def collect_logs(self) -> str:
        """Collect authentication and system logs."""
        output = self.run_bash_script("log_extract.sh")
        return output or ""
    
    def analyze_logs(self, log_text: str) -> Dict[str, Any]:
        """
        Analyze logs for patterns without sending raw logs to LLM.
        Returns a summarized JSON structure with detected issues.
        """
        if not log_text:
            return {
                "failed_ssh_logins": 0,
                "authentication_failures": 0,
                "service_errors": [],
                "auth_warnings": 0,
                "permission_denied": 0,
                "segfaults": 0,
                "kernel_errors": 0
            }
        
        analysis = {
            "failed_ssh_logins": 0,
            "authentication_failures": 0,
            "service_errors": [],
            "auth_warnings": 0,
            "permission_denied": 0,
            "segfaults": 0,
            "kernel_errors": 0
        }
        
        # Common service names to look for (avoid false positives)
        known_services = [
            "apache2", "nginx", "mysql", "postgresql", "systemd", "ssh", "sshd",
            "cron", "rsyslog", "network", "dbus", "polkit", "systemd-logind"
        ]
        
        lines = log_text.split('\n')
        auth_section = False
        sys_section = False
        
        for line in lines:
            # Skip empty lines and section headers
            if not line.strip() or line.strip().startswith("==="):
                continue
                
            # Detect section boundaries
            if "AUTHENTICATION LOG" in line:
                auth_section = True
                sys_section = False
                continue
            elif "SYSTEM ERROR LOG" in line:
                auth_section = False
                sys_section = True
                continue
            
            line_lower = line.lower()
            
            # Authentication log patterns
            if auth_section:
                if "failed password" in line_lower or "authentication failure" in line_lower:
                    analysis["failed_ssh_logins"] += 1
                    analysis["authentication_failures"] += 1
                if "permission denied" in line_lower:
                    analysis["permission_denied"] += 1
                if "warning" in line_lower and ("auth" in line_lower or "ssh" in line_lower):
                    analysis["auth_warnings"] += 1
            
            # System log patterns
            if sys_section:
                if "permission denied" in line_lower:
                    analysis["permission_denied"] += 1
                if "segfault" in line_lower or "segmentation fault" in line_lower:
                    analysis["segfaults"] += 1
                
                # Detect kernel errors
                if "kernel" in line_lower and ("error" in line_lower or "fail" in line_lower):
                    analysis["kernel_errors"] += 1
                
                # Extract service names from error messages (improved pattern matching)
                # Look for patterns like "service_name: error" or "error in service_name"
                # Avoid numeric IDs and systemd unit IDs
                
                # Pattern 1: service.service: message
                service_match = re.search(r'([a-z][a-z0-9-]+)\.service[:\s]', line_lower)
                if service_match:
                    service = service_match.group(1)
                    if service and service not in analysis["service_errors"]:
                        analysis["service_errors"].append(service)
                
                # Pattern 2: service_name error or error in service_name
                for service_name in known_services:
                    if service_name in line_lower and ("error" in line_lower or "fail" in line_lower or "critical" in line_lower):
                        if service_name not in analysis["service_errors"]:
                            analysis["service_errors"].append(service_name)
                
                # Pattern 3: Generic service name extraction (avoid IDs)
                # Match words that look like service names (not numbers, not IDs like "17t10")
                if "error" in line_lower or "fail" in line_lower:
                    # Extract potential service names (words before/after error keywords)
                    words = re.findall(r'\b([a-z][a-z0-9-]{2,})\b', line_lower)
                    for word in words:
                        # Skip common non-service words and numeric IDs
                        if (word not in ["error", "failed", "failure", "system", "log", "message", 
                                         "the", "and", "for", "with", "from", "this", "that"] and
                            not word.isdigit() and
                            len(word) > 3 and
                            word not in analysis["service_errors"]):
                            # Check if it's a known service or looks like one
                            if any(svc in word or word in svc for svc in known_services):
                                analysis["service_errors"].append(word)
                                break  # Only add one per line
        
        # Remove duplicates and sort
        analysis["service_errors"] = sorted(list(set(analysis["service_errors"])))
        
        return analysis
    
    def rule_based_analysis(self) -> Dict[str, Any]:
        """
        Perform rule-based analysis on collected data.
        Returns severity levels: LOW, MEDIUM, HIGH, CRITICAL
        """
        findings = {
            "health": [],
            "security": [],
            "overall_severity": "LOW"
        }
        
        # Health analysis
        health = self.data.get("health", {})
        
        # CPU analysis (preserved from original CPU monitor with enhanced thresholds)
        # Original logic: if cpu > 80: WARNING
        # Enhanced: Added CRITICAL (90%) and MEDIUM (60%) thresholds
        cpu_usage = health.get("cpu", {}).get("usage_percent", 0)
        if cpu_usage > 90:
            findings["health"].append({
                "metric": "CPU Usage",
                "value": f"{cpu_usage:.1f}%",
                "severity": "CRITICAL",
                "message": f"CPU usage is critically high at {cpu_usage:.1f}%"
            })
        elif cpu_usage > 80:
            findings["health"].append({
                "metric": "CPU Usage",
                "value": f"{cpu_usage:.1f}%",
                "severity": "HIGH",
                "message": f"CPU usage is high at {cpu_usage:.1f}%"
            })
        elif cpu_usage > 60:
            findings["health"].append({
                "metric": "CPU Usage",
                "value": f"{cpu_usage:.1f}%",
                "severity": "MEDIUM",
                "message": f"CPU usage is moderately elevated at {cpu_usage:.1f}%"
            })
        
        # Memory analysis
        mem_usage = health.get("memory", {}).get("usage_percent", 0)
        if mem_usage > 90:
            findings["health"].append({
                "metric": "Memory Usage",
                "value": f"{mem_usage:.1f}%",
                "severity": "CRITICAL",
                "message": f"Memory usage is critically high at {mem_usage:.1f}%"
            })
        elif mem_usage > 80:
            findings["health"].append({
                "metric": "Memory Usage",
                "value": f"{mem_usage:.1f}%",
                "severity": "HIGH",
                "message": f"Memory usage is high at {mem_usage:.1f}%"
            })
        elif mem_usage > 75:
            findings["health"].append({
                "metric": "Memory Usage",
                "value": f"{mem_usage:.1f}%",
                "severity": "MEDIUM",
                "message": f"Memory usage is moderately elevated at {mem_usage:.1f}%"
            })
        
        # Disk analysis
        disk_usage = health.get("disk", {}).get("usage_percent", 0)
        if disk_usage > 90:
            findings["health"].append({
                "metric": "Disk Usage",
                "value": f"{disk_usage}%",
                "severity": "CRITICAL",
                "message": f"Disk usage is critically high at {disk_usage}%"
            })
        elif disk_usage > 85:
            findings["health"].append({
                "metric": "Disk Usage",
                "value": f"{disk_usage}%",
                "severity": "HIGH",
                "message": f"Disk usage is high at {disk_usage}%"
            })
        elif disk_usage > 75:
            findings["health"].append({
                "metric": "Disk Usage",
                "value": f"{disk_usage}%",
                "severity": "MEDIUM",
                "message": f"Disk usage is moderately elevated at {disk_usage}%"
            })
        
        # Security analysis
        ssh_config = self.data.get("ssh_config", {})
        
        # SSH root login check
        if ssh_config.get("root_login_enabled") == "yes":
            findings["security"].append({
                "metric": "SSH Root Login",
                "value": "Enabled",
                "severity": "HIGH",
                "message": "Root login via SSH is enabled. This is a security risk."
            })
        
        # SSH password authentication check
        if ssh_config.get("password_auth_enabled") == "yes":
            findings["security"].append({
                "metric": "SSH Password Auth",
                "value": "Enabled",
                "severity": "MEDIUM",
                "message": "Password authentication is enabled. Consider using key-based authentication."
            })
        
        # Log analysis - promote log findings to severity levels
        log_analysis = self.data.get("log_analysis", {})
        
        # Failed SSH login attempts
        failed_logins = log_analysis.get("failed_ssh_logins", 0)
        if failed_logins > 20:
            findings["security"].append({
                "metric": "Failed SSH Logins",
                "value": str(failed_logins),
                "severity": "HIGH",
                "title": "Potential Brute Force Attack",
                "message": f"High number of failed SSH login attempts ({failed_logins}). Possible brute force attack.",
                "description": "Multiple failed authentication attempts detected in system logs. This may indicate an automated attack attempting to gain unauthorized access."
            })
        elif failed_logins > 10:
            findings["security"].append({
                "metric": "Failed SSH Logins",
                "value": str(failed_logins),
                "severity": "MEDIUM",
                "title": "Authentication Failures Detected",
                "message": f"Multiple failed SSH login attempts ({failed_logins}) detected.",
                "description": "Repeated authentication failures suggest potential security concerns or misconfigured access attempts."
            })
        
        # Service errors - promote to findings
        service_errors = log_analysis.get("service_errors", [])
        if len(service_errors) >= 1:
            service_list = ", ".join(service_errors[:5])
            findings["health"].append({
                "metric": "Service Stability Risk",
                "value": service_list,
                "severity": "MEDIUM",
                "title": "Service Stability Risk",
                "message": f"Service-related errors detected in system logs.",
                "description": f"Multiple service-related error entries detected for: {service_list}. This indicates possible misconfiguration or unstable background services that may lead to service interruptions."
            })
        
        # Kernel errors
        kernel_errors = log_analysis.get("kernel_errors", 0)
        if kernel_errors >= 1:
            findings["health"].append({
                "metric": "Kernel Errors",
                "value": str(kernel_errors),
                "severity": "HIGH",
                "title": "Kernel-Level Issues Detected",
                "message": f"Kernel errors detected ({kernel_errors}) in system logs.",
                "description": "Kernel-level errors indicate serious system issues that may affect stability and require immediate investigation."
            })
        
        # Segfaults
        segfaults = log_analysis.get("segfaults", 0)
        if segfaults > 0:
            findings["health"].append({
                "metric": "Segmentation Faults",
                "value": str(segfaults),
                "severity": "HIGH",
                "title": "Application Crashes Detected",
                "message": f"Segmentation faults detected ({segfaults}).",
                "description": "Segmentation faults indicate application crashes, which may point to software bugs, memory corruption, or compatibility issues."
            })
        
        # Authentication warnings
        auth_warnings = log_analysis.get("auth_warnings", 0)
        if auth_warnings > 5:
            findings["security"].append({
                "metric": "Authentication Warnings",
                "value": str(auth_warnings),
                "severity": "MEDIUM",
                "title": "Authentication System Warnings",
                "message": f"Multiple authentication warnings ({auth_warnings}) detected.",
                "description": "Repeated authentication warnings may indicate configuration issues or unusual authentication patterns that warrant review."
            })
        
        # Determine overall severity
        severities = []
        for finding in findings["health"] + findings["security"]:
            severities.append(finding["severity"])
        
        if "CRITICAL" in severities:
            findings["overall_severity"] = "CRITICAL"
        elif "HIGH" in severities:
            findings["overall_severity"] = "HIGH"
        elif "MEDIUM" in severities:
            findings["overall_severity"] = "MEDIUM"
        else:
            findings["overall_severity"] = "LOW"
        
        return findings
    
    def collect_all_data(self, include_health: bool = True, include_logs: bool = True):
        """Collect all system data."""
        print("Collecting system data...", file=sys.stderr)
        print(f"Platform: {platform.system()}", file=sys.stderr)
        print(f"Bash command: {self.bash_cmd}", file=sys.stderr)
        
        if include_health:
            self.data["health"] = self.collect_system_health()
            self.data["users_services"] = self.collect_users_services()
        
        self.data["ssh_config"] = self.collect_ssh_config()
        
        if include_logs:
            log_text = self.collect_logs()
            self.data["log_text"] = log_text
            self.data["log_analysis"] = self.analyze_logs(log_text)
        
        # Perform rule-based analysis
        self.analysis = self.rule_based_analysis()
    
    def print_summary(self, ai_analysis: Optional[str] = None):
        """Print a clean CLI summary with expanded sections."""
        print("\n" + "="*60)
        print("Linux Server Health & Security Analysis")
        print("="*60)
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Overall Severity: {self.analysis.get('overall_severity', 'UNKNOWN')}")
        print()
        
        # Health summary with status indicators
        health = self.data.get("health", {})
        if health:
            cpu = health.get("cpu", {})
            mem = health.get("memory", {})
            disk = health.get("disk", {})
            
            cpu_pct = cpu.get('usage_percent', 0)
            mem_pct = mem.get('usage_percent', 0)
            disk_pct = disk.get('usage_percent', 0)
            
            # Determine status indicators
            cpu_status = "[OK]" if cpu_pct < 60 else "[MEDIUM]" if cpu_pct < 80 else "[HIGH]" if cpu_pct < 90 else "[CRITICAL]"
            mem_status = "[OK]" if mem_pct < 75 else "[MEDIUM]" if mem_pct < 80 else "[HIGH]" if mem_pct < 90 else "[CRITICAL]"
            disk_status = "[OK]" if disk_pct < 75 else "[MEDIUM]" if disk_pct < 85 else "[HIGH]" if disk_pct < 90 else "[CRITICAL]"
            
            print("System Health:")
            print(f"  CPU Usage:    {cpu_pct:.1f}% {cpu_status}")
            print(f"  Memory Usage: {mem_pct:.1f}% {mem_status}")
            print(f"  Disk Usage:   {disk_pct}% {disk_status}")
            print()
        
        # Security summary
        ssh = self.data.get("ssh_config", {})
        if ssh:
            print("Security Configuration:")
            root_status = "Enabled [WARNING]" if ssh.get('root_login_enabled') == 'yes' else "Disabled [OK]"
            pass_status = "Enabled [WARNING]" if ssh.get('password_auth_enabled') == 'yes' else "Disabled [OK]"
            print(f"  SSH Root Login:            {root_status}")
            print(f"  SSH Password Authentication: {pass_status}")
            print()
        
        # Log Intelligence section (NEW)
        log_analysis = self.data.get("log_analysis", {})
        if log_analysis:
            print("Log Intelligence:")
            failed_logins = log_analysis.get("failed_ssh_logins", 0)
            auth_warnings = log_analysis.get("auth_warnings", 0)
            service_errors = log_analysis.get("service_errors", [])
            kernel_errors = log_analysis.get("kernel_errors", 0)
            
            # Status indicators for log metrics
            login_status = "[OK]" if failed_logins == 0 else "[LOW]" if failed_logins < 10 else "[MEDIUM]" if failed_logins < 20 else "[HIGH]"
            auth_warn_status = "[OK]" if auth_warnings == 0 else "[LOW]" if auth_warnings < 5 else "[MEDIUM]"
            service_status = "[OK]" if len(service_errors) == 0 else "[MEDIUM]"
            kernel_status = "[OK]" if kernel_errors == 0 else "[HIGH]"
            
            print(f"  Authentication Failures: {failed_logins} {login_status}")
            if auth_warnings > 0:
                print(f"  Authentication Warnings: {auth_warnings} {auth_warn_status}")
            if len(service_errors) > 0:
                service_list = ", ".join(service_errors[:5])
                print(f"  Service Errors: {service_list} {service_status}")
            if kernel_errors > 0:
                print(f"  Kernel Errors: {kernel_errors} {kernel_status}")
            if failed_logins == 0 and auth_warnings == 0 and len(service_errors) == 0 and kernel_errors == 0:
                print("  No significant log anomalies detected [OK]")
            print()
        
        # Expanded Findings section (multi-line format)
        findings = self.analysis.get("health", []) + self.analysis.get("security", [])
        if findings:
            print("Key Findings:")
            for finding in findings[:10]:  # Limit to top 10
                severity_label = {
                    "CRITICAL": "[CRITICAL]",
                    "HIGH": "[HIGH]",
                    "MEDIUM": "[MEDIUM]",
                    "LOW": "[LOW]"
                }.get(finding.get("severity", "LOW"), "[INFO]")
                
                # Use title if available, otherwise use metric
                title = finding.get("title") or finding.get("metric", "Unknown")
                
                print(f"  {severity_label} {title}")
                
                # Print description if available (multi-line)
                if finding.get("description"):
                    # Split description into bullet points if it contains multiple sentences
                    desc = finding.get("description")
                    # Add bullet point formatting
                    print(f"    • {desc}")
                elif finding.get("message"):
                    print(f"    • {finding['message']}")
                print()
        else:
            print("Key Findings:")
            print("  No critical issues detected. System appears healthy.")
            print()
        
        # AI Analysis section (always shown)
        print("AI Analysis:")
        if ai_analysis:
            # Print AI analysis with proper formatting
            lines = ai_analysis.strip().split('\n')
            for line in lines:
                if line.strip():
                    print(f"  {line.strip()}")
        else:
            # Generate fallback analysis
            fallback_text = self._generate_fallback_analysis()
            print(f"  {fallback_text}")
        print()
        
        print("="*60)
    
    def _generate_fallback_analysis(self) -> str:
        """Generate deterministic fallback analysis text when AI is unavailable."""
        health = self.data.get("health", {})
        log_analysis = self.data.get("log_analysis", {})
        findings = self.analysis.get("health", []) + self.analysis.get("security", [])
        
        cpu_pct = health.get("cpu", {}).get("usage_percent", 0)
        mem_pct = health.get("memory", {}).get("usage_percent", 0)
        disk_pct = health.get("disk", {}).get("usage_percent", 0)
        service_errors = log_analysis.get("service_errors", [])
        failed_logins = log_analysis.get("failed_ssh_logins", 0)
        
        # Build analysis text
        parts = []
        
        # Resource health
        if cpu_pct < 60 and mem_pct < 75 and disk_pct < 75:
            parts.append("The server shows healthy resource utilization")
        elif cpu_pct > 80 or mem_pct > 80 or disk_pct > 85:
            parts.append("The server shows elevated resource usage that requires attention")
        else:
            parts.append("The server shows acceptable resource utilization")
        
        # Security
        if len(findings) == 0 or not any(f.get("severity") in ["HIGH", "CRITICAL"] for f in findings if f.get("metric", "").startswith("SSH")):
            parts.append("with no critical security misconfigurations")
        else:
            parts.append("but security configuration issues were detected")
        
        # Log findings
        if len(service_errors) > 0:
            parts.append(f". However, system logs reveal service-related errors ({', '.join(service_errors[:3])}) that may indicate configuration issues or unstable background processes")
        elif failed_logins > 10:
            parts.append(f". Multiple failed authentication attempts ({failed_logins}) were detected and should be investigated")
        elif len(findings) == 0:
            parts.append(". No significant anomalies were detected in system logs")
        else:
            parts.append(". Review the findings above for potential issues")
        
        return " ".join(parts) + "."
    
    def generate_markdown_report(self, ai_recommendations: Optional[str] = None) -> str:
        """Generate a markdown report."""
        report = []
        report.append("# Linux Server Health & Security Analysis Report\n")
        report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Overall Severity:** {self.analysis.get('overall_severity', 'UNKNOWN')}\n")
        report.append("---\n")
        
        # System Health Section
        report.append("## System Health\n")
        health = self.data.get("health", {})
        if health:
            cpu = health.get("cpu", {})
            mem = health.get("memory", {})
            disk = health.get("disk", {})
            
            report.append("### Resource Usage\n")
            report.append(f"- **CPU Usage:** {cpu.get('usage_percent', 0):.1f}% (Load Average: {cpu.get('load_1min', 0):.2f}, Cores: {cpu.get('cores', 'N/A')})")
            report.append(f"- **Memory Usage:** {mem.get('usage_percent', 0):.1f}% ({mem.get('used_mb', 0)} MB / {mem.get('total_mb', 0)} MB)")
            report.append(f"- **Disk Usage:** {disk.get('usage_percent', 0)}% ({disk.get('used', 'N/A')} / {disk.get('total', 'N/A')})")
            report.append("")
        
        # Users & Services Section
        report.append("## Users & Services\n")
        users_services = self.data.get("users_services", {})
        if users_services:
            users = users_services.get("users", {})
            services = users_services.get("services", {})
            
            report.append(f"- **Logged-in Users:** {users.get('logged_in_count', 0)}")
            report.append(f"- **Active Services:** {services.get('active_count', 0)}")
            if users.get("logged_in_users") and users.get("logged_in_users") != "none":
                report.append(f"- **User List:** {users.get('logged_in_users')}")
            report.append("")
        
        # Security Findings Section
        report.append("## Security Findings\n")
        ssh = self.data.get("ssh_config", {})
        if ssh:
            report.append("### SSH Configuration\n")
            report.append(f"- **Root Login Enabled:** {ssh.get('root_login_enabled', 'unknown')}")
            report.append(f"- **Password Authentication:** {ssh.get('password_auth_enabled', 'unknown')}")
            report.append("")
        
        # Findings
        findings = self.analysis.get("health", []) + self.analysis.get("security", [])
        if findings:
            report.append("### Issues Detected\n")
            for finding in findings:
                report.append(f"#### {finding['metric']} - {finding['severity']}")
                report.append(f"- **Value:** {finding['value']}")
                report.append(f"- **Message:** {finding['message']}")
                report.append("")
        else:
            report.append("No security issues detected.\n")
        
        # Log Analysis Section
        log_analysis = self.data.get("log_analysis", {})
        if log_analysis:
            report.append("## Log Analysis\n")
            report.append("### Summary\n")
            report.append(f"- **Failed SSH Logins:** {log_analysis.get('failed_ssh_logins', 0)}")
            report.append(f"- **Authentication Failures:** {log_analysis.get('authentication_failures', 0)}")
            report.append(f"- **Permission Denied Events:** {log_analysis.get('permission_denied', 0)}")
            report.append(f"- **Segmentation Faults:** {log_analysis.get('segfaults', 0)}")
            if log_analysis.get("service_errors"):
                report.append(f"- **Services with Errors:** {', '.join(log_analysis['service_errors'][:10])}")
            report.append("")
        
        # AI Recommendations Section
        if ai_recommendations:
            report.append("## AI Recommendations\n")
            report.append(ai_recommendations)
            report.append("")
        
        report.append("---\n")
        report.append("*Report generated by AI-Assisted Linux Server Health & Log Analyzer*\n")
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="AI-Assisted Linux Server Health & Log Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Display terminal summary only"
    )
    parser.add_argument(
        "--full-report",
        action="store_true",
        help="Generate markdown report (report.md)"
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Include log analysis"
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Include health analysis (CPU, memory, disk)"
    )
    
    args = parser.parse_args()
    
    # Default behavior: include everything
    include_health = args.health if args.health else True
    include_logs = args.logs if args.logs else True
    
    # Initialize analyzer
    analyzer = SystemAnalyzer()
    
    # Check if we can proceed (have bash available)
    if analyzer.is_windows and not analyzer.bash_cmd:
        print("\nCannot proceed: bash/WSL not available on Windows.", file=sys.stderr)
        print("Please install WSL or run this tool on a Linux system.\n", file=sys.stderr)
        sys.exit(1)
    
    # Collect data
    try:
        analyzer.collect_all_data(include_health=include_health, include_logs=include_logs)
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError during data collection: {e}", file=sys.stderr)
        import traceback
        print("\nFull error traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    
    # Get AI analysis (always attempt, fallback if unavailable)
    ai_analysis = None
    if AIEngine:
        try:
            ai_engine = AIEngine()
            ai_analysis = ai_engine.generate_recommendations(analyzer.data, analyzer.analysis)
        except Exception as e:
            # Silently fall back to deterministic analysis
            ai_analysis = None
    
    # Print summary (always)
    try:
        analyzer.print_summary(ai_analysis=ai_analysis)
    except Exception as e:
        print(f"\nError printing summary: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    
    # Generate report if requested
    if args.full_report:
        ai_recommendations = None
        if AIEngine:
            try:
                ai_engine = AIEngine()
                ai_recommendations = ai_engine.generate_recommendations(analyzer.data, analyzer.analysis)
            except Exception as e:
                print(f"Warning: Could not generate AI recommendations: {e}", file=sys.stderr)
        
        report_content = analyzer.generate_markdown_report(ai_recommendations)
        
        report_path = Path("report.md")
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            print(f"\nReport generated: {report_path}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing report: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
