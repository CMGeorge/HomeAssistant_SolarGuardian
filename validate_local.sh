#!/bin/bash
# Local validation script - Run all checks before pushing to GitHub
# Usage: ./validate_local.sh

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║              🔍 Local Validation Script 🔍                    ║"
echo "║                                                               ║"
echo "║  Running all checks that GitHub Actions will perform...      ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

FAILED=0

# Track individual check results
declare -a RESULTS

# Function to print result
check_result() {
    local name=$1
    local result=$2
    if [ $result -eq 0 ]; then
        RESULTS+=("✅ $name")
        echo "  ✅ PASSED"
    else
        RESULTS+=("❌ $name")
        FAILED=1
        echo "  ❌ FAILED"
    fi
    echo ""
}

# ============================================================================
# 1. JSON Validation
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 1/8 Validating JSON files..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

JSON_FAILED=0

echo -n "  Checking manifest.json... "
if jq empty custom_components/solarguardian/manifest.json 2>/dev/null; then
    echo "✅"
else
    echo "❌"
    JSON_FAILED=1
fi

echo -n "  Checking hacs.json... "
if jq empty hacs.json 2>/dev/null; then
    echo "✅"
else
    echo "❌"
    JSON_FAILED=1
fi

echo -n "  Checking strings.json... "
if jq empty custom_components/solarguardian/strings.json 2>/dev/null; then
    echo "✅"
else
    echo "❌"
    JSON_FAILED=1
fi

