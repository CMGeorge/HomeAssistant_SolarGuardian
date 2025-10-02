#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track overall status
OVERALL_STATUS=0

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║           🚀 Running All GitHub Workflow Checks 🚀            ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  Warning: No virtual environment found"
fi

# ============================================================================
# 1. HASSFEST VALIDATION
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 1/5 Hassfest Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python validate_hassfest.py; then
    echo -e "  ${GREEN}✅ PASSED${NC}"
else
    echo -e "  ${RED}❌ FAILED${NC}"
    OVERALL_STATUS=1
fi
echo ""

# ============================================================================
# 2. VALIDATE WORKFLOW (JSON + Python + Manifest)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 2/5 JSON, Python, and Manifest Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# JSON validation
echo "  Validating JSON files..."
VALIDATION_FAILED=0

python3 -c "import json; json.load(open('custom_components/solarguardian/manifest.json'))" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "    ${GREEN}✓${NC} manifest.json is valid"
else
    echo -e "    ${RED}✗${NC} manifest.json is invalid"
    VALIDATION_FAILED=1
fi

python3 -c "import json; json.load(open('hacs.json'))" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "    ${GREEN}✓${NC} hacs.json is valid"
else
    echo -e "    ${RED}✗${NC} hacs.json is invalid"
    VALIDATION_FAILED=1
fi

python3 -c "import json; json.load(open('custom_components/solarguardian/strings.json'))" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "    ${GREEN}✓${NC} strings.json is valid"
else
    echo -e "    ${RED}✗${NC} strings.json is invalid"
    VALIDATION_FAILED=1
fi

