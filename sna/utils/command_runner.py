#!/usr/bin/env python3
"""
Command Runner Utility
Executes bash scripts and system commands safely.
"""

import subprocess
import os
import platform
import shutil
from pathlib import Path
from typing import Optional


class CommandRunner:
    """Handles execution of bash scripts and system commands."""
    
    def __init__(self, bash_dir: str = "bash"):
        self.bash_dir = Path(bash_dir)
        self.is_windows = platform.system() == "Windows"
        self.bash_cmd = self._find_bash_command()
    
    def _find_bash_command(self) -> Optional[str]:
        """Find the bash command to use for executing scripts."""
        if not self.is_windows:
            if shutil.which("bash"):
                return "bash"
            return None
        
        # On Windows, try to find bash
        if shutil.which("wsl"):
            return "wsl"
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
            return None
        
        if not self.bash_cmd:
            return None
        
        try:
            # Build command based on platform
            if self.is_windows:
                if self.bash_cmd == "wsl":
                    # Convert Windows path to WSL path
                    wsl_path = str(script_path).replace("\\", "/")
                    if wsl_path.startswith("C:"):
                        wsl_path = "/mnt/c" + wsl_path[2:]
                    elif wsl_path.startswith("c:"):
                        wsl_path = "/mnt/c" + wsl_path[2:]
                    cmd = ["wsl", "bash", wsl_path]
                else:
                    cmd = [self.bash_cmd, str(script_path)]
            else:
                try:
                    os.chmod(script_path, 0o755)
                except (OSError, PermissionError):
                    pass
                cmd = [self.bash_cmd, str(script_path)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None
    
    def run_command(self, command: list, timeout: int = 30) -> Optional[str]:
        """Run a system command and return output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            if result.returncode == 0:
                return result.stdout
            return None
        except Exception:
            return None
