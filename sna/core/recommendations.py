#!/usr/bin/env python3
"""
Recommendations Engine
Generates actionable recommendations based on findings.
"""

from typing import Dict, Any, List


class RecommendationsEngine:
    """Generates actionable recommendations."""
    
    def __init__(self):
        self.recommendation_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize recommendation templates."""
        return {
            "cpu_high": "Investigate high CPU usage - check running processes and consider resource optimization",
            "memory_high": "Review memory usage - identify memory-intensive processes and consider adding swap or RAM",
            "disk_high": "Disk space is running low - clean up old logs, temporary files, or unused packages",
            "ssh_root": "Disable root SSH login for better security - edit /etc/ssh/sshd_config",
            "ssh_password": "Consider disabling password authentication and using SSH keys only",
            "failed_logins": "Review authentication logs and consider implementing Fail2Ban to prevent brute force attacks",
            "service_errors": "Investigate service errors - check service status and logs for misconfiguration",
            "kernel_errors": "Kernel errors detected - investigate hardware, drivers, or system stability issues",
            "segfaults": "Application crashes detected - review application logs and check for memory issues"
        }
    
    def generate(self, findings: List[Dict[str, Any]], always_include_baseline: bool = True) -> List[str]:
        """Generate recommendations from findings. Always includes baseline recommendations."""
        recommendations = []
        seen = set()
        
        # Generate recommendations from findings
        for finding in findings:
            metric = finding.get("metric", "").lower()
            severity = finding.get("severity", "")
            
            # Include all findings, not just HIGH/CRITICAL
            if "cpu" in metric:
                rec = self.recommendation_templates.get("cpu_high", "Review CPU usage")
            elif "memory" in metric:
                rec = self.recommendation_templates.get("memory_high", "Review memory usage")
            elif "disk" in metric:
                rec = self.recommendation_templates.get("disk_high", "Review disk usage")
            elif "root" in metric and "ssh" in metric:
                rec = self.recommendation_templates.get("ssh_root", "Review SSH configuration")
            elif "password" in metric and "ssh" in metric:
                rec = self.recommendation_templates.get("ssh_password", "Review SSH authentication")
            elif "login" in metric or "auth" in metric:
                rec = self.recommendation_templates.get("failed_logins", "Review authentication logs")
            elif "service" in metric:
                rec = self.recommendation_templates.get("service_errors", "Review service status")
            elif "kernel" in metric:
                rec = self.recommendation_templates.get("kernel_errors", "Investigate kernel issues")
            elif "segfault" in metric or "crash" in metric:
                rec = self.recommendation_templates.get("segfaults", "Investigate application crashes")
            else:
                # Use custom recommendation if available
                rec = finding.get("recommendation", f"Review {finding.get('title', 'issue')}")
            
            if rec and rec not in seen:
                recommendations.append(rec)
                seen.add(rec)
        
        # Always include baseline recommendations (even when system is healthy)
        if always_include_baseline:
            baseline_recs = [
                "Schedule periodic audits using cron for continuous monitoring",
                "Maintain baseline snapshots after system updates or configuration changes",
                "Continue monitoring authentication logs for unusual patterns",
                "Review system health metrics regularly to detect trends"
            ]
            for rec in baseline_recs:
                if rec not in seen:
                    recommendations.append(rec)
                    seen.add(rec)
        
        return recommendations
