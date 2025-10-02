# Local Validation Guide

This guide shows you how to run all GitHub workflow checks locally before pushing to GitHub.

---

## 🎯 Why Run Locally?

- ✅ **Faster**: Get instant feedback without waiting for GitHub Actions
- ✅ **Save Resources**: Don't waste GitHub Actions minutes on failures
- ✅ **Iterate Quickly**: Fix issues immediately
- ✅ **Confidence**: Know your code will pass before pushing

---

## 📋 Prerequisites

### Install Required Tools

```bash
# Install Home Assistant CLI tools
pip install homeassistant

# Install pre-commit (for code quality checks)
pip install pre-commit

# Install validation tools
pip install black isort ruff mypy pylint

# Install pytest for tests
pip install pytest pytest-homeassistant-custom-component

# Install hassfest validator
pip install homeassistant-devcontainer
```

### Or Use Virtual Environment (Recommended)

```bash
cd /Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install all tools
pip install homeassistant pre-commit black isort ruff mypy pylint pytest pytest-homeassistant-custom-component
```

---

## 🔍 1. Hassfest Validation (Home Assistant Manifest Check)

### Using Docker (Recommended - Exact Same as GitHub)

```bash
# Run hassfest using Home Assistant's official Docker image
docker run --rm -v $(pwd):/github/workspace ghcr.io/home-assistant/home-assistant/amd64-homeassistant:dev python3 -m script.hassfest --integration-path /github/workspace/custom_components/solarguardian
```

### Using Home Assistant CLI

```bash
cd /Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian

# Check manifest.json
python3 -m homeassistant.scripts.hassfest --integration custom_components/solarguardian
```

### Manual Validation

```bash
# Check manifest.json syntax
cat custom_components/solarguardian/manifest.json | jq .

# Verify required fields exist
jq '.domain, .name, .documentation, .issue_tracker, .version, .requirements, .codeowners' custom_components/solarguardian/manifest.json
```

**What it checks:**
- ✅ `manifest.json` syntax is valid
- ✅ All required fields present
- ✅ URLs are accessible
- ✅ Version format correct
- ✅ Requirements are valid Python packages

---

## 🏷️ 2. HACS Validation

### Using HACS Action Locally

```bash
# Install HACS validator
pip install hacs-validate

# Run HACS validation
cd /Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian
hacs-validate --repository .
```

### Manual HACS Checks

```bash
# Check hacs.json exists and is valid
cat hacs.json | jq .

# Verify required files exist
ls -la README.md
ls -la info.md
ls -la custom_components/solarguardian/manifest.json

# Check for required fields in hacs.json
jq '.name, .render_readme' hacs.json
```

**What it checks:**
- ✅ `hacs.json` is valid
- ✅ `README.md` exists
- ✅ `info.md` exists
- ✅ Repository structure is correct
- ✅ No brand violations

---

## 🎨 3. Code Quality Checks

### Black (Code Formatting)

```bash
cd /Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian

# Check if code needs formatting
black --check custom_components/

# Auto-fix formatting
black custom_components/
```

### isort (Import Sorting)

```bash
# Check import order
isort --check-only custom_components/

# Auto-fix imports
isort custom_components/
```

### Ruff (Fast Python Linter)

```bash
# Run Ruff linter
ruff check custom_components/

# Auto-fix issues
ruff check --fix custom_components/
```

### Pylint (Comprehensive Linter)

```bash
# Run pylint on integration
pylint custom_components/solarguardian/
```

### MyPy (Type Checking)

```bash
# Check type hints
mypy custom_components/solarguardian/
```

---

## 🧪 4. Run Tests Locally

### Using pytest

```bash
cd /Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_api.py -v

# Run with coverage
pytest tests/ --cov=custom_components.solarguardian --cov-report=html
```

### Run Tests with Real API

```bash
# Make sure tests/.env exists with credentials
cd tests
pytest unit/test_api.py -v -s
pytest integration/ -v -s
```

---

## 🔒 5. Security Checks

### Check for Secrets

```bash
cd /Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian

# Search for potential secrets (should return nothing)
grep -r "app_key.*=.*[A-Za-z0-9]" --exclude-dir=.git --exclude-dir=.venv --exclude="*.md" . | grep -v "CONF_APP_KEY\|example"

# Check .env files aren't tracked
git ls-files | grep "\.env$"
```

### Verify .gitignore

```bash
# Test gitignore is working
echo "test_secret=abc123" > tests/.env
git check-ignore tests/.env
# Should output: tests/.env

# Clean up
rm tests/.env
```

---

## 📦 6. JSON Validation

### Validate All JSON Files

```bash
cd /Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian

# Validate manifest.json
jq empty custom_components/solarguardian/manifest.json && echo "✅ manifest.json valid"

# Validate hacs.json
jq empty hacs.json && echo "✅ hacs.json valid"

# Validate strings.json
jq empty custom_components/solarguardian/strings.json && echo "✅ strings.json valid"

# Validate translation files
for file in custom_components/solarguardian/translations/*.json; do
    jq empty "$file" && echo "✅ $(basename $file) valid"
done
```

---

## 🚀 7. Pre-commit Hooks (Automated Checks)

### Set Up Pre-commit

```bash
cd /Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian

# Install pre-commit hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files
```

**What pre-commit does:**
- ✅ Runs Black formatting
- ✅ Runs isort
- ✅ Runs Ruff
- ✅ Validates JSON
- ✅ Checks for secrets
- ✅ Validates YAML

