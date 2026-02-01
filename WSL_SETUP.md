# WSL Setup Guide for Linux Server Health Analyzer

## Quick Start

1. **Open WSL terminal** (Ubuntu or your Linux distribution)

2. **Navigate to your project**:
   ```bash
   cd /mnt/c/Users/user/SNA
   ```

3. **Run the setup test**:
   ```bash
   bash test_setup.sh
   ```

4. **If setup passes, run the analyzer**:
   ```bash
   python3 analyzer.py
   ```

## Common Issues and Solutions

### Issue 1: "python: command not found"

**Solution:**
```bash
# Install Python 3
sudo apt-get update
sudo apt-get install python3 python3-pip
```

### Issue 2: "bash scripts not executable"

**Solution:**
```bash
chmod +x bash/*.sh
```

### Issue 3: "Module not found" errors

**Solution:**
```bash
# Install required packages
pip3 install python-dotenv google-generativeai

# Or install from requirements.txt
pip3 install -r requirements.txt
```

### Issue 4: "Permission denied" for log files

**Solution:**
```bash
# Run with sudo (for log access)
sudo python3 analyzer.py
```

### Issue 5: Script runs but shows no output

**Check:**
1. Are you in the correct directory?
   ```bash
   pwd
   ls -la
   ```

2. Try running with verbose output:
   ```bash
   python3 analyzer.py --summary 2>&1
   ```

3. Check if scripts are working:
   ```bash
   bash bash/system_health.sh
   ```

### Issue 6: "Nothing happened" - Silent failure

**Debug steps:**
```bash
# 1. Check Python version
python3 --version

# 2. Test if analyzer imports correctly
python3 -c "import analyzer; print('OK')"

# 3. Run with explicit error output
python3 analyzer.py 2>&1 | tee output.log

# 4. Check the output log
cat output.log
```

## Step-by-Step Setup

### 1. Verify WSL is working
```bash
uname -a
# Should show Linux kernel version
```

### 2. Install Python (if needed)
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip
```

### 3. Install dependencies
```bash
cd /mnt/c/Users/user/SNA
pip3 install python-dotenv google-generativeai
```

### 4. Make scripts executable
```bash
chmod +x bash/*.sh
```

### 5. Test a bash script manually
```bash
bash bash/system_health.sh
# Should output JSON with CPU, memory, disk info
```

### 6. Run the analyzer
```bash
python3 analyzer.py
```

## Expected Output

When working correctly, you should see:

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

## Getting Help

If you're still having issues:

1. **Check the error messages** - they usually tell you what's wrong
2. **Run the test script**: `bash test_setup.sh`
3. **Check file permissions**: `ls -la bash/*.sh`
4. **Verify Python can import modules**: `python3 -c "import sys; print(sys.path)"`

## Notes

- WSL uses Linux, so the tool should work the same as on a native Linux system
- Some log files might not exist in WSL (like `/var/log/auth.log`)
- The tool will gracefully handle missing log files
- You may need `sudo` for some operations
