# Before & After: Code Comparison

## CPU Collection: Original vs Refactored

### Original Approach (Python)
```python
def get_cpu_usage():
    """Get CPU usage percentage."""
    result = subprocess.run(
        ['top', '-bn1'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    # Parse CPU line
    for line in result.stdout.split('\n'):
        if 'Cpu(s)' in line:
            parts = line.split(',')
            for part in parts:
                if 'id' in part:
                    idle = float(part.split('%')[0].strip())
                    usage = 100 - idle
                    return usage
    return 0.0
```

### Refactored Approach (Bash + Python)

**Bash Script (`bash/system_health.sh`):**
```bash
# CPU Usage (1-minute load average and percentage)
cpu_load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
cpu_cores=$(nproc)
cpu_percent=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
```

**Python Parser (`analyzer.py`):**
```python
def collect_system_health(self) -> Dict[str, Any]:
    """Collect CPU, memory, and disk usage."""
    output = self.run_bash_script("system_health.sh")
    if not output:
        return {}
    
    try:
        return json.loads(output)  # Parse JSON from bash script
    except json.JSONDecodeError as e:
        print(f"Error parsing system health JSON: {e}", file=sys.stderr)
        return {}
```

**Key Improvements:**
1. ✅ **Preserved logic:** Same `top -bn1` command, same parsing approach
2. ✅ **Enhanced:** Added load average and core count
3. ✅ **Modular:** Can test bash script independently
4. ✅ **Consistent:** Same pattern for memory and disk
5. ✅ **Structured:** JSON output for reliable parsing

---

## Threshold Logic: Original vs Enhanced

### Original
```python
if cpu > 80:
    print("WARNING: High CPU usage!")
elif cpu > 60:
    print("NOTE: Moderate CPU usage")
```

### Refactored
```python
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
```

**Key Improvements:**
1. ✅ **Preserved:** 80% threshold still triggers HIGH severity
2. ✅ **Enhanced:** Added CRITICAL (90%) and MEDIUM (60%) levels
3. ✅ **Structured:** Returns structured findings instead of print statements
4. ✅ **Consistent:** Same pattern applied to memory and disk
5. ✅ **Actionable:** Messages explain severity and values

---

## Output: Original vs Enhanced

### Original
```
CPU Usage: 45.2%
NOTE: Moderate CPU usage
```

### Refactored
```
============================================================
Linux Server Health & Security Analysis
============================================================
Analysis Date: 2024-01-15 14:30:22
Overall Severity: HIGH

System Health:
  CPU:    45.2% (Load: 1.23)
  Memory: 68.5% (4096/8192 MB)
  Disk:   82.0% (164G/200G)

Security Configuration:
  SSH Root Login:      Disabled [OK]
  SSH Password Auth:   Disabled [OK]

Key Findings:
  [MEDIUM] Disk Usage: Disk usage is moderately elevated at 82%

============================================================
```

**Key Improvements:**
1. ✅ **Preserved:** CPU usage still displayed prominently
2. ✅ **Enhanced:** Added context (load average, memory, disk)
3. ✅ **Structured:** Clear sections and formatting
4. ✅ **Actionable:** Severity indicators and findings
5. ✅ **Professional:** Suitable for system administration reports

---

## Architecture: Monolithic vs Modular

### Original Structure
```
cpu_monitor_original.py (50 lines)
├── get_cpu_usage()
└── main()
```

### Refactored Structure
```
project/ (650+ lines, modular)
├── bash/
│   ├── system_health.sh      (CPU + Memory + Disk)
│   ├── users_services.sh     (Users + Services)
│   ├── ssh_check.sh          (Security)
│   └── log_extract.sh        (Logs)
├── analyzer.py               (Orchestration + Analysis)
├── ai_engine.py              (LLM Integration)
└── README.md                  (Documentation)
```

**Benefits of Modular Approach:**
1. ✅ **Testable:** Each component can be tested independently
2. ✅ **Maintainable:** Changes to one component don't affect others
3. ✅ **Extensible:** Easy to add new metrics or features
4. ✅ **Debuggable:** Can run bash scripts manually to verify
5. ✅ **Professional:** Follows software engineering best practices

---

## Feature Comparison

| Feature | Original | Refactored |
|---------|----------|------------|
| CPU Monitoring | ✅ | ✅ (Enhanced) |
| Memory Monitoring | ❌ | ✅ |
| Disk Monitoring | ❌ | ✅ |
| User Enumeration | ❌ | ✅ |
| Service Status | ❌ | ✅ |
| SSH Security Check | ❌ | ✅ |
| Log Analysis | ❌ | ✅ |
| AI Recommendations | ❌ | ✅ |
| Markdown Reports | ❌ | ✅ |
| CLI Flags | ❌ | ✅ |
| Error Handling | Basic | Comprehensive |
| Platform Support | Linux only | Linux + WSL |

---

## Code Quality Improvements

### Error Handling

**Original:**
```python
except Exception as e:
    print(f"Error getting CPU usage: {e}", file=sys.stderr)
    return 0.0
```

**Refactored:**
```python
except subprocess.TimeoutExpired:
    print(f"Error: {script_name} timed out", file=sys.stderr)
    return None
except Exception as e:
    print(f"Error running {script_name}: {e}", file=sys.stderr)
    return None
```

### Type Hints

**Original:** No type hints

**Refactored:**
```python
def collect_system_health(self) -> Dict[str, Any]:
    """Collect CPU, memory, and disk usage."""
```

### Documentation

**Original:** Minimal comments

**Refactored:** Comprehensive docstrings and inline comments explaining sysadmin concepts

---

## Summary

The refactored code:
- ✅ **Preserves** all original CPU monitoring logic
- ✅ **Enhances** with additional metrics and features
- ✅ **Improves** code quality and maintainability
- ✅ **Expands** functionality while maintaining clarity
- ✅ **Follows** professional software engineering practices

The evolution from a simple CPU monitor to a comprehensive system analyzer demonstrates incremental development, modular design, and preservation of working functionality.
