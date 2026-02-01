#!/bin/bash
# Quick Test Script - Run all basic tests in sequence

echo "=========================================="
echo "  Quick Test: System Health Analyzer"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to test and report
test_step() {
    local name=$1
    local command=$2
    
    echo -n "Testing: $name... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

# 1. Check Python
test_step "Python Installation" "python3 --version"

# 2. Check dependencies
test_step "Python Dependencies" "python3 -c 'import json, subprocess, sys, os, re, argparse, platform, shutil'"

# 3. Check bash scripts exist
test_step "Bash Scripts Exist" "[ -f bash/system_health.sh ] && [ -f bash/users_services.sh ] && [ -f bash/ssh_check.sh ] && [ -f bash/log_extract.sh ]"

# 4. Check Python files exist
test_step "Python Files Exist" "[ -f analyzer.py ] && [ -f ai_engine.py ]"

# 5. Test bash script execution
test_step "System Health Script" "bash bash/system_health.sh | grep -q 'cpu'"

# 6. Test users/services script
test_step "Users/Services Script" "bash bash/users_services.sh | grep -q 'users'"

# 7. Test SSH check script
test_step "SSH Check Script" "bash bash/ssh_check.sh | grep -q 'ssh'"

# 8. Test Python analyzer help
test_step "Analyzer Help Command" "python3 analyzer.py --help | grep -q 'usage'"

# 9. Test analyzer execution (quick)
test_step "Analyzer Execution" "timeout 10 python3 analyzer.py --summary 2>&1 | grep -q 'Linux Server Health'"

# 10. Test report generation
test_step "Report Generation" "python3 analyzer.py --full-report 2>&1 | grep -q 'Report generated' || [ -f report.md ]"

echo ""
echo "=========================================="
echo "  Test Results"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run full analyzer: python3 analyzer.py"
    echo "  2. Generate report: python3 analyzer.py --full-report"
    echo "  3. View report: cat report.md"
    exit 0
else
    echo -e "${YELLOW}⚠ Some tests failed. Check the output above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Install Python: sudo apt-get install python3 python3-pip"
    echo "  - Install dependencies: pip3 install -r requirements.txt"
    echo "  - Make scripts executable: chmod +x bash/*.sh"
    exit 1
fi
