# Quick Test Guide - Enhanced Analyzer

## Step-by-Step Testing

### 1. Open WSL Terminal
```bash
wsl
```

### 2. Navigate to Project
```bash
cd /mnt/c/Users/user/SNA
```

### 3. Run the Analyzer
```bash
python3 analyzer.py
```

## What You Should See

The output should now include **ALL** of these sections:

✅ **System Health** (with status indicators)
✅ **Security Configuration**
✅ **Log Intelligence** (NEW SECTION)
✅ **Key Findings** (expanded, multi-line)
✅ **AI Analysis** (always shown)

## Expected Output Format

```
============================================================
Linux Server Health & Security Analysis
============================================================
Analysis Date: 2024-XX-XX XX:XX:XX
Overall Severity: LOW/MEDIUM/HIGH/CRITICAL

System Health:
  CPU Usage:    XX.X% [OK/MEDIUM/HIGH/CRITICAL]
  Memory Usage: XX.X% [OK/MEDIUM/HIGH/CRITICAL]
  Disk Usage:   XX% [OK/MEDIUM/HIGH/CRITICAL]

Security Configuration:
  SSH Root Login:            Disabled [OK]
  SSH Password Authentication: Disabled [OK]

Log Intelligence:
  Authentication Failures: X [OK/LOW/MEDIUM/HIGH]
  [Service Errors: service1, service2 [MEDIUM] - if any]
  [Kernel Errors: X [HIGH] - if any]

Key Findings:
  [SEVERITY] Title
    • Description text (multi-line)

AI Analysis:
  Analysis text here (always present)

============================================================
```

## Verify Each Feature

### ✅ Check 1: Status Indicators
Look for `[OK]`, `[MEDIUM]`, `[HIGH]`, or `[CRITICAL]` after each metric.

### ✅ Check 2: Log Intelligence Section
Should appear between Security Configuration and Key Findings.

### ✅ Check 3: Expanded Findings
Findings should be multi-line with:
- Severity label
- Title
- Bullet point description

### ✅ Check 4: AI Analysis
Should always appear at the end, even if it's fallback text.

## Test with Full Report

```bash
python3 analyzer.py --full-report
cat report.md
```

The markdown report should also contain all sections.

## Troubleshooting

### If Log Intelligence section is missing:
- Check if logs are being collected: `bash bash/log_extract.sh`
- The section will show "No significant log anomalies detected [OK]" if no issues

### If AI Analysis is missing:
- Check if `.env` file exists: `cat .env`
- Fallback analysis should still appear

### If findings are still one-line:
- Make sure you're running the latest version
- Check: `python3 analyzer.py --help` should work

## Quick Verification Commands

```bash
# 1. Test log extraction
bash bash/log_extract.sh | head -20

# 2. Test analyzer
python3 analyzer.py

# 3. Check for all required sections
python3 analyzer.py | grep -E "Log Intelligence|AI Analysis|Key Findings"

# 4. Generate full report
python3 analyzer.py --full-report && cat report.md | head -50
```

## Success Criteria

Your test is successful if you see:

1. ✅ Status indicators on health metrics
2. ✅ "Log Intelligence:" section visible
3. ✅ Multi-line findings with bullet points
4. ✅ "AI Analysis:" section at the end
5. ✅ Output looks professional and comprehensive (not like a basic CPU monitor)

---

**Ready to test? Run: `python3 analyzer.py`**
