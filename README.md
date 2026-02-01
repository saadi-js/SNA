# AI-Assisted Linux Server Health & Log Analyzer

A read-only Linux system administration tool that audits basic server health, analyzes important system logs, and generates intelligent explanations and recommendations using an LLM API.

## Project Evolution

This tool evolved from a simple CPU monitoring script into a comprehensive system auditing tool. The original CPU collection logic was preserved and enhanced, then expanded with additional system metrics, security checks, log analysis, and AI-powered recommendations.

**Original State:** Single Python script displaying CPU usage percentage  
**Current State:** Modular CLI tool with health monitoring, security auditing, log analysis, and AI integration

See `PROJECT_EVOLUTION.md` for detailed evolution documentation.

## Project Purpose

This tool is designed for system administrators who need a quick, non-invasive way to:
- Assess server resource utilization (CPU, memory, disk)
- Review security configurations (SSH settings)
- Analyze system and authentication logs for anomalies
- Receive AI-powered explanations and actionable recommendations

**Important:** This tool performs **read-only** operations. It does not modify system state or execute any destructive actions.

## System Administration Concepts Covered

### 1. System Health Monitoring
- **CPU Usage**: Load average and percentage utilization
- **Memory Usage**: Total, used, available memory and percentage
- **Disk Usage**: Filesystem utilization for root partition

### 2. User & Service Management
- Active user sessions
- Running system services (systemd)
- Service status monitoring

### 3. Security Auditing
- SSH configuration analysis:
  - Root login permissions
  - Password authentication settings
- Authentication log analysis:
  - Failed login attempts
  - Brute force detection
- Permission denial tracking

### 4. Log Analysis
- Pattern matching in authentication logs (`/var/log/auth.log` or `/var/log/secure`)
- System error log analysis (`/var/log/syslog` or `/var/log/messages`)
- Service error detection
- Segmentation fault tracking

### 5. Rule-Based Analysis
The tool uses predefined rules to assess severity:
- **CPU > 90%**: CRITICAL
- **CPU > 80%**: HIGH
- **Memory > 90%**: CRITICAL
- **Memory > 80%**: HIGH
- **Disk > 90%**: CRITICAL
- **Disk > 85%**: HIGH
- **Disk > 75%**: MEDIUM
- **Failed SSH logins > 20**: HIGH security risk
- **Root SSH enabled**: HIGH security risk
- **Password auth enabled**: MEDIUM security risk

## Requirements

- **Operating System**: Linux (Ubuntu/Debian preferred)
- **Python**: Python 3.6 or higher
- **Bash**: Standard bash shell
- **Permissions**: Read access to system logs (may require sudo for some log files)
- **Optional**: LLM API key for AI recommendations (Gemini, OpenAI, or Anthropic)

## Installation

1. Clone or download this project:
```bash
git clone <repository-url>
cd SNA
```

2. Make bash scripts executable:
```bash
chmod +x bash/*.sh
```

3. Install Python dependencies:
```bash
# Install required packages (includes python-dotenv for .env file support)
pip install -r requirements.txt

# Or install individually:
pip install python-dotenv google-generativeai
```

4. Configure API key (choose one method):

**Method 1: Using .env file (Recommended)**
```bash
# The .env file is already created with your Gemini API key
# Just ensure it exists in the project root directory
# .env file format:
# GEMINI_API_KEY=your-api-key-here
# LLM_PROVIDER=gemini
```

**Method 2: Environment variables**
```bash
# For Gemini (default)
export GEMINI_API_KEY="your-api-key-here"
export LLM_PROVIDER="gemini"

# For OpenAI
export OPENAI_API_KEY="your-api-key-here"
export LLM_PROVIDER="openai"

# For Anthropic
export ANTHROPIC_API_KEY="your-api-key-here"
export LLM_PROVIDER="anthropic"
```

## Usage

### Basic Usage

Run the analyzer with default settings (includes all checks):
```bash
python analyzer.py
```

### CLI Options

```bash
python analyzer.py [OPTIONS]
```

**Options:**
- `--summary`: Display terminal summary only (default behavior)
- `--full-report`: Generate markdown report file (`report.md`)
- `--logs`: Include log analysis (enabled by default)
- `--health`: Include health analysis (enabled by default)

