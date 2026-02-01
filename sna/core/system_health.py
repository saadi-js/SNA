#!/usr/bin/env python3
"""
System Health Module
Collects and analyzes CPU, memory, and disk metrics.
"""

import json
import sys
from typing import Dict, Any, Optional
from ..utils.command_runner import CommandRunner


class SystemHealthCollector:
    """Collects system health metrics."""
    
    def __init__(self, command_runner: CommandRunner):
        self.runner = command_runner
    
    def collect(self) -> Dict[str, Any]:
        """Collect CPU, memory, and disk usage."""
        output = self.runner.run_bash_script("system_health.sh")
        if not output:
            return {}
        
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            print(f"Error parsing system health JSON: {e}", file=sys.stderr)
            return {}
    
    def get_status(self, health_data: Dict[str, Any]) -> Dict[str, str]:
        """Get status indicators for health metrics."""
        cpu_pct = health_data.get("cpu", {}).get("usage_percent", 0)
        mem_pct = health_data.get("memory", {}).get("usage_percent", 0)
        disk_pct = health_data.get("disk", {}).get("usage_percent", 0)
        
        cpu_status = self._get_cpu_status(cpu_pct)
        mem_status = self._get_memory_status(mem_pct)
        disk_status = self._get_disk_status(disk_pct)
        
        return {
            "cpu": cpu_status,
            "memory": mem_status,
            "disk": disk_status
        }
    
    def _get_cpu_status(self, pct: float) -> str:
        """Get CPU status indicator."""
        if pct >= 90:
            return "[CRITICAL]"
        elif pct >= 80:
            return "[HIGH]"
        elif pct >= 60:
            return "[MEDIUM]"
        return "[OK]"
    
    def _get_memory_status(self, pct: float) -> str:
        """Get memory status indicator."""
        if pct >= 90:
            return "[CRITICAL]"
        elif pct >= 80:
            return "[HIGH]"
        elif pct >= 75:
            return "[MEDIUM]"
        return "[OK]"
    
    def _get_disk_status(self, pct: int) -> str:
        """Get disk status indicator."""
        if pct >= 90:
            return "[CRITICAL]"
        elif pct >= 85:
            return "[HIGH]"
        elif pct >= 75:
            return "[MEDIUM]"
        return "[OK]"
