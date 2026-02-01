#!/usr/bin/env python3
"""
Original CPU Monitor - Simple CLI tool
This was the starting point before expansion.
"""

import subprocess
import sys

def get_cpu_usage():
    """Get CPU usage percentage."""
    try:
        # Get CPU usage from top command
        result = subprocess.run(
            ['top', '-bn1'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Parse CPU line
        for line in result.stdout.split('\n'):
            if 'Cpu(s)' in line:
                # Extract idle percentage
                parts = line.split(',')
                for part in parts:
                    if 'id' in part:
                        idle = float(part.split('%')[0].strip())
                        usage = 100 - idle
                        return usage
        return 0.0
    except Exception as e:
        print(f"Error getting CPU usage: {e}", file=sys.stderr)
        return 0.0

def main():
    """Main entry point."""
    cpu = get_cpu_usage()
    print(f"CPU Usage: {cpu:.1f}%")
    
    # Simple threshold check
    if cpu > 80:
        print("WARNING: High CPU usage!")
    elif cpu > 60:
        print("NOTE: Moderate CPU usage")

if __name__ == "__main__":
    main()
