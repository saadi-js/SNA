#!/usr/bin/env python3
"""
Severity Scoring Engine
Computes system-wide severity scores based on collected data.
"""

from typing import Dict, Any, List


class SeverityScorer:
    """Calculates severity scores for system state."""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize scoring rules."""
        return {
            "health": [
                {"metric": "cpu", "threshold": 90, "severity": "CRITICAL"},
                {"metric": "cpu", "threshold": 80, "severity": "HIGH"},
                {"metric": "cpu", "threshold": 60, "severity": "MEDIUM"},
                {"metric": "memory", "threshold": 90, "severity": "CRITICAL"},
                {"metric": "memory", "threshold": 80, "severity": "HIGH"},
                {"metric": "memory", "threshold": 75, "severity": "MEDIUM"},
                {"metric": "disk", "threshold": 90, "severity": "CRITICAL"},
                {"metric": "disk", "threshold": 85, "severity": "HIGH"},
                {"metric": "disk", "threshold": 75, "severity": "MEDIUM"},
            ],
            "security": [
                {"metric": "root_ssh", "value": True, "severity": "HIGH"},
                {"metric": "password_auth", "value": True, "severity": "MEDIUM"},
            ],
            "logs": [
                {"metric": "failed_logins", "threshold": 20, "severity": "HIGH"},
                {"metric": "failed_logins", "threshold": 10, "severity": "MEDIUM"},
                {"metric": "service_errors", "threshold": 1, "severity": "MEDIUM"},
                {"metric": "kernel_errors", "threshold": 1, "severity": "HIGH"},
                {"metric": "segfaults", "threshold": 1, "severity": "HIGH"},
            ]
        }
    
    def score_health(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score health metrics."""
        findings = []
        cpu_pct = health_data.get("cpu", {}).get("usage_percent", 0)
        mem_pct = health_data.get("memory", {}).get("usage_percent", 0)
        disk_pct = health_data.get("disk", {}).get("usage_percent", 0)
        
        # CPU scoring
        if cpu_pct >= 90:
            findings.append({"severity": "CRITICAL", "metric": "CPU", "value": cpu_pct})
        elif cpu_pct >= 80:
            findings.append({"severity": "HIGH", "metric": "CPU", "value": cpu_pct})
        elif cpu_pct >= 60:
            findings.append({"severity": "MEDIUM", "metric": "CPU", "value": cpu_pct})
        
        # Memory scoring
        if mem_pct >= 90:
            findings.append({"severity": "CRITICAL", "metric": "Memory", "value": mem_pct})
        elif mem_pct >= 80:
            findings.append({"severity": "HIGH", "metric": "Memory", "value": mem_pct})
        elif mem_pct >= 75:
            findings.append({"severity": "MEDIUM", "metric": "Memory", "value": mem_pct})
        
        # Disk scoring
        if disk_pct >= 90:
            findings.append({"severity": "CRITICAL", "metric": "Disk", "value": disk_pct})
        elif disk_pct >= 85:
            findings.append({"severity": "HIGH", "metric": "Disk", "value": disk_pct})
        elif disk_pct >= 75:
            findings.append({"severity": "MEDIUM", "metric": "Disk", "value": disk_pct})
        
        return findings
    
    def score_security(self, ssh_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score security configuration."""
        findings = []
        
        if ssh_config.get("root_login_enabled") == "yes":
            findings.append({"severity": "HIGH", "metric": "SSH Root Login", "value": "Enabled"})
        
        if ssh_config.get("password_auth_enabled") == "yes":
            findings.append({"severity": "MEDIUM", "metric": "SSH Password Auth", "value": "Enabled"})
        
        return findings
    
    def score_logs(self, log_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score log analysis."""
        findings = []
        
        failed_logins = log_analysis.get("failed_ssh_logins", 0)
        if failed_logins > 20:
            findings.append({"severity": "HIGH", "metric": "Failed Logins", "value": failed_logins})
        elif failed_logins > 10:
            findings.append({"severity": "MEDIUM", "metric": "Failed Logins", "value": failed_logins})
        
        if len(log_analysis.get("service_errors", [])) >= 1:
            findings.append({"severity": "MEDIUM", "metric": "Service Errors", "value": len(log_analysis["service_errors"])})
        
        if log_analysis.get("kernel_errors", 0) >= 1:
            findings.append({"severity": "HIGH", "metric": "Kernel Errors", "value": log_analysis["kernel_errors"]})
        
        if log_analysis.get("segfaults", 0) > 0:
            findings.append({"severity": "HIGH", "metric": "Segfaults", "value": log_analysis["segfaults"]})
        
        return findings
    
    def compute_overall_severity(self, all_findings: List[Dict[str, Any]]) -> str:
        """Compute overall system severity with non-zero baseline."""
        severities = [f.get("severity") for f in all_findings if f.get("severity")]
        
        if "CRITICAL" in severities:
            return "CRITICAL"
        elif "HIGH" in severities:
            return "HIGH"
        elif "MEDIUM" in severities:
            return "MEDIUM"
        elif len(all_findings) > 0:
            # Any findings present, even if all LOW
            return "LOW"
        return "LOW"
    
    def compute_risk_score(self, all_findings: List[Dict[str, Any]], log_analysis: Dict[str, Any] = None) -> int:
        """
        Compute numeric risk score (0-100).
        0-20 = LOW, 21-50 = MEDIUM, 51+ = HIGH
        """
        score = 0
        
        # Base score from findings
        for finding in all_findings:
            severity = finding.get("severity", "LOW")
            if severity == "CRITICAL":
                score += 30
            elif severity == "HIGH":
                score += 15
            elif severity == "MEDIUM":
                score += 8
            elif severity == "LOW":
                score += 2
        
        # Additional scoring from log analysis
        if log_analysis:
            # Any log category present adds to baseline
            if log_analysis.get("failed_ssh_logins", 0) > 0:
                score += 3
            if len(log_analysis.get("service_errors", [])) > 0:
                score += 5
            if log_analysis.get("kernel_errors", 0) > 0:
                score += 10
            if log_analysis.get("auth_warnings", 0) > 0:
                score += 2
        
        # Cap at 100
        return min(score, 100)
