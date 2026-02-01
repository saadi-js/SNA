# WSL Testing Guide - Enhanced SNA Analyzer

## Quick Start

### 1. Open WSL Terminal
```bash
wsl
```

### 2. Navigate to Project
```bash
cd /mnt/c/Users/user/SNA
```

### 3. Test Basic Audit
```bash
python3 analyzer_new.py audit
```

**Expected:** Should show Findings and Recommendations sections even if system is healthy.

---

## Complete Test Sequence

### Test 1: Basic Audit (Check New Features)
```bash
python3 analyzer_new.py audit
```

**Verify:**
- ✅ Risk Score appears (e.g., "Risk Score: 12 / 100 (LOW)")
- ✅ Findings section appears (even if all [LOW])
- ✅ Recommendations section appears
- ✅ All sections are clearly formatted

### Test 2: Full Audit with Process Snapshot
```bash
python3 analyzer_new.py audit --full
```

**Verify:**
- ✅ All features from Test 1
- ✅ Process Snapshot section appears
- ✅ Top CPU and Memory processes listed

### Test 3: JSON Export
```bash
python3 analyzer_new.py audit --json
```

**Verify:**
- ✅ Creates `reports/` directory
- ✅ Saves JSON file: `reports/audit_YYYYMMDD_HHMMSS.json`
- ✅ File contains: severity, risk_score, findings, recommendations

**Check the file:**
```bash
ls reports/
cat reports/audit_*.json | head -30
```

### Test 4: Security Audit
```bash
python3 analyzer_new.py security
```

**Verify:**
- ✅ Security Findings section (always shown)
- ✅ Recommendations section (always shown)
- ✅ Even if no issues, shows baseline findings

### Test 5: Log Intelligence
```bash
python3 analyzer_new.py logs
```

**Verify:**
- ✅ Log Summary with metrics
- ✅ Log Findings section (always shown)
- ✅ Recommendations section (always shown)

### Test 6: Baseline Management
```bash
# Save a baseline
python3 analyzer_new.py baseline save

# List baselines
python3 analyzer_new.py baseline list

# Compare (use name from list)
python3 analyzer_new.py baseline compare baseline_20240201_143022
```

**Verify:**
- ✅ Baseline saves successfully
- ✅ List shows saved baselines
- ✅ Compare shows drift detection

---

## What to Look For

### ✅ Success Indicators

1. **Risk Score Always Shown:**
   ```
   Risk Score: 12 / 100 (LOW)
   ```

2. **Findings Section Always Present:**
   ```
   Findings:
     [LOW] System Health Status
       • No abnormal resource usage detected...
   ```

3. **Recommendations Always Present:**
   ```
   Recommendations:
     • Schedule periodic audits using cron...
     • Maintain baseline snapshots...
   ```

4. **JSON Export Works:**
   ```
   Report saved: reports/audit_20240201_143022.json
   ```

### ❌ If Something's Missing

**No Risk Score:**
- Check if you're running `analyzer_new.py` (not old `analyzer.py`)

**No Findings/Recommendations:**
- Make sure you're using the latest version
- Check: `python3 analyzer_new.py --help` should show all commands

**JSON Export Fails:**
- Check write permissions: `ls -la reports/`
- Verify directory created: `ls -d reports/`

---

## Quick Verification Script

Run this to verify all features:

```bash
#!/bin/bash
echo "=== Testing SNA Analyzer ==="

echo "1. Testing basic audit..."
python3 analyzer_new.py audit > /tmp/test1.txt 2>&1
if grep -q "Risk Score" /tmp/test1.txt && grep -q "Findings" /tmp/test1.txt && grep -q "Recommendations" /tmp/test1.txt; then
    echo "   ✓ Basic audit works"
else
    echo "   ✗ Basic audit missing features"
fi

echo "2. Testing JSON export..."
python3 analyzer_new.py audit --json > /tmp/test2.txt 2>&1
if [ -d "reports" ] && ls reports/audit_*.json > /dev/null 2>&1; then
    echo "   ✓ JSON export works"
else
    echo "   ✗ JSON export failed"
fi

echo "3. Testing security command..."
python3 analyzer_new.py security > /tmp/test3.txt 2>&1
if grep -q "Security Findings" /tmp/test3.txt && grep -q "Recommendations" /tmp/test3.txt; then
    echo "   ✓ Security command works"
else
    echo "   ✗ Security command missing features"
fi

echo "4. Testing logs command..."
python3 analyzer_new.py logs > /tmp/test4.txt 2>&1
if grep -q "Log Findings" /tmp/test4.txt && grep -q "Recommendations" /tmp/test4.txt; then
    echo "   ✓ Logs command works"
else
    echo "   ✗ Logs command missing features"
fi

echo "=== Test Complete ==="
```

---

## Expected Output Example

When you run `python3 analyzer_new.py audit`, you should see:

```
============================================================
System Audit Report
============================================================
Analysis Date: 2024-02-01 14:30:22
Overall Severity: LOW
Risk Score: 12 / 100 (LOW)

System Health:
  CPU Usage:    3.7% [OK]
  Memory Usage: 12.8% [OK]
  Disk Usage:   1% [OK]

Security Configuration:
  SSH Root Login:            Disabled [OK]
  SSH Password Authentication: Disabled [OK]

Log Intelligence:
  Authentication Failures: 0 [OK]

Findings:
  [LOW] System Health Status
    • No abnormal resource usage detected - CPU, memory, and disk are within normal ranges
  [LOW] Security Configuration Status
    • No security misconfigurations found - SSH settings are properly configured
  [LOW] Log Intelligence Status
    • Logs show normal operational behavior - authentication, services, kernel logs are clean

Recommendations:
  • Schedule periodic audits using cron for continuous monitoring
  • Maintain baseline snapshots after system updates or configuration changes
  • Continue monitoring authentication logs for unusual patterns
  • Review system health metrics regularly to detect trends

============================================================
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'sna'"
**Fix:**
```bash
# Make sure you're in the project directory
pwd
# Should show: /mnt/c/Users/user/SNA

# Check if sna directory exists
ls -la sna/
```

### "Command not found: analyzer_new.py"
**Fix:**
```bash
# Use python3 explicitly
python3 analyzer_new.py audit
```

### "No such file or directory: reports"
**Fix:**
```bash
# The tool should create it automatically, but if not:
mkdir -p reports
python3 analyzer_new.py audit --json
```

---

## Ready to Test!

Start with:
```bash
python3 analyzer_new.py audit
```

You should immediately see the enhanced output with Findings and Recommendations sections.
