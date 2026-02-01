#!/usr/bin/env python3
"""
Process Snapshot Module
Captures top CPU and memory processes (snapshot, not monitoring).
"""

import subprocess
import sys
from typing import Dict, Any, List, Optional
from ..utils.command_runner import CommandRunner


class ProcessSnapshot:
    """Captures process snapshots."""
    
    def __init__(self, command_runner: CommandRunner):
        self.runner = command_runner
    
    def get_top_cpu_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top CPU-consuming processes."""
        try:
            # Use ps command to get top CPU processes
            cmd = ["ps", "aux", "--sort=-%cpu", "--no-headers"]
            output = self.runner.run_command(cmd)
            
            if not output:
                return []
            
            processes = []
            lines = output.strip().split('\n')[:limit]
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 11:
                    processes.append({
                        "user": parts[0],
                        "pid": parts[1],
                        "cpu": parts[2],
                        "mem": parts[3],
                        "command": " ".join(parts[10:])
                    })
            
            return processes
        except Exception:
            return []
    
    def get_top_memory_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top memory-consuming processes."""
        try:
            # Use ps command to get top memory processes
            cmd = ["ps", "aux", "--sort=-%mem", "--no-headers"]
            output = self.runner.run_command(cmd)
            
            if not output:
                return []
            
            processes = []
            lines = output.strip().split('\n')[:limit]
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 11:
                    processes.append({
                        "user": parts[0],
                        "pid": parts[1],
                        "cpu": parts[2],
                        "mem": parts[3],
                        "command": " ".join(parts[10:])
                    })
            
            return processes
        except Exception:
            return []
    
    def get_process_snapshot(self, limit: int = 5) -> Dict[str, Any]:
        """Get complete process snapshot."""
        return {
            "top_cpu": self.get_top_cpu_processes(limit),
            "top_memory": self.get_top_memory_processes(limit)
        }
