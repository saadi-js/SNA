#!/usr/bin/env python3
"""
Baseline Manager
Handles saving and comparing system state snapshots.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class BaselineManager:
    """Manages system baseline snapshots."""
    
    def __init__(self, baseline_dir: str = ".baseline"):
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(exist_ok=True)
        self.schema_file = self.baseline_dir / "schema.json"
    
    def save(self, system_data: Dict[str, Any], name: Optional[str] = None) -> Path:
        """Save current system state as baseline."""
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"baseline_{timestamp}"
        
        baseline_file = self.baseline_dir / f"{name}.json"
        
        baseline_data = {
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "system": {
                "cpu": system_data.get("health", {}).get("cpu", {}),
                "memory": system_data.get("health", {}).get("memory", {}),
                "disk": system_data.get("health", {}).get("disk", {}),
            },
            "services": {
                "active_count": system_data.get("users_services", {}).get("services", {}).get("active_count", 0),
                "active_services": system_data.get("users_services", {}).get("services", {}).get("active_services", "").split(",") if system_data.get("users_services", {}).get("services", {}).get("active_services") else []
            },
            "users": {
                "logged_in_count": system_data.get("users_services", {}).get("users", {}).get("logged_in_count", 0),
            },
            "security": {
                "ssh_root_login": system_data.get("ssh_config", {}).get("root_login_enabled", "unknown"),
                "ssh_password_auth": system_data.get("ssh_config", {}).get("password_auth_enabled", "unknown"),
            }
        }
        
        with open(baseline_file, "w") as f:
            json.dump(baseline_data, f, indent=2)
        
        return baseline_file
    
    def load(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a baseline by name."""
        baseline_file = self.baseline_dir / f"{name}.json"
        if not baseline_file.exists():
            return None
        
        with open(baseline_file, "r") as f:
            return json.load(f)
    
    def list_baselines(self) -> List[str]:
        """List all available baselines."""
        baselines = []
        for file in self.baseline_dir.glob("baseline_*.json"):
            baselines.append(file.stem)
        return sorted(baselines)
    
    def compare(self, current_data: Dict[str, Any], baseline_name: str) -> Dict[str, Any]:
        """Compare current state with baseline."""
        baseline = self.load(baseline_name)
        if not baseline:
            return {"error": f"Baseline '{baseline_name}' not found"}
        
        drift = {
            "baseline_name": baseline_name,
            "baseline_timestamp": baseline.get("timestamp"),
            "comparison_timestamp": datetime.now().isoformat(),
            "changes": []
        }
        
        # Compare CPU
        current_cpu = current_data.get("health", {}).get("cpu", {}).get("usage_percent", 0)
        baseline_cpu = baseline.get("system", {}).get("cpu", {}).get("usage_percent", 0)
        if abs(current_cpu - baseline_cpu) > 10:
            drift["changes"].append({
                "type": "resource_spike",
                "metric": "CPU",
                "baseline": baseline_cpu,
                "current": current_cpu,
                "change": current_cpu - baseline_cpu
            })
        
        # Compare Memory
        current_mem = current_data.get("health", {}).get("memory", {}).get("usage_percent", 0)
        baseline_mem = baseline.get("system", {}).get("memory", {}).get("usage_percent", 0)
        if abs(current_mem - baseline_mem) > 10:
            drift["changes"].append({
                "type": "resource_spike",
                "metric": "Memory",
                "baseline": baseline_mem,
                "current": current_mem,
                "change": current_mem - baseline_mem
            })
        
        # Compare Disk
        current_disk = current_data.get("health", {}).get("disk", {}).get("usage_percent", 0)
        baseline_disk = baseline.get("system", {}).get("disk", {}).get("usage_percent", 0)
        if current_disk > baseline_disk + 5:
            drift["changes"].append({
                "type": "disk_growth",
                "metric": "Disk",
                "baseline": baseline_disk,
                "current": current_disk,
                "change": current_disk - baseline_disk
            })
        
        # Compare Services
        current_services = set(current_data.get("users_services", {}).get("services", {}).get("active_services", "").split(",") if current_data.get("users_services", {}).get("services", {}).get("active_services") else [])
        baseline_services = set(baseline.get("services", {}).get("active_services", []))
        
        new_services = current_services - baseline_services
        removed_services = baseline_services - current_services
        
        if new_services:
            drift["changes"].append({
                "type": "new_services",
                "services": list(new_services)
            })
        
        if removed_services:
            drift["changes"].append({
                "type": "removed_services",
                "services": list(removed_services)
            })
        
        # Compare user count
        current_users = current_data.get("users_services", {}).get("users", {}).get("logged_in_count", 0)
        baseline_users = baseline.get("users", {}).get("logged_in_count", 0)
        if current_users != baseline_users:
            drift["changes"].append({
                "type": "user_count_change",
                "baseline": baseline_users,
                "current": current_users
            })
        
        return drift
