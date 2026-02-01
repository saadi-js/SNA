# SNA - Usage Guide

## Multi-Command CLI Interface

### Full System Audit
```bash
python analyzer_new.py audit
python analyzer_new.py audit --full    # Include process snapshot
python analyzer_new.py audit --json    # Output as JSON
```

### Security Audit
```bash
python analyzer_new.py security
```

### Log Intelligence
```bash
python analyzer_new.py logs
```

### Baseline Management
```bash
# Save current system state
python analyzer_new.py baseline save
python analyzer_new.py baseline save --name production

# Compare with baseline
python analyzer_new.py baseline compare --name baseline_20240201_120000

# List all baselines
python analyzer_new.py baseline list
```

## Features

✅ Multi-command CLI interface
✅ Modular architecture (sna/core, sna/baseline, sna/utils)
✅ Severity scoring engine
✅ Baseline save/compare functionality
✅ Process snapshot (with --full flag)
✅ Recommendations engine
✅ JSON export (--json flag)
✅ Offline-first (no cloud dependency)

## Migration

The new modular version is in `analyzer_new.py`. To use it:

1. Test: `python analyzer_new.py audit`
2. Once verified, you can rename: `mv analyzer.py analyzer_old.py && mv analyzer_new.py analyzer.py`
