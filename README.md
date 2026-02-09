# AI-Assisted Linux Server Health & Log Analyzer

A comprehensive Linux system administration tool that provides both traditional audit capabilities and an **interactive natural language shell** for real-time system monitoring, security auditing, and intelligent recommendations using AI.

## Project Evolution

This tool evolved from a simple CPU monitoring script into a comprehensive system auditing tool with an interactive shell interface.

**Original State:** Single Python script displaying CPU usage percentage  
**Current State:** 
- Modular CLI tool with health monitoring, security auditing, log analysis, and AI integration
- **Interactive Shell** with natural language commands for real-time monitoring and analysis
- Advanced features including predictive analytics, multi-node monitoring, and automated remediation

See `PROJECT_EVOLUTION.md` for detailed evolution documentation.

## Key Features

### Traditional CLI Auditing
- System health monitoring (CPU, memory, disk)
- Security configuration analysis (SSH, firewall)
- Log analysis and pattern detection
- Baseline comparison and trend analysis
- AI-powered recommendations

### Interactive Shell ⭐ NEW
An intelligent command interface that accepts natural language queries:
- **Real-time monitoring**: Monitor logs, CPU, memory, disk, and network activity as they happen
- **Security auditing**: Check firewall rules, scan vulnerabilities, monitor file integrity
- **Predictive analytics**: Analyze trends in resource usage
- **Multi-node monitoring**: Monitor cluster nodes simultaneously
- **Automated remediation**: Restart failed services, terminate high-CPU processes
- **Advanced reporting**: Export reports in multiple formats (JSON, CSV, PDF)
- **User management**: Role-based access control (RBAC)
- **Plugin system**: Extend functionality with custom plugins
- **Real-time visualization**: Interactive graphs for resource usage
- **Backup & restore**: Configuration management
- **AI insights**: Get intelligent recommendations on-demand

## Updated Features

### User Management
- Add, remove, and list users.
- Role-based access control (RBAC).

### System Health Check
- Run a comprehensive health check for CPU, memory, disk, and network.
- Display a detailed system health report.

### Plugin Management
- Load, unload, and update plugins dynamically.
- List all currently loaded plugins.

### Backup Management
- List all available backups.
- Delete specific backups.

### Language Support
- Set the language for the interactive shell (supports `en`, `es`, `fr`).
- Future support for additional languages.

### Enhanced Commands
- **Disk Usage**: Fetch detailed disk usage metrics.
- **Firewall Check**: Display and manage firewall rules.
- **Vulnerability Scan**: Scan for vulnerabilities using `nmap`.
- **Log Monitoring**: Monitor logs with real-time updates.
- **Visualization**: Generate interactive graphs for resource usage.

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

- **Operating System**: Linux (Ubuntu/Debian preferred, works in WSL on Windows)
- **Python**: Python 3.6 or higher
- **Bash**: Standard bash shell
- **Permissions**: Read access to system logs (may require sudo for some log files)
- **Optional**: LLM API key for AI recommendations (Gemini, OpenAI, or Anthropic)

### Python Dependencies
- `python-dotenv` - Environment variable management
- `google-generativeai` - Google Gemini API (or `openai`/`anthropic` for alternatives)
- `psutil` - System monitoring
- `watchdog` - Real-time file monitoring
- `matplotlib` - Data visualization

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

# FoInteractive Shell (Recommended)

Launch the interactive shell for natural language queries:

```bash
python interactive_shell.py
```

Once in the shell, you can use natural language commands:

```
> show cpu usage
> show system logs
> monitor logs
> check firewall
> scan vulnerabilities
> predict cpu trends
> monitor cluster
> restart failed services
> export report
> send alert
> visualize cpu usage
> get ai recommendations
> help
> exit
```

**Example Session:**
```
Welcome to the Interactive Shell! Type 'help' for available commands.

> show cpu usage
Fetching CPU usage...
CPU Load Average: 0.45
CPU Usage: 23.4%

> monitor logs
Enter the path to the log file to monitor: /var/log/auth.log
Monitoring log file: /var/log/auth.log
[Real-time log entries displayed here...]
Press Ctrl+C to stop monitoring

> get ai recommendations
Fetching AI-powered recommendations...
Recommendations:
- Optimize CPU-intensive processes.
- Schedule regular system audits.
```

### Traditional CLI Auditing

Run the analyzer with command-line options:

```bash
# Basic audit
python analyzer_new.py audit

# Full audit with process snapshot
python analyzer_new.py audit --full

# Export to JSON
python analyzer_new.py audit --json

# Save/compare baseline
python analyzer_new.py baseline save
python analyzer_new.py baseline compare
```

### WSL Usage

On Windows with WSL:

```bash
# Open WSL terminal
wsl

# Navigate to project
cd /mnt/c/Users/user/SNA

# Run interactive shell
python3 interactive_shell.py

# Or run traditional audit
python3 analyzer_new.py audit
```bash
python analyzer.py --health --no-logs
```

**Log analysis only:**
SNA/
├── bash/                           # System data collection scripts
│   ├── system_health.sh            # CPU, memory, disk collection
│   ├── users_services.sh           # Users and services collection
│   ├── ssh_check.sh                # SSH configuration checks
│   └── log_extract.sh              # Log extraction
├── sna/                            # Main Python package
│   ├── baseline/                   # Baseline management
│   │   └── baseline_manager.py
│   ├── core/                       # Core analysis modules
│   │   ├── logs.py                 # Log analysis
│   │   ├── processes.py            # Process monitoring
│   │   ├── recommendations.py      # Recommendations engine
│   │   ├── scoring.py              # Risk scoring
│   │   ├── security.py             # Security checks
│   │   └── system_health.py        # Health monitoring
│   └── utils/                      # Utility modules
│       ├── command_runner.py       # Command execution
│       ├── os_detect.py            # OS detection
│       └── output.py               # Output formatting
├── interactive_shell.py            # Interactive natural language shell ⭐
├── analyzer_new.py                 # Modern CLI analyzer
├── analyzer.py                     # Legacy analyzer (backup)
├── ai_engine.py                    # LLM integration module
├── requirements.txt                # Python dependencies
└── README.md     ===============================================
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