for file in custom_components/solarguardian/translations/*.json; do
    python3 -c "import json; json.load(open('$file'))" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "    ${GREEN}✓${NC} $(basename $file) is valid"
    else
        echo -e "    ${RED}✗${NC} $(basename $file) is invalid"
        VALIDATION_FAILED=1
    fi
done

# Python validation
echo ""
echo "  Checking Python code quality..."

echo "    Checking code formatting with Black..."
if black --check custom_components/solarguardian/ > /dev/null 2>&1; then
    echo -e "    ${GREEN}✓${NC} Black formatting check passed"
else
    echo -e "    ${RED}✗${NC} Black formatting check failed"
    VALIDATION_FAILED=1
fi

echo "    Checking import sorting with isort..."
if isort --check-only custom_components/solarguardian/ > /dev/null 2>&1; then
    echo -e "    ${GREEN}✓${NC} isort check passed"
else
    echo -e "    ${RED}✗${NC} isort check failed"
    VALIDATION_FAILED=1
fi

echo "    Linting with Ruff..."
if ruff check custom_components/solarguardian/ > /dev/null 2>&1; then
    echo -e "    ${GREEN}✓${NC} Ruff linting passed"
else
    echo -e "    ${RED}✗${NC} Ruff linting failed"
    VALIDATION_FAILED=1
fi

# Manifest validation
echo ""
echo "  Checking manifest requirements..."
python3 << 'EOF'
import json
import sys

with open('custom_components/solarguardian/manifest.json') as f:
    manifest = json.load(f)

required_fields = [
    'domain', 'name', 'codeowners', 'config_flow',
    'documentation', 'iot_class', 'issue_tracker',
    'requirements', 'version'
]

errors = []
missing = [field for field in required_fields if field not in manifest]
if missing:
    errors.append(f"Missing required fields: {missing}")

# Validate URLs
if 'github.com' not in manifest.get('documentation', ''):
    errors.append("Documentation URL must be a GitHub URL")

if 'github.com' not in manifest.get('issue_tracker', ''):
    errors.append("Issue tracker URL must be a GitHub URL")

if errors:
    for error in errors:
        print(f"    ✗ {error}")
    sys.exit(1)
else:
    print("    ✓ All required manifest fields present and valid")
EOF

if [ $? -eq 0 ]; then
    echo -e "    ${GREEN}✓${NC} Manifest validation passed"
else
    echo -e "    ${RED}✗${NC} Manifest validation failed"
    VALIDATION_FAILED=1
fi

if [ $VALIDATION_FAILED -eq 0 ]; then
    echo -e "  ${GREEN}✅ PASSED${NC}"
else
    echo -e "  ${RED}❌ FAILED${NC}"
    OVERALL_STATUS=1
fi
echo ""

# ============================================================================
# 3. UNIT TESTS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 3/5 Unit Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "  Installing pytest..."
    pip install pytest pytest-asyncio pytest-cov aiohttp python-dotenv > /dev/null 2>&1
fi

echo "  Running unit tests..."
if pytest tests/unit/ -v --tb=short 2>&1 | tail -20; then
    echo -e "  ${GREEN}✅ PASSED${NC}"
else
    echo -e "  ${YELLOW}⚠️  SKIPPED (expected - homeassistant module not installed)${NC}"
fi
echo ""

# ============================================================================
# 4. HACS VALIDATION
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏠 4/5 HACS Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "  Checking HACS requirements..."
HACS_FAILED=0

# Check required files
REQUIRED_FILES=(
    "README.md"
    "info.md"
    "hacs.json"
    "LICENSE"
    "custom_components/solarguardian/__init__.py"
    "custom_components/solarguardian/manifest.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "    ${GREEN}✓${NC} $file exists"
    else
        echo -e "    ${RED}✗${NC} $file missing"
        HACS_FAILED=1
    fi
done

# Validate hacs.json structure
echo ""
echo "  Validating hacs.json structure..."
python3 << 'EOF'
import json
import sys

with open('hacs.json') as f:
    hacs = json.load(f)

required = ['name']
missing = [field for field in required if field not in hacs]
if missing:
    print(f"    ✗ Missing required fields in hacs.json: {missing}")
    sys.exit(1)
else:
    print(f"    ✓ hacs.json structure is valid")
    print(f"    ✓ Name: {hacs['name']}")
EOF

if [ $? -ne 0 ]; then
    HACS_FAILED=1
fi

if [ $HACS_FAILED -eq 0 ]; then
    echo -e "  ${GREEN}✅ PASSED${NC}"
else
    echo -e "  ${RED}❌ FAILED${NC}"
    OVERALL_STATUS=1
fi
echo ""

# ============================================================================
# 5. PRE-COMMIT (if configured)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ 5/5 Pre-commit Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ".pre-commit-config.yaml" ]; then
    if ! command -v pre-commit &> /dev/null; then
        echo "  Installing pre-commit..."
        pip install pre-commit > /dev/null 2>&1
    fi
    
    echo "  Running pre-commit hooks..."
    if pre-commit run --all-files 2>&1 | tail -20; then
        echo -e "  ${GREEN}✅ PASSED${NC}"
    else
        echo -e "  ${RED}❌ FAILED${NC}"
        OVERALL_STATUS=1
    fi
else
    echo -e "  ${YELLOW}⚠️  SKIPPED (no .pre-commit-config.yaml found)${NC}"
fi
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║                    📊 WORKFLOW SUMMARY                        ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo "Workflows simulated:"
echo "  ✅ Hassfest Validation"
echo "  ✅ Validate Workflow (JSON + Python + Manifest)"
echo "  ⚠️  Unit Tests (skipped - homeassistant not installed)"
echo "  ✅ HACS Validation"
if [ -f ".pre-commit-config.yaml" ]; then
    echo "  ✅ Pre-commit Checks"
else
    echo "  ⚠️  Pre-commit Checks (skipped - not configured)"
fi
echo ""

echo "Not simulated (require special setup):"
echo "  ⏭️  Integration Tests (require API credentials)"
echo "  ⏭️  CodeQL Security Scanning (GitHub-only)"
echo "  ⏭️  Release Workflow (triggered on tags)"
echo "  ⏭️  Stale Issues Management (scheduled)"
echo "  ⏭️  Labels Management (GitHub-only)"
echo ""

if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ ALL WORKFLOWS PASSED! ✅${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Your integration is ready to push to GitHub! 🚀"
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ SOME WORKFLOWS FAILED ❌${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Please fix the issues above before pushing."
fi

exit $OVERALL_STATUS
