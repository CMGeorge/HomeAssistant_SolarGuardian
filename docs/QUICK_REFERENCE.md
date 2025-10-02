# Quick Command Reference

Quick reference for common tasks in the SolarGuardian integration project.

## Setup Commands

### Install Dependencies

```bash
# Using pip3
pip3 install pytest pytest-asyncio python-dotenv aiohttp

# Or with virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-asyncio python-dotenv
```

### Configure Test Credentials

```bash
cd tests
cp .env.example .env
# Edit .env with your real credentials
nano .env  # or use your preferred editor
```

## Test Commands

### Run All Tests

```bash
cd tests
python3 -m pytest -v
```

### Run Specific Test Categories

```bash
# Unit tests only
python3 -m pytest unit/ -v

# Integration tests only
python3 -m pytest integration/ -v

# With coverage
python3 -m pytest --cov=custom_components.solarguardian --cov-report=html
```

### Run Specific Tests

```bash
# Specific test file
python3 -m pytest unit/test_api.py -v

# Specific test class
python3 -m pytest unit/test_api.py::TestSolarGuardianAPI -v

# Specific test method
python3 -m pytest unit/test_api.py::TestSolarGuardianAPI::test_authenticate -v
```

## Git Commands

### Review Changes

```bash
# See all changes
git status

# See what will be committed
git diff --cached

# Check for any .env files (should only see .env.example)
git status | grep .env
```

### Commit Changes

```bash
# Add new files
git add .github/ .gitignore tests/.env.example tests/.gitignore
git add CLEANUP_TASKS.md COPILOT_SETUP_COMPLETE.md STATUS.md

# Commit
git commit -m "Setup Copilot instructions and organize test structure"

# Push
git push origin master
```

### Security Check Before Push

```bash
# Verify .env is NOT tracked
git ls-files | grep -E "\.env$"
# Should return nothing (only .env.example should be tracked)

# Check what's being committed
git diff --cached --name-only
```

## Development Commands

### Run Integration in Home Assistant

```bash
# Copy to HA config directory
cp -r custom_components/solarguardian ~/.homeassistant/custom_components/

# Restart Home Assistant
# Then add integration via UI: Settings > Devices & Services > Add Integration
```

### Enable Debug Logging in Home Assistant

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.solarguardian: debug
```

### View Home Assistant Logs

```bash
# From HA config directory
tail -f home-assistant.log | grep solarguardian
```

## API Testing Commands

### Test API Connection Manually

```bash
# Test domain connectivity
curl -I https://glapi.mysolarguardian.com
curl -I https://openapi.epsolarpv.com

# Test authentication (replace with your credentials)
curl -X POST https://glapi.mysolarguardian.com/epCloud/user/getAuthToken \
  -H "Content-Type: application/json" \
  -d '{"appKey":"YOUR_KEY","appSecret":"YOUR_SECRET"}'
```

### Run Integration Services

From Home Assistant Developer Tools > Services:

```yaml
# Test connection
service: solarguardian.test_connection
data:
  verbose: true

# Get diagnostics
service: solarguardian.get_diagnostics

# Reset latest data fetching
service: solarguardian.reset_latest_data
```

## File Management Commands

### View Project Structure

```bash
# Tree view (if available)
tree -L 3 -I '__pycache__|*.pyc'

# Or using find
find . -type f -not -path '*/\.*' -not -path '*/__pycache__/*' | sort
```

### Check File Sizes

```bash
# Find large files
find . -type f -size +1M -exec ls -lh {} \;

# Check specific directory
du -sh custom_components/solarguardian/*
```

### Clean Up Python Cache

```bash
# Remove all __pycache__ directories
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Remove .pyc files
find . -name "*.pyc" -delete
```

## Troubleshooting Commands

### Check Python Environment

```bash
# Python version
python3 --version

# Installed packages
pip3 list | grep -E "pytest|aiohttp|dotenv"

# Check module paths
python3 -c "import sys; print('\n'.join(sys.path))"
```

### Test Import Paths

```bash
# Test if integration can be imported
cd tests
python3 -c "import sys; sys.path.insert(0, '../custom_components'); from solarguardian.api import SolarGuardianAPI; print('✅ Import successful')"
```

### View Logs for Errors

```bash
# From tests directory
python3 -m pytest -v --tb=short

# With full traceback
python3 -m pytest -v --tb=long

# Stop on first failure
python3 -m pytest -x
```

## Documentation Commands

### Generate Documentation

```bash
# If you add documentation generation later
# pip install sphinx sphinx-rtd-theme
# sphinx-quickstart docs
# sphinx-build -b html docs docs/_build
```

### View API Documentation

```bash
# Open in browser
open solarguardian_api.txt
# or
cat solarguardian_api.txt | less
```

## Useful Aliases (Optional)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# SolarGuardian shortcuts
alias sg-test='cd ~/path/to/HomeAssistant_SolarGuardian/tests && python3 -m pytest -v'
alias sg-unit='cd ~/path/to/HomeAssistant_SolarGuardian/tests && python3 -m pytest unit/ -v'
alias sg-int='cd ~/path/to/HomeAssistant_SolarGuardian/tests && python3 -m pytest integration/ -v'
alias sg-log='tail -f ~/.homeassistant/home-assistant.log | grep solarguardian'
```

## Quick Checks

### Before Committing

```bash
# Run all these checks
git status | grep "\.env$"  # Should see nothing
python3 -m pytest tests/ -v  # Should pass
grep -r "appKey.*=.*['\"]" custom_components/  # Should find nothing
grep -r "appSecret.*=.*['\"]" custom_components/  # Should find nothing
```

### Security Audit

```bash
# Check for any hardcoded credentials
grep -r "appKey\|appSecret\|X-Access-Token" custom_components/ --exclude-dir=__pycache__

# Check git history for secrets (if concerned)
git log -S "appKey" --all
```

## Environment Variables

### Set for Testing

```bash
# Temporary for current session
export APP_KEY="your_key"
export APP_SECRET="your_secret"
export DOMAIN="glapi.mysolarguardian.com"

# Or use .env file (already configured in tests/.env)
```

## Performance Commands

### Profile Tests

```bash
# Time test execution
time python3 -m pytest tests/ -v

# Profile specific test
python3 -m cProfile -o output.prof tests/unit/test_api.py
```

---

## Quick Help

- **Full Guide**: `.github/copilot-instructions.md`
- **Test Docs**: `tests/README.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`
- **Status**: `STATUS.md`

**Tip**: Use GitHub Copilot for code suggestions - it has access to all project guidelines!