### Run Specific Hook

```bash
# Run only Black
pre-commit run black --all-files

# Run only Ruff
pre-commit run ruff --all-files
```

---

## 🎯 8. All-in-One Validation Script

Create a script to run all checks at once:

```bash
#!/bin/bash
# save as: validate_local.sh

echo "🔍 Running local validation..."
echo ""

cd /Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "📋 1/7 Validating JSON files..."
jq empty custom_components/solarguardian/manifest.json && echo "  ✅ manifest.json" || echo "  ❌ manifest.json FAILED"
jq empty hacs.json && echo "  ✅ hacs.json" || echo "  ❌ hacs.json FAILED"
jq empty custom_components/solarguardian/strings.json && echo "  ✅ strings.json" || echo "  ❌ strings.json FAILED"

echo ""
echo "🎨 2/7 Checking code formatting..."
black --check custom_components/ && echo "  ✅ Black passed" || echo "  ❌ Black failed (run: black custom_components/)"

echo ""
echo "📦 3/7 Checking import order..."
isort --check-only custom_components/ && echo "  ✅ isort passed" || echo "  ❌ isort failed (run: isort custom_components/)"

echo ""
echo "🔍 4/7 Running Ruff linter..."
ruff check custom_components/ && echo "  ✅ Ruff passed" || echo "  ❌ Ruff failed"

echo ""
echo "🧪 5/7 Running tests..."
pytest tests/ -v --tb=short && echo "  ✅ Tests passed" || echo "  ❌ Tests failed"

echo ""
echo "🔒 6/7 Checking for secrets..."
SECRETS=$(grep -r "app_key.*=.*[A-Za-z0-9]" --exclude-dir=.git --exclude-dir=.venv --exclude="*.md" . | grep -v "CONF_APP_KEY\|example" | wc -l)
if [ "$SECRETS" -eq "0" ]; then
    echo "  ✅ No secrets found"
else
    echo "  ❌ Potential secrets found!"
fi

echo ""
echo "✅ 7/7 Checking manifest requirements..."
python3 << 'EOF'
import json
with open('custom_components/solarguardian/manifest.json') as f:
    manifest = json.load(f)
    required = ['domain', 'name', 'documentation', 'issue_tracker', 'version', 'requirements', 'codeowners']
    missing = [f for f in required if f not in manifest]
    if missing:
        print(f"  ❌ Missing fields: {missing}")
    else:
        print("  ✅ All required fields present")
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Local validation complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

### Make it executable and run:

```bash
chmod +x validate_local.sh
./validate_local.sh
```

---

## 🐳 9. Docker Validation (Most Accurate)

Use Docker to run validation exactly as GitHub Actions does:

```bash
# Run in Home Assistant container
docker run --rm -v $(pwd):/config ghcr.io/home-assistant/home-assistant:stable python -m pytest /config/tests/

# Run hassfest in container
docker run --rm -v $(pwd):/workspace ghcr.io/home-assistant/home-assistant:dev python3 -m script.hassfest --integration-path /workspace/custom_components/solarguardian
```

---

## 📊 10. Quick Pre-Push Checklist

Before `git push`, run these quick checks:

```bash
# 1. Format code
black custom_components/
isort custom_components/

# 2. Lint
ruff check custom_components/

# 3. Validate JSON
jq empty custom_components/solarguardian/manifest.json
jq empty hacs.json

# 4. Run tests
pytest tests/ -v

# 5. Check for secrets
git diff | grep -i "secret\|password\|key" | grep -v "CONF_"

# 6. Verify .env is ignored
git status | grep "\.env"  # Should show nothing

# If all pass, you're ready!
git push
```

---

## 🔧 Troubleshooting

### Issue: "jq: command not found"

```bash
# macOS
brew install jq

# Linux
sudo apt-get install jq
```

### Issue: "pytest: command not found"

```bash
pip install pytest pytest-homeassistant-custom-component
```

### Issue: "Docker not running"

```bash
# Start Docker Desktop on macOS
open -a Docker

# Or use native validation without Docker
```

### Issue: "Tests fail with API errors"

```bash
# Create tests/.env with your credentials
cd tests
cp .env.example .env
# Edit .env with your actual credentials
```

---

## 🎯 Recommended Workflow

### Before Every Commit:

```bash
# 1. Auto-format
black custom_components/
isort custom_components/

# 2. Run pre-commit
pre-commit run --all-files

# 3. Test changes
pytest tests/unit/ -v
```

### Before Every Push:

```bash
# Run full validation script
./validate_local.sh

# If all passes:
git push
```

### Before Creating PR:

```bash
# Run everything including integration tests
pytest tests/ -v --cov
./validate_local.sh
docker run --rm -v $(pwd):/workspace ghcr.io/home-assistant/home-assistant:dev python3 -m script.hassfest
```

---

## 📚 Additional Resources

- **Home Assistant Developer Docs**: https://developers.home-assistant.io
- **HACS Documentation**: https://hacs.xyz/docs/publish/start
- **Pre-commit Hooks**: https://pre-commit.com
- **pytest Documentation**: https://docs.pytest.org

---

## ✅ Summary

**Install Once:**
```bash
pip install homeassistant pre-commit black isort ruff pytest
pre-commit install
```

**Run Before Push:**
```bash
./validate_local.sh
```

**Auto-format:**
```bash
black custom_components/
isort custom_components/
```

This ensures your code passes all checks before it even reaches GitHub! 🚀
