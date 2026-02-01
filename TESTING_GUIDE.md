# Testing Guide: WSL Setup & Verification

## Quick Start Testing

### Step 1: Open WSL Terminal
```bash
# From Windows PowerShell or Start Menu
wsl
```

### Step 2: Navigate to Project
```bash
cd /mnt/c/Users/user/SNA
```

### Step 3: Run Setup Test
```bash
bash test_setup.sh
```

This will check:
- ✅ Python installation
- ✅ Dependencies
- ✅ Bash scripts
- ✅ File permissions
- ✅ Script executability

---

## Detailed Testing Steps

### Phase 1: Environment Verification

#### 1.1 Check Python
```bash
python3 --version
# Should show: Python 3.x.x

# If not installed:
sudo apt-get update
sudo apt-get install python3 python3-pip
```

#### 1.2 Install Dependencies
```bash
pip3 install python-dotenv google-generativeai
# OR
pip3 install -r requirements.txt
```

#### 1.3 Verify Files Exist
```bash
ls -la
# Should see: analyzer.py, ai_engine.py, bash/, etc.

ls -la bash/
# Should see: system_health.sh, users_services.sh, ssh_check.sh, log_extract.sh
```

#### 1.4 Make Scripts Executable
```bash
chmod +x bash/*.sh
chmod +x test_setup.sh
```

---

### Phase 2: Component Testing

#### 2.1 Test Bash Scripts Individually

**Test CPU/Memory/Disk Collection:**
```bash
bash bash/system_health.sh
```

**Expected Output:**
```json
{
  "cpu": {
    "load_1min": 1.23,
    "cores": 4,
    "usage_percent": 45.2
  },
  "memory": {
    "total_mb": 8192,
    "used_mb": 4096,
    "usage_percent": 50.0
  },
  "disk": {
    "total": "100G",
    "used": "50G",
    "available": "45G",
    "usage_percent": 50
  }
}
```

**Test Users & Services:**
```bash
bash bash/users_services.sh
```

**Expected Output:**
```json
{
  "users": {
    "logged_in_count": 1,
    "logged_in_users": "username",
    "root_logged_in": 0
  },
  "services": {
    "active_count": 45,
    "active_services": "ssh,apache2,mysql"
  }
}
```

**Test SSH Configuration:**
```bash
bash bash/ssh_check.sh
```

**Expected Output:**
```json
{
  "ssh_config_exists": true,
  "ssh_service_running": "active",
  "root_login_enabled": "no",
  "root_login_setting": "prohibit-password",
  "password_auth_enabled": "yes",
  "password_auth_setting": "yes"
}
```

**Test Log Extraction:**
```bash
bash bash/log_extract.sh
```

**Expected Output:**
```
=== AUTHENTICATION LOG (Last 200 entries) ===
[log entries...]

=== SYSTEM ERROR LOG (Last 100 entries) ===
[log entries...]
```

**Note:** Log files may not exist in WSL. This is OK - the tool handles missing files gracefully.

---

### Phase 3: Python Module Testing

#### 3.1 Test Python Imports
```bash
python3 -c "import analyzer; print('✓ analyzer.py imports OK')"
python3 -c "import ai_engine; print('✓ ai_engine.py imports OK')"
```

#### 3.2 Test Analyzer Help
```bash
python3 analyzer.py --help
```

**Expected Output:**
```
usage: analyzer.py [-h] [--summary] [--full-report] [--logs] [--health]

AI-Assisted Linux Server Health & Log Analyzer

options:
  -h, --help     show this help message and exit
  --summary      Display terminal summary only
  --full-report  Generate markdown report (report.md)
  --logs         Include log analysis
  --health       Include health analysis (CPU, memory, disk)
```

---

### Phase 4: Full System Testing

#### 4.1 Basic Run (Terminal Summary)
```bash
python3 analyzer.py
```

**Expected Output:**
```
Collecting system data...
Platform: Linux
Bash command: bash

============================================================
Linux Server Health & Security Analysis
============================================================
Analysis Date: 2024-XX-XX XX:XX:XX
Overall Severity: LOW

System Health:
  CPU:    XX.X% (Load: X.XX)
  Memory: XX.X% (XXXX/XXXX MB)
  Disk:   XX% (XXG/XXXG)

Security Configuration:
  SSH Root Login:      Disabled [OK]
  SSH Password Auth:   Disabled [OK]

No issues detected.

============================================================
```

#### 4.2 Test with Full Report
```bash
python3 analyzer.py --full-report
```

**Expected Output:**
- Terminal summary (same as above)
- Plus: `Report generated: report.md`

**Verify Report:**
```bash
cat report.md
```

Should contain:
- System Health section
- Users & Services section
- Security Findings section
- Log Analysis section
- AI Recommendations section (if API key configured)

#### 4.3 Test Health Only
```bash
python3 analyzer.py --health
```

Should show only health metrics, no logs.

#### 4.4 Test Logs Only
```bash
python3 analyzer.py --logs
```

Should show log analysis, minimal health info.

---

### Phase 5: AI Integration Testing

#### 5.1 Verify .env File
```bash
cat .env
```

**Should contain:**
```
GEMINI_API_KEY=AIzaSyD98_A6mbQS9rZlz0e0ZWRlNPLZ-xWyMLw
LLM_PROVIDER=gemini
```

