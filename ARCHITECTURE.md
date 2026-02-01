# System Architecture: AI-Assisted Linux Server Health & Log Analyzer

## Overview

This document explains the architecture and design decisions of the system analyzer, showing how it evolved from a simple CPU monitor to a comprehensive auditing tool.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLI Entry Point (analyzer.py)                │
│                         python analyzer.py                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              SystemAnalyzer Class (Orchestration)               │
│  • Platform detection (Linux/Windows/WSL)                        │
│  • Bash script execution                                         │
│  • Data collection coordination                                  │
│  • Rule-based analysis                                          │
│  • Report generation                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ↓                    ↓                    ↓
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Bash Data     │  │ Bash Data    │  │ Bash Data     │
│ Collectors   │  │ Collectors   │  │ Collectors   │
│               │  │              │  │              │
│ system_health │  │ users_       │  │ ssh_check    │
│ .sh           │  │ services.sh  │  │ .sh          │
│               │  │              │  │              │
│ • CPU         │  │ • Users      │  │ • SSH config │
│ • Memory      │  │ • Services   │  │ • Security   │
│ • Disk        │  │              │  │   settings   │
└───────┬───────┘  └───────┬──────┘  └───────┬──────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ↓
                ┌──────────────────────┐
                │  JSON Data Parsing    │
                │  (Python analyzer.py) │
                └──────────┬───────────┘
                           │
                           ↓
                ┌──────────────────────┐
                │  Rule-Based Analysis  │
                │  • Severity levels    │
                │  • Threshold checks   │
                │  • Pattern matching  │
                └──────────┬───────────┘
                           │
                           ↓
                ┌──────────────────────┐
                │  Log Analysis         │
                │  • Pattern detection │
                │  • Summarization     │
                │  • No raw logs      │
                └──────────┬───────────┘
                           │
                           ↓
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ↓                  ↓                  ↓
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ AI Engine     │  │ Terminal      │  │ Markdown      │
│ (ai_engine.py)│  │ Output        │  │ Report        │
│               │  │               │  │ (report.md)   │
│ • LLM API     │  │ • Summary     │  │ • Full report│
│ • Explanations│  │ • Findings    │  │ • AI insights│
│ • Recommendations│ • Severity    │  │ • Details     │
└───────────────┘  └───────────────┘  └───────────────┘
```

## Component Details

### 1. Bash Data Collectors

**Purpose:** Collect raw system data using standard Linux commands

**Files:**
- `bash/system_health.sh` - CPU, memory, disk metrics
- `bash/users_services.sh` - User sessions and service status
- `bash/ssh_check.sh` - SSH configuration security checks
- `bash/log_extract.sh` - Authentication and system logs

**Design Decision:** Why Bash?
- Standard sysadmin tooling
- Efficient command execution
- Easy to test independently
- Follows Unix philosophy
- Can be run manually for debugging

**Output Format:** JSON (for easy parsing) or structured text

### 2. Python Core Engine (analyzer.py)

**Purpose:** Orchestrate data collection, parse outputs, perform analysis

**Key Classes:**
- `SystemAnalyzer` - Main orchestrator class

**Key Methods:**
- `run_bash_script()` - Execute bash scripts with platform detection
- `collect_system_health()` - Parse health metrics JSON
- `collect_users_services()` - Parse user/service data
- `collect_ssh_config()` - Parse SSH configuration
- `collect_logs()` - Get log text
- `analyze_logs()` - Pattern matching and summarization
- `rule_based_analysis()` - Apply severity thresholds
- `print_summary()` - Terminal output formatting
- `generate_markdown_report()` - Markdown report generation

**Design Decision:** Why Python?
- Excellent for data parsing and manipulation
- Good subprocess handling
- Easy JSON processing
- Clean CLI argument parsing
- Good for structured analysis logic

### 3. AI Engine (ai_engine.py)

**Purpose:** Generate intelligent explanations and recommendations

**Key Features:**
- Abstracted LLM interface (supports Gemini, OpenAI, Anthropic)
- Sends summarized data (never raw logs)
- Graceful fallback if API unavailable
- System administrator tone in prompts

**Design Decision:** Why Abstracted?
- Easy to switch LLM providers
- Graceful degradation
- No hard dependencies
- Testable without API keys

### 4. Rule-Based Analysis

**Purpose:** Apply predefined thresholds and severity levels

**CPU Thresholds:**
- > 90% → CRITICAL
- > 80% → HIGH (preserved from original)
- > 60% → MEDIUM

**Memory Thresholds:**
- > 90% → CRITICAL
- > 80% → HIGH
- > 75% → MEDIUM

**Disk Thresholds:**
- > 90% → CRITICAL
- > 85% → HIGH
- > 75% → MEDIUM

**Security Thresholds:**
- Root SSH enabled → HIGH
- Password auth enabled → MEDIUM
- Failed logins > 20 → HIGH

**Design Decision:** Why Rule-Based First?
- Fast and deterministic
- No API dependency
- Clear, explainable results
- Works offline
- AI enhances but doesn't replace

## Data Flow

### Collection Phase
```
Bash Script → subprocess.run() → stdout → JSON.parse() → Python dict
```

### Analysis Phase
```
Python dict → rule_based_analysis() → findings dict → severity levels
```

### Intelligence Phase
```
findings dict → AI engine → summarized context → LLM API → recommendations
```

### Output Phase
```
findings + recommendations → print_summary() → terminal
findings + recommendations → generate_markdown_report() → report.md
```

## Platform Support

### Linux (Native)
- Direct bash execution
- Full feature support
- All log files accessible (with sudo)

### Windows + WSL
- Detects WSL automatically
- Converts paths (C:\ → /mnt/c/)
- Executes scripts via WSL
- Full feature support

### Windows (No WSL)
- Shows helpful error message
- Suggests WSL installation
- Graceful failure

## Security Considerations

1. **Read-Only Operations**
   - No file modifications
   - No service management
   - No configuration changes
   - Pure auditing

2. **Log Privacy**
   - Raw logs never sent to LLM
   - Only summarized metrics
   - Pattern counts, not content

3. **Permission Handling**
   - Graceful degradation if files inaccessible
   - Clear error messages
   - Suggests sudo when needed

## Extensibility

### Adding New Metrics

1. Create bash script in `bash/` directory
2. Output JSON format
3. Add collection method in `SystemAnalyzer`
4. Add parsing logic
5. Add rule-based thresholds
6. Update report generation

### Adding New LLM Provider

1. Add API key detection in `AIEngine.__init__()`
2. Add `_call_provider()` method
3. Update provider selection logic
4. Test with fallback

## Performance Considerations

- **Bash Scripts:** Fast, native command execution
- **JSON Parsing:** Efficient Python json module
- **Rule Analysis:** O(n) complexity, very fast
- **AI Calls:** Async-capable (future enhancement)
- **Report Generation:** In-memory string building

## Error Handling Strategy

1. **Bash Script Failures:** Return empty dict, continue
2. **JSON Parse Errors:** Log error, use defaults
3. **Missing Files:** Graceful degradation
4. **API Failures:** Fallback to rule-based recommendations
5. **Permission Errors:** Clear messages, suggest sudo

## Testing Strategy

1. **Bash Scripts:** Test independently with sample data
2. **Python Parsing:** Unit tests with mock JSON
3. **Rule Analysis:** Test with known thresholds
4. **AI Engine:** Mock API responses
5. **Integration:** End-to-end on test Linux system

## Future Enhancements (Out of Scope for 3-Day Project)

- Network interface monitoring
- Process-level analysis
- Historical trending
- Alerting system
- Web dashboard (explicitly excluded per requirements)
- Auto-remediation (explicitly excluded per requirements)
