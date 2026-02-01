# Baseline Usage Guide

## Step 1: List Available Baselines

First, see what baselines you have:

```bash
python3 analyzer_new.py baseline list
```

This will show output like:
```
Available baselines:
  - baseline_20240201_120000
  - baseline_20240201_150000
```

## Step 2: Save a Baseline (if needed)

If you don't have a baseline yet, save one:

```bash
python3 analyzer_new.py baseline save
```

Or with a custom name:

```bash
python3 analyzer_new.py baseline save --name production
```

## Step 3: Compare with Baseline

Use the exact baseline name from the list:

```bash
python3 analyzer_new.py baseline compare baseline_20240201_120000
```

**Important:** Replace `baseline_20240201_120000` with the actual baseline name from your list.

## Example Workflow

```bash
# 1. Save initial baseline
python3 analyzer_new.py baseline save

# 2. List baselines to get the name
python3 analyzer_new.py baseline list
# Output: baseline_20240201_143022

# 3. Make some system changes...

# 4. Compare current state with baseline
python3 analyzer_new.py baseline compare baseline_20240201_143022
```

## Common Errors

### Error: "Baseline name required"
- You forgot to provide the baseline name
- Use: `python3 analyzer_new.py baseline compare <actual_name>`

### Error: "Baseline 'xxx' not found"
- The baseline name doesn't exist
- Run `python3 analyzer_new.py baseline list` to see available baselines
- Use the exact name from the list

### Error: "syntax error near unexpected token"
- You used `<timestamp>` literally instead of the actual name
- Always use the exact baseline name from the list command