### Examples

**Terminal summary only:**
```bash
python analyzer.py --summary
```

**Generate full report with AI recommendations:**
```bash
python analyzer.py --full-report
```

**Health check only (no logs):**
```bash
python analyzer.py --health --no-logs
```

**Log analysis only:**
```bash
python analyzer.py --logs --no-health
```

## Sample Output

### Terminal Summary

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
  SSH Root Login:      ENABLED ⚠️
  SSH Password Auth:   ENABLED ⚠️

Key Findings:
  🟠 [HIGH] SSH Root Login: Root login via SSH is enabled. This is a security risk.
  🟡 [MEDIUM] SSH Password Auth: Password authentication is enabled. Consider using key-based authentication.
  🟡 [MEDIUM] Disk Usage: Disk usage is moderately elevated at 82%
  🟡 [MEDIUM] Failed SSH Logins: Multiple failed SSH login attempts (15) detected.

============================================================
```

### Markdown Report

The `--full-report` option generates a `report.md` file with:
- System Health metrics
- Users & Services information
- Security Findings
- Log Analysis summary
- AI Recommendations (if API key is configured)

## Project Structure

```
project/
├── bash/
│   ├── system_health.sh      # CPU, memory, disk collection
│   ├── users_services.sh      # Users and services collection
│   ├── ssh_check.sh           # SSH configuration checks
│   └── log_extract.sh         # Log extraction
├── analyzer.py                # Main analyzer script
├── ai_engine.py               # LLM integration module
├── report.md                  # Generated report (after --full-report)
└── README.md                  # This file
```

## How It Works

1. **Data Collection**: Bash scripts collect system information and output JSON or structured text
2. **Parsing**: Python analyzer parses outputs into structured data
3. **Rule-Based Analysis**: Predefined rules assess severity levels
4. **Log Pattern Matching**: Logs are analyzed for patterns (no raw logs sent to LLM)
5. **AI Integration**: Summarized data is sent to LLM API for explanations and recommendations
6. **Output**: Results displayed in terminal and/or saved to markdown report

## Limitations

### Read-Only Operations
- This tool **never modifies** system state
- All operations are read-only
- No configuration changes are made
- No services are started/stopped

### Simplified Scope
- Focuses on basic health metrics (CPU, memory, disk)
- Limited to common log locations
- Basic SSH configuration checks only
- No network analysis
- No advanced security scanning

### Log Access
- Some log files may require `sudo` permissions
- Log locations vary by distribution (handles common paths)
- Large log files may take time to process

### AI Features
- Requires API key and internet connection
- Falls back gracefully if API unavailable
- Uses rule-based recommendations as backup

### Platform Support
- Designed for Linux (Ubuntu/Debian)
- May work on other distributions with minor adjustments
- Bash scripts assume standard Linux utilities

## Security Considerations

- **No Data Transmission**: Raw logs are never sent to LLM APIs
- **Summarized Data Only**: Only metrics and counts are transmitted
- **Read-Only**: Tool cannot modify system configuration
- **Local Processing**: All analysis happens locally

## Troubleshooting

### Permission Errors
If you see permission errors for log files:
```bash
sudo python analyzer.py
```

### Script Not Found
Ensure bash scripts are executable:
```bash
chmod +x bash/*.sh
```

### JSON Parse Errors
Some systems may have different command outputs. Check bash script compatibility with your distribution.

### AI Recommendations Not Working
- Verify API key is set: `echo $OPENAI_API_KEY`
- Check internet connectivity
- Tool will work without AI features (rule-based recommendations only)

## Contributing

This is an educational project. Suggestions for improvements are welcome, but please maintain:
- Read-only operation principle
- Clean, readable code
- Clear documentation
- Focus on correctness over features

## License

This project is provided as-is for educational and administrative purposes.

## Author Notes

This tool was designed as a university-level System & Network Administration project, focusing on:
- Correctness of system administration concepts
- Relevance to real-world scenarios
- Clarity of implementation and documentation
- Safety and non-destructive behavior

---

**Remember**: This is an auditing tool. Always verify findings manually before taking action on production systems.
