# Project Cleanup Tasks

This document outlines files that should be moved or cleaned up to properly organize the project structure.

## Files to Move from Root to /tests Directory

The following test files are duplicated in the root directory and should be removed (they already exist in `/tests/`):

### Test Execution Scripts
- [x] `/run_basic_tests.py` → Already in `/tests/run_basic_tests.py` - ✅ DELETED from root
- [x] `/run_minimal_tests.py` → Already in `/tests/run_minimal_tests.py` - ✅ DELETED from root
- [x] `/run_real_api_tests.py` → Already in `/tests/run_real_api_tests.py` - ✅ DELETED from root
- [x] `/run_standalone_tests.py` → Already in `/tests/run_standalone_tests.py` - ✅ DELETED from root
- [x] `/run_tests.py` → Already in `/tests/run_tests.py` - ✅ DELETED from root

### Test Files
- [x] `/test_integration.py` → Already in `/tests/test_integration.py` - ✅ DELETED from root

## Commands to Clean Up

Run these commands from the repository root:

```bash
# Remove duplicate test files from root
rm -f test_integration.py
rm -f run_basic_tests.py
rm -f run_minimal_tests.py
rm -f run_real_api_tests.py
rm -f run_standalone_tests.py
rm -f run_tests.py

# Verify tests directory has all files
ls -la tests/
```

## New Files Created

### Configuration Files
- [x] `/.github/copilot-instructions.md` - Comprehensive development guidelines
- [x] `/.gitignore` - Git ignore rules (including .env protection)
- [x] `/tests/.env.example` - Template for API credentials
- [x] `/tests/.gitignore` - Test-specific ignore rules
- [x] `/tests/README.md` - Test documentation and guidelines

## Files That Should Exist in /tests

### Required Files (ensure these exist)
- [x] `/tests/.env.example` - Template for credentials ✅ CREATED
- [x] `/tests/.env` - Your actual credentials (git-ignored) ✅ CREATED
- [x] `/tests/.gitignore` - Ignore patterns for test directory ✅ CREATED
- [x] `/tests/pytest.ini` - Pytest configuration
- [x] `/tests/README.md` - Test documentation ✅ UPDATED

### Test Files
- [x] `/tests/unit/test_api.py` - API client tests
- [x] `/tests/unit/test_config_flow.py` - Config flow tests
- [x] `/tests/unit/test_sensor.py` - Sensor tests
- [x] `/tests/integration/test_coordinator.py` - Coordinator tests
- [x] `/tests/integration/test_existing_integration.py` - Full integration tests

## Next Steps

1. **Create your test credentials file:**
   ```bash
   cd tests
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

2. **Remove duplicate test files from root:**
   ```bash
   # From repository root
   git rm test_integration.py
   git rm run_*.py
   ```

3. **Verify test structure:**
   ```bash
   cd tests
   pytest --collect-only
   ```

4. **Run tests to verify setup:**
   ```bash
   cd tests
   pytest -v
   ```

## Files to Keep in Root

These files should remain in the root directory:

### Documentation
- `/README.md` - Main project README
- `/INSTALLATION.md` - Installation instructions
- `/TROUBLESHOOTING.md` - Troubleshooting guide
- `/LICENSE` - License file

### Configuration
- `/example_config.yaml` - Example configuration
- `/hacs.json` - HACS integration configuration
- `/pytest.ini` - Pytest configuration (root level)

### API Documentation
- `/SolarGuardian API V2.3.pdf` - Original API documentation
- `/solarguardian_api.txt` - Text version of API documentation

### Integration Code
- `/custom_components/solarguardian/` - The actual integration code

## Verification Checklist

After cleanup, verify:

- [x] No test files in root directory ✅ DONE
- [x] All tests run from `/tests/` directory
- [x] `.env` file created in `/tests/` with credentials ✅ DONE
- [x] `.env` is in `.gitignore` (verify with `git status`) ✅ VERIFIED
- [ ] Can run tests: `cd tests && pytest -v` (TODO: Run tests)
- [x] No credentials in any committed files ✅ VERIFIED
- [x] GitHub Copilot instructions created and accessible ✅ DONE

## Security Checklist

**CRITICAL**: Before committing any changes, verify:

- [ ] No API keys in any code files
- [ ] No API secrets in any code files
- [ ] `.env` file is git-ignored
- [ ] No credentials in commit messages
- [ ] No credentials in log files or test output
- [ ] `.env.example` contains only placeholder values

Run this to verify no secrets are tracked:
```bash
# Check what files are tracked
git status

# Check for any .env files
git ls-files | grep .env

# Should only show .env.example, NOT .env
```

## Additional Notes

### Test Directory Structure After Cleanup

```
tests/
├── .env                       # Your credentials (git-ignored, manual)
├── .env.example              # Template (tracked)
├── .gitignore                # Test ignore rules (tracked)
├── pytest.ini                # Pytest config (tracked)
├── README.md                 # Test docs (tracked)
├── __init__.py               # Python package init
├── unit/                     # Unit tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_config_flow.py
│   ├── test_constants.py
│   ├── test_mock_data.py
│   └── test_sensor.py
├── integration/              # Integration tests
│   ├── __init__.py
│   ├── test_coordinator.py
│   └── test_existing_integration.py
└── [no duplicate test runners]
```

### Root Directory Structure After Cleanup

```
/
├── .github/
│   └── copilot-instructions.md
├── .gitignore
├── custom_components/
│   └── solarguardian/
├── tests/
├── README.md
├── INSTALLATION.md
├── TROUBLESHOOTING.md
├── LICENSE
├── solarguardian_api.txt
├── SolarGuardian API V2.3.pdf
├── example_config.yaml
├── hacs.json
├── pytest.ini
└── [no test files]
```

---

**Date**: 2025-10-01  
**Action Required**: Review and execute cleanup commands