echo -n "  Checking translation files... "
TRANS_FAILED=0
for file in custom_components/solarguardian/translations/*.json; do
    if ! jq empty "$file" 2>/dev/null; then
        echo "❌ $(basename $file)"
        TRANS_FAILED=1
    fi
done
if [ $TRANS_FAILED -eq 0 ]; then
    echo "✅"
else
    JSON_FAILED=1
fi

check_result "JSON Validation" $JSON_FAILED

# ============================================================================
# 2. Manifest Validation
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 2/8 Validating manifest.json..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

MANIFEST_FAILED=0
python3 << 'EOF'
import json
import sys

try:
    with open('custom_components/solarguardian/manifest.json') as f:
        manifest = json.load(f)

    required = ['domain', 'name', 'documentation', 'issue_tracker', 'version', 'requirements', 'codeowners']
    missing = [f for f in required if f not in manifest]

    if missing:
        print(f"  ❌ Missing required fields: {', '.join(missing)}")
        sys.exit(1)

    # Check domain matches directory name
    if manifest['domain'] != 'solarguardian':
        print(f"  ❌ Domain '{manifest['domain']}' doesn't match directory name")
        sys.exit(1)

    # Check version format
    version = manifest['version']
    if not version or len(version.split('.')) < 2:
        print(f"  ❌ Invalid version format: {version}")
        sys.exit(1)

    print("  ✅ All required fields present")
    print(f"  ✅ Domain: {manifest['domain']}")
    print(f"  ✅ Version: {version}")

except Exception as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)
EOF
MANIFEST_FAILED=$?

check_result "Manifest Validation" $MANIFEST_FAILED

# ============================================================================
# 3. Code Formatting (Black)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 3/8 Checking code formatting (Black)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

BLACK_FAILED=0
if command -v black &> /dev/null; then
    if black --check custom_components/ 2>&1 | grep -q "would be reformatted"; then
        echo "  ⚠️  Code needs formatting. Run: black custom_components/"
        BLACK_FAILED=1
    else
        echo "  ✅ Code is properly formatted"
    fi
else
    echo "  ⚠️  Black not installed. Run: pip install black"
    BLACK_FAILED=1
fi

check_result "Black Formatting" $BLACK_FAILED

# ============================================================================
# 4. Import Sorting (isort)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 4/8 Checking import order (isort)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ISORT_FAILED=0
if command -v isort &> /dev/null; then
    if isort --check-only custom_components/ 2>&1 | grep -q "would be reformatted"; then
        echo "  ⚠️  Imports need sorting. Run: isort custom_components/"
        ISORT_FAILED=1
    else
        echo "  ✅ Imports are properly sorted"
    fi
else
    echo "  ⚠️  isort not installed. Run: pip install isort"
    ISORT_FAILED=1
fi

check_result "isort Import Order" $ISORT_FAILED

# ============================================================================
# 5. Linting (Ruff)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 5/8 Running Ruff linter..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RUFF_FAILED=0
if command -v ruff &> /dev/null; then
    if ruff check custom_components/ --quiet; then
        echo "  ✅ Ruff checks passed"
    else
        echo "  ❌ Ruff found issues. Run: ruff check custom_components/"
        RUFF_FAILED=1
    fi
else
    echo "  ⚠️  Ruff not installed. Run: pip install ruff"
    RUFF_FAILED=1
fi

check_result "Ruff Linting" $RUFF_FAILED

# ============================================================================
# 6. Security Checks
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔒 6/8 Checking for secrets..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SECURITY_FAILED=0

# Check for hardcoded credentials (excluding constants and examples)
SECRETS=$(grep -r "app_key.*=.*['\"][A-Za-z0-9]" \
    --exclude-dir=.git \
    --exclude-dir=.venv \
    --exclude-dir=docs \
    --exclude="*.md" \
    . 2>/dev/null | \
    grep -v "CONF_APP_KEY\|example\|your_app_key" | \
    wc -l || echo "0")

if [ "$SECRETS" -eq "0" ]; then
    echo "  ✅ No hardcoded secrets found"
else
    echo "  ❌ Potential secrets found! Check your code."
    SECURITY_FAILED=1
fi

# Check .env isn't tracked
if git ls-files | grep -q "\.env$"; then
    echo "  ❌ .env file is tracked by git!"
    SECURITY_FAILED=1
else
    echo "  ✅ .env files properly ignored"
fi

check_result "Security Checks" $SECURITY_FAILED

# ============================================================================
# 7. Tests
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 7/8 Running tests..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TEST_FAILED=0
if command -v pytest &> /dev/null; then
    if [ -d "tests" ]; then
        echo "  Running unit tests..."
        if pytest tests/unit/ -v --tb=short -q 2>&1 | tail -10; then
            echo "  ✅ Tests passed"
        else
            echo "  ❌ Some tests failed"
            TEST_FAILED=1
        fi
    else
        echo "  ⚠️  No tests directory found"
    fi
else
    echo "  ⚠️  pytest not installed. Run: pip install pytest"
    TEST_FAILED=1
fi

check_result "Tests" $TEST_FAILED

# ============================================================================
# 8. Required Files Check
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 8/8 Checking required files..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

FILES_FAILED=0

required_files=(
    "README.md"
    "info.md"
    "hacs.json"
    "LICENSE"
    "custom_components/solarguardian/__init__.py"
    "custom_components/solarguardian/manifest.json"
)

for file in "${required_files[@]}"; do
    echo -n "  Checking $file... "
    if [ -f "$file" ]; then
        echo "✅"
    else
        echo "❌"
        FILES_FAILED=1
    fi
done

check_result "Required Files" $FILES_FAILED

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║                    📊 VALIDATION SUMMARY                      ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

for result in "${RESULTS[@]}"; do
    echo "  $result"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "🎉 ALL CHECKS PASSED! 🎉"
    echo ""
    echo "Your code is ready to push to GitHub!"
    echo ""
    echo "Next steps:"
    echo "  git add -A"
    echo "  git commit -m 'your message'"
    echo "  git push"
    echo ""
    exit 0
else
    echo ""
    echo "❌ SOME CHECKS FAILED ❌"
    echo ""
    echo "Please fix the issues above before pushing."
    echo ""
    echo "Quick fixes:"
    echo "  • Format code:     black custom_components/"
    echo "  • Sort imports:    isort custom_components/"
    echo "  • Fix lint issues: ruff check --fix custom_components/"
    echo ""
    exit 1
fi
