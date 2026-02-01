#!/usr/bin/env python3
"""
SNA - System & Network Administration Analyzer
Multi-command CLI tool for system auditing and intelligence.
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import modules
from sna.utils.command_runner import CommandRunner
from sna.utils.os_detect import check_platform_compatibility
from sna.utils.output import OutputFormatter
from sna.core.system_health import SystemHealthCollector
from sna.core.security import SecurityCollector
from sna.core.logs import LogAnalyzer
from sna.core.processes import ProcessSnapshot
from sna.core.scoring import SeverityScorer
from sna.core.recommendations import RecommendationsEngine
from sna.baseline.baseline_manager import BaselineManager

# Optional AI engine
try:
    from ai_engine import AIEngine
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class SNACore:
    """Core SNA orchestrator."""
    
    def __init__(self):
        self.runner = CommandRunner()
        self.health_collector = SystemHealthCollector(self.runner)
        self.security_collector = SecurityCollector(self.runner)
        self.log_analyzer = LogAnalyzer(self.runner)
        self.process_snapshot = ProcessSnapshot(self.runner)
        self.scorer = SeverityScorer()
        self.recommender = RecommendationsEngine()
        self.baseline_manager = BaselineManager()
        self.formatter = OutputFormatter()
        
        # Check platform compatibility
        compatible, message = check_platform_compatibility()
        if not compatible:
            print(f"Error: {message}", file=sys.stderr)
            sys.exit(1)
    
    def collect_all_data(self, include_processes: bool = False) -> dict:
        """Collect all system data."""
        data = {}
        
        # Health data
        data["health"] = self.health_collector.collect()
        data["users_services"] = self._collect_users_services()
        data["ssh_config"] = self.security_collector.collect_ssh_config()
        
        # Log data
        log_text = self.log_analyzer.collect_logs()
        data["log_text"] = log_text
        data["log_analysis"] = self.log_analyzer.analyze(log_text)
        
        # Process snapshot (optional)
        if include_processes:
            data["processes"] = self.process_snapshot.get_process_snapshot()
        
        return data
    
    def _collect_users_services(self) -> dict:
        """Collect users and services data."""
        output = self.runner.run_bash_script("users_services.sh")
        if not output:
            return {}
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return {}
    
    def run_audit(self, full: bool = False, json_output: bool = False) -> dict:
        """Run full system audit."""
        if not json_output:
            print(self.formatter.format_header("System Audit Report", 60))
            print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        data = self.collect_all_data(include_processes=full)
        
        # Score system
        health_scores = self.scorer.score_health(data.get("health", {}))
        security_scores = self.scorer.score_security(data.get("ssh_config", {}))
        log_scores = self.scorer.score_logs(data.get("log_analysis", {}))
        
        all_scores = health_scores + security_scores + log_scores
        overall_severity = self.scorer.compute_overall_severity(all_scores)
        risk_score = self.scorer.compute_risk_score(all_scores, data.get("log_analysis", {}))
        
        if not json_output:
            print(f"Overall Severity: {overall_severity}")
            print(f"Risk Score: {risk_score} / 100", end="")
            if risk_score <= 20:
                print(" (LOW)")
            elif risk_score <= 50:
                print(" (MEDIUM)")
            else:
                print(" (HIGH)")
            print()
        
        # System Health
        health = data.get("health", {})
        if health and not json_output:
            status = self.health_collector.get_status(health)
            print(self.formatter.format_section("System Health"))
            cpu = health.get("cpu", {})
            mem = health.get("memory", {})
            disk = health.get("disk", {})
            print(self.formatter.format_metric("CPU Usage", f"{cpu.get('usage_percent', 0):.1f}%", status["cpu"]))
            print(self.formatter.format_metric("Memory Usage", f"{mem.get('usage_percent', 0):.1f}%", status["memory"]))
            print(self.formatter.format_metric("Disk Usage", f"{disk.get('usage_percent', 0)}%", status["disk"]))
        
        # Security Configuration
        ssh = data.get("ssh_config", {})
        if ssh and not json_output:
            print(self.formatter.format_section("Security Configuration"))
            root_status = "Enabled [WARNING]" if ssh.get('root_login_enabled') == 'yes' else "Disabled [OK]"
            pass_status = "Enabled [WARNING]" if ssh.get('password_auth_enabled') == 'yes' else "Disabled [OK]"
            print(self.formatter.format_metric("SSH Root Login", root_status))
            print(self.formatter.format_metric("SSH Password Auth", pass_status))
        
        # Log Intelligence
        log_analysis = data.get("log_analysis", {})
        if log_analysis and not json_output:
            print(self.formatter.format_section("Log Intelligence"))
            failed_logins = log_analysis.get("failed_ssh_logins", 0)
            login_status = "[OK]" if failed_logins == 0 else "[LOW]" if failed_logins < 10 else "[MEDIUM]" if failed_logins < 20 else "[HIGH]"
            print(self.formatter.format_metric("Authentication Failures", str(failed_logins), login_status))
            
            service_errors = log_analysis.get("service_errors", [])
            if service_errors:
                print(self.formatter.format_metric("Service Errors", ", ".join(service_errors[:5]), "[MEDIUM]"))
            
            if log_analysis.get("kernel_errors", 0) > 0:
                print(self.formatter.format_metric("Kernel Errors", str(log_analysis["kernel_errors"]), "[HIGH]"))
        
        # Findings - always generate explicit findings
        findings = []
        findings.extend(self.security_collector.analyze_ssh_risks(data.get("ssh_config", {})))
        findings.extend(self.log_analyzer.analyze_findings(data.get("log_analysis", {})))
        
        # Add health findings
        for score in health_scores:
            findings.append({
                "severity": score["severity"],
                "title": f"{score['metric']} Usage Elevated",
                "description": f"{score['metric']} usage is at {score['value']}%",
                "recommendation": f"Review {score['metric'].lower()} usage patterns"
            })
        
        # Generate baseline findings even when system is healthy
        if not findings:
            findings = self._generate_baseline_findings(data)
        
        # Recommendations - always generate
        recommendations = self.recommender.generate(findings, always_include_baseline=True)
        
        if json_output:
            return {
                "timestamp": datetime.now().isoformat(),
                "severity": overall_severity,
                "risk_score": risk_score,
                "health": health,
                "security": data.get("ssh_config", {}),
                "logs": data.get("log_analysis", {}),
                "findings": findings,
                "recommendations": recommendations
            }
        
        # Findings section - ALWAYS show (even when healthy)
        print(self.formatter.format_section("Findings"))
        if findings:
            for finding in findings[:10]:
                print(self.formatter.format_finding(
                    finding.get("severity", "LOW"),
                    finding.get("title", "Unknown"),
                    finding.get("description", "")
                ))
        else:
            print("  No abnormal resource usage detected")
            print("  No security misconfigurations found")
            print("  Logs show normal operational behavior")
        
        # Recommendations section - ALWAYS show
        print(self.formatter.format_section("Recommendations"))
        if recommendations:
            for rec in recommendations:
                print(self.formatter.format_recommendation(rec))
        else:
            print(self.formatter.format_recommendation("Schedule periodic audits using cron for continuous monitoring"))
            print(self.formatter.format_recommendation("Maintain baseline snapshots after system updates"))
            print(self.formatter.format_recommendation("Continue monitoring authentication logs for unusual patterns"))
        
        # Process snapshot (if --full)
        if full and data.get("processes"):
            print(self.formatter.format_section("Process Snapshot"))
            top_cpu = data["processes"].get("top_cpu", [])
            if top_cpu:
                print("  Top CPU Processes:")
                for proc in top_cpu[:5]:
                    print(f"    {proc.get('command', '')[:50]} - CPU: {proc.get('cpu', '')}%")
            
            top_mem = data["processes"].get("top_memory", [])
            if top_mem:
                print("  Top Memory Processes:")
                for proc in top_mem[:5]:
                    print(f"    {proc.get('command', '')[:50]} - MEM: {proc.get('mem', '')}%")
        
        # AI Analysis (if available)
        if AI_AVAILABLE:
            try:
                ai_engine = AIEngine()
                ai_analysis = ai_engine.generate_recommendations(data, {"overall_severity": overall_severity})
                if ai_analysis:
                    print(self.formatter.format_section("AI Analysis"))
                    for line in ai_analysis.strip().split('\n'):
                        if line.strip():
                            print(f"  {line.strip()}")
            except Exception:
                pass
        
        print("\n" + "="*60)
        return data
    
    def _generate_baseline_findings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate baseline findings when system is healthy."""
        findings = []
        
        health = data.get("health", {})
        log_analysis = data.get("log_analysis", {})
        
        # Always add baseline findings
        findings.append({
            "severity": "LOW",
            "title": "System Health Status",
            "description": "No abnormal resource usage detected - CPU, memory, and disk are within normal ranges",
            "recommendation": "Continue monitoring resource usage patterns"
        })
        
        findings.append({
            "severity": "LOW",
            "title": "Security Configuration Status",
            "description": "No security misconfigurations found - SSH settings are properly configured",
            "recommendation": "Maintain current security posture and review periodically"
        })
        
        # Check if any log categories are present (even if no errors)
        if log_analysis:
            log_categories = []
            if log_analysis.get("failed_ssh_logins", 0) == 0:
                log_categories.append("authentication")
            if len(log_analysis.get("service_errors", [])) == 0:
                log_categories.append("services")
            if log_analysis.get("kernel_errors", 0) == 0:
                log_categories.append("kernel")
            
            if log_categories:
                findings.append({
                    "severity": "LOW",
                    "title": "Log Intelligence Status",
                    "description": f"Logs show normal operational behavior - {', '.join(log_categories)} logs are clean",
                    "recommendation": "Continue monitoring logs for anomalies"
                })
        
        return findings
    
    def run_security(self) -> None:
        """Run security-focused audit."""
        print(self.formatter.format_header("Security Audit", 60))
        
        data = self.collect_all_data()
        
        # Security findings
        ssh_findings = self.security_collector.analyze_ssh_risks(data.get("ssh_config", {}))
        log_findings = self.log_analyzer.analyze_findings(data.get("log_analysis", {}))
        
        # Filter for security-related findings
        security_findings = [f for f in log_findings if "auth" in f.get("title", "").lower() or "login" in f.get("title", "").lower()]
        security_findings.extend(ssh_findings)
        
        # Always show findings section
        print(self.formatter.format_section("Security Findings"))
        if security_findings:
            for finding in security_findings:
                print(self.formatter.format_finding(
                    finding.get("severity", "LOW"),
                    finding.get("title", "Unknown"),
                    finding.get("description", "")
                ))
        else:
            print("  [LOW] No security misconfigurations found")
            print("  [LOW] SSH configuration is properly secured")
            print("  [LOW] Authentication logs show normal patterns")
        
        # Always show recommendations
        print(self.formatter.format_section("Recommendations"))
        if security_findings:
            for finding in security_findings:
                if finding.get("recommendation"):
                    print(self.formatter.format_recommendation(finding["recommendation"]))
        else:
            print(self.formatter.format_recommendation("Continue monitoring authentication logs for unusual patterns"))
            print(self.formatter.format_recommendation("Maintain current security posture and review SSH configuration periodically"))
            print(self.formatter.format_recommendation("Consider implementing Fail2Ban for automated brute force protection"))
        
        print("\n" + "="*60)
    
    def run_logs(self) -> None:
        """Run log intelligence analysis."""
        print(self.formatter.format_header("Log Intelligence Analysis", 60))
        
        log_text = self.log_analyzer.collect_logs()
        log_analysis = self.log_analyzer.analyze(log_text)
        findings = self.log_analyzer.analyze_findings(log_analysis)
        
        print(self.formatter.format_section("Log Summary"))
        print(self.formatter.format_metric("Failed SSH Logins", str(log_analysis.get("failed_ssh_logins", 0))))
        print(self.formatter.format_metric("Authentication Warnings", str(log_analysis.get("auth_warnings", 0))))
        print(self.formatter.format_metric("Service Errors", str(len(log_analysis.get("service_errors", [])))))
        print(self.formatter.format_metric("Kernel Errors", str(log_analysis.get("kernel_errors", 0))))
        print(self.formatter.format_metric("Segfaults", str(log_analysis.get("segfaults", 0))))
        
        # Always show findings section
        print(self.formatter.format_section("Log Findings"))
        if findings:
            for finding in findings:
                print(self.formatter.format_finding(
                    finding.get("severity", "LOW"),
                    finding.get("title", "Unknown"),
                    finding.get("description", "")
                ))
        else:
            print("  [LOW] Logs show normal operational behavior")
            print("  [LOW] No authentication failures detected")
            print("  [LOW] No service errors or kernel issues found")
        
        # Always show recommendations
        print(self.formatter.format_section("Recommendations"))
        if findings:
            recommendations = self.recommender.generate(findings, always_include_baseline=True)
            for rec in recommendations:
                print(self.formatter.format_recommendation(rec))
        else:
            print(self.formatter.format_recommendation("Continue monitoring logs for anomalies and unusual patterns"))
            print(self.formatter.format_recommendation("Review authentication logs periodically for security concerns"))
            print(self.formatter.format_recommendation("Set up log rotation to manage log file sizes"))
        
        print("\n" + "="*60)
    
    def baseline_save(self, name: str = None) -> None:
        """Save current system state as baseline."""
        print("Collecting system data for baseline...")
        data = self.collect_all_data()
        
        baseline_file = self.baseline_manager.save(data, name)
        print(f"Baseline saved: {baseline_file.name}")
        print(f"Location: {baseline_file}")
    
    def baseline_compare(self, baseline_name: str) -> None:
        """Compare current state with baseline."""
        print(f"Comparing with baseline: {baseline_name}")
        
        current_data = self.collect_all_data()
        drift = self.baseline_manager.compare(current_data, baseline_name)
        
        if "error" in drift:
            print(f"Error: {drift['error']}")
            return
        
        print(self.formatter.format_header("Baseline Comparison", 60))
        print(f"Baseline: {drift['baseline_name']} ({drift['baseline_timestamp']})")
        print(f"Current: {drift['comparison_timestamp']}\n")
        
        if drift["changes"]:
            print(self.formatter.format_section("Detected Changes"))
            for change in drift["changes"]:
                change_type = change.get("type", "unknown")
                if change_type == "resource_spike":
                    print(f"  {change['metric']} spike: {change['baseline']:.1f}% → {change['current']:.1f}% (Δ{change['change']:+.1f}%)")
                elif change_type == "disk_growth":
                    print(f"  Disk growth: {change['baseline']}% → {change['current']}% (Δ{change['change']:+}%)")
                elif change_type == "new_services":
                    print(f"  New services: {', '.join(change['services'])}")
                elif change_type == "removed_services":
                    print(f"  Removed services: {', '.join(change['services'])}")
                elif change_type == "user_count_change":
                    print(f"  User count: {change['baseline']} → {change['current']}")
        else:
            print("  No significant changes detected.")
        
        print("\n" + "="*60)
    
    def baseline_list(self) -> None:
        """List all available baselines."""
        baselines = self.baseline_manager.list_baselines()
        if baselines:
            print("Available baselines:")
            for baseline in baselines:
                print(f"  - {baseline}")
        else:
            print("No baselines found.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SNA - System & Network Administration Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Run full system audit")
    audit_parser.add_argument("--full", action="store_true", help="Include process snapshot")
    audit_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Security command
    subparsers.add_parser("security", help="Run security-focused audit")
    
    # Logs command
    subparsers.add_parser("logs", help="Run log intelligence analysis")
    
    # Baseline commands
    baseline_parser = subparsers.add_parser("baseline", help="Baseline management")
    baseline_subparsers = baseline_parser.add_subparsers(dest="baseline_action")
    
    baseline_save_parser = baseline_subparsers.add_parser("save", help="Save current system state")
    baseline_save_parser.add_argument("--name", help="Baseline name (optional)")
    
    baseline_compare_parser = baseline_subparsers.add_parser("compare", help="Compare with baseline")
    baseline_compare_parser.add_argument("name", help="Baseline name to compare with (use 'baseline list' to see available)")
    
    baseline_subparsers.add_parser("list", help="List all baselines")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    sna = SNACore()
    
    try:
        if args.command == "audit":
            result = sna.run_audit(full=args.full, json_output=args.json)
            if args.json:
                # Save to reports/ directory
                reports_dir = Path("reports")
                reports_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_file = reports_dir / f"audit_{timestamp}.json"
                with open(report_file, "w") as f:
                    json.dump(result, f, indent=2)
                print(f"Report saved: {report_file}", file=sys.stderr)
        elif args.command == "security":
            sna.run_security()
        elif args.command == "logs":
            sna.run_logs()
        elif args.command == "baseline":
            if args.baseline_action == "save":
                sna.baseline_save(name=getattr(args, 'name', None))
            elif args.baseline_action == "compare":
                baseline_name = getattr(args, 'name', None)
                if not baseline_name:
                    print("Error: Baseline name required. Use 'baseline list' to see available baselines.", file=sys.stderr)
                    print("Usage: python analyzer_new.py baseline compare <baseline_name>", file=sys.stderr)
                    sys.exit(1)
                sna.baseline_compare(baseline_name)
            elif args.baseline_action == "list":
                sna.baseline_list()
            else:
                baseline_parser.print_help()
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
