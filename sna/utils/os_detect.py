#!/usr/bin/env python3
"""
OS Detection Utility
Detects platform and provides compatibility checks.
"""

import platform
import sys


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system() == "Linux"


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == "Windows"


def check_platform_compatibility() -> tuple[bool, str]:
    """
    Check if platform is compatible.
    Returns (is_compatible, message)
    """
    if is_linux():
        return True, "Linux platform detected"
    
    if is_windows():
        # Check for WSL
        import shutil
        if shutil.which("wsl") or shutil.which("bash"):
            return True, "Windows with WSL/bash detected"
        return False, "Windows detected but WSL/bash not available"
    
    return False, f"Unsupported platform: {platform.system()}"