#### 5.2 Test AI Engine (if API key set)
```bash
python3 -c "
from ai_engine import AIEngine
engine = AIEngine()
print(f'API Key: {\"Set\" if engine.api_key else \"Not Set\"}')
print(f'Provider: {engine.provider}')
"
```

#### 5.3 Test Full Report with AI
```bash
python3 analyzer.py --full-report
cat report.md | grep -A 20 "AI Recommendations"
```

Should show AI-generated recommendations if API key is valid.

---

### Phase 6: Error Handling Testing

#### 6.1 Test Missing Scripts (should handle gracefully)
```bash
# Temporarily rename a script
mv bash/system_health.sh bash/system_health.sh.bak
python3 analyzer.py
# Should show error but continue
mv bash/system_health.sh.bak bash/system_health.sh
```

#### 6.2 Test Permission Issues
```bash
# Remove execute permission
chmod -x bash/system_health.sh
python3 analyzer.py
# Should still work (runs via bash explicitly)
chmod +x bash/system_health.sh
```

#### 6.3 Test Missing Logs (should handle gracefully)
```bash
# WSL may not have /var/log/auth.log - this is OK
python3 analyzer.py --logs
# Should show "log not found" but continue
```

---

## Test Scenarios

### Scenario 1: Fresh WSL Installation
```bash
# 1. Install Python
sudo apt-get update
sudo apt-get install python3 python3-pip

# 2. Install dependencies
cd /mnt/c/Users/user/SNA
pip3 install -r requirements.txt

# 3. Make scripts executable
chmod +x bash/*.sh

# 4. Run analyzer
python3 analyzer.py
```

### Scenario 2: High CPU Usage Test
```bash
# Generate some CPU load
stress-ng --cpu 2 --timeout 10s &

# Run analyzer (should detect high CPU)
python3 analyzer.py

# Should show HIGH or CRITICAL severity for CPU
```

### Scenario 3: Full Feature Test
```bash
# Run with all features
python3 analyzer.py --full-report

# Verify all sections in report
grep -E "^##" report.md
# Should show:
# ## System Health
# ## Users & Services
# ## Security Findings
# ## Log Analysis
# ## AI Recommendations
```

---

## Troubleshooting

### Issue: "python3: command not found"
**Solution:**
```bash
sudo apt-get install python3
```

### Issue: "ModuleNotFoundError: No module named 'dotenv'"
**Solution:**
```bash
pip3 install python-dotenv
```

### Issue: "Permission denied" for bash scripts
**Solution:**
```bash
chmod +x bash/*.sh
```

### Issue: "Error: Script not found"
**Solution:**
```bash
# Verify you're in the right directory
pwd
# Should be: /mnt/c/Users/user/SNA

# Check files exist
ls -la bash/
```

### Issue: "No output" or "Nothing happened"
**Solution:**
```bash
# Run with verbose error output
python3 analyzer.py 2>&1

# Check if scripts work manually
bash bash/system_health.sh
```

### Issue: Log files not found
**Solution:**
This is normal in WSL. The tool handles missing logs gracefully. To test with real logs, you'd need a full Linux installation or VM.

---

## Success Criteria

Your testing is successful if:

✅ All bash scripts execute and return JSON/text
✅ Python analyzer runs without errors
✅ Terminal summary displays correctly
✅ Markdown report generates
✅ Health metrics show real values
✅ Security checks work (SSH config)
✅ Log analysis handles missing files gracefully
✅ AI recommendations appear (if API key set)
✅ Error handling works (missing files, permissions)

---

## Quick Test Checklist

Run through this checklist:

```bash
# 1. Environment
[ ] python3 --version works
[ ] pip3 install -r requirements.txt succeeds
[ ] chmod +x bash/*.sh succeeds

# 2. Bash Scripts
[ ] bash bash/system_health.sh returns JSON
[ ] bash bash/users_services.sh returns JSON
[ ] bash bash/ssh_check.sh returns JSON
[ ] bash bash/log_extract.sh returns text

# 3. Python
[ ] python3 analyzer.py --help works
[ ] python3 analyzer.py shows summary
[ ] python3 analyzer.py --full-report generates report.md

# 4. Output
[ ] Terminal summary shows CPU, Memory, Disk
[ ] Terminal summary shows Security Configuration
[ ] report.md file exists and has content
[ ] report.md contains all sections

# 5. AI (if configured)
[ ] .env file exists with API key
[ ] AI recommendations appear in report.md
```

---

## Next Steps After Testing

Once testing is complete:

1. **Document any issues** you encounter
2. **Verify all features** work as expected
3. **Test on different systems** if possible
4. **Review the generated reports** for quality
5. **Prepare for submission** with all documentation

---

## Example Complete Test Run

```bash
# Complete test sequence
cd /mnt/c/Users/user/SNA

# Setup
bash test_setup.sh

# Individual components
bash bash/system_health.sh | head -20
bash bash/users_services.sh
bash bash/ssh_check.sh

# Full analyzer
python3 analyzer.py

# Full report
python3 analyzer.py --full-report
cat report.md

# Verify success
echo "✓ All tests completed!"
```

This comprehensive testing ensures your analyzer works correctly in WSL before submission.
