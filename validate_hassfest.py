#!/usr/bin/env python3
"""Manual hassfest-style validation for Home Assistant custom components."""

import json
import sys
from pathlib import Path


def validate_manifest(manifest_path: Path) -> list[str]:
    """Validate manifest.json."""
    errors = []

    with open(manifest_path) as f:
        manifest = json.load(f)

    # Required fields for custom components
    required = ["domain", "name", "documentation", "codeowners", "version"]
    for field in required:
        if field not in manifest:
            errors.append(f"❌ Missing required field: {field}")

    # Fields that are NOT allowed in custom components (core only)
    forbidden_custom = ["homeassistant"]
    for field in forbidden_custom:
        if field in manifest:
            errors.append(
                f"❌ Field '{field}' is only allowed in core integrations, remove from custom component"
            )

    # Check domain matches directory name
    if manifest.get("domain") != manifest_path.parent.name:
        errors.append(
            f"❌ Domain '{manifest.get('domain')}' doesn't match directory name '{manifest_path.parent.name}'"
        )

    # Check config_flow exists if specified
    if manifest.get("config_flow"):
        config_flow_path = manifest_path.parent / "config_flow.py"
        if not config_flow_path.exists():
            errors.append("❌ config_flow: true but config_flow.py not found")

    # Check IoT class
    valid_iot_classes = [
        "assumed_state",
        "calculated",
        "cloud_polling",
        "cloud_push",
        "local_polling",
        "local_push",
    ]
    if "iot_class" in manifest:
        if manifest["iot_class"] not in valid_iot_classes:
            errors.append(f"❌ Invalid iot_class: {manifest['iot_class']}")

    # Check dependencies
    if "requirements" in manifest:
        for req in manifest["requirements"]:
            if "==" not in req:
                errors.append(f"❌ Requirements must be pinned with ==: {req}")

    return errors


def validate_strings(strings_path: Path) -> list[str]:
    """Validate strings.json."""
    errors = []

    if not strings_path.exists():
        errors.append("❌ strings.json not found")
        return errors

    with open(strings_path) as f:
        strings = json.load(f)

    # Check config section exists if config_flow is used
    if "config" not in strings:
        errors.append("❌ Missing 'config' section in strings.json")

    return errors


def validate_translations(integration_path: Path) -> list[str]:
    """Validate translation files."""
    errors = []

    translations_dir = integration_path / "translations"
    if not translations_dir.exists():
        return []  # Translations are optional

    # Check en.json exists
    en_json = translations_dir / "en.json"
    if not en_json.exists():
        errors.append(
            "❌ translations/en.json not found (required if translations/ exists)"
        )

    # Validate each translation file
    for trans_file in translations_dir.glob("*.json"):
        try:
            with open(trans_file) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"❌ Invalid JSON in {trans_file.name}: {e}")

    return errors


def validate_platforms(integration_path: Path) -> list[str]:
    """Validate platform files."""
    errors = []

    # Check for __init__.py
    init_file = integration_path / "__init__.py"
    if not init_file.exists():
        errors.append("❌ __init__.py not found")

    # Check platform files have proper structure
    platform_files = ["sensor.py", "binary_sensor.py", "switch.py", "button.py"]
    for platform_file in platform_files:
        platform_path = integration_path / platform_file
        if platform_path.exists():
            # Basic syntax check
            try:
                with open(platform_path) as f:
                    compile(f.read(), platform_file, "exec")
            except SyntaxError as e:
                errors.append(f"❌ Syntax error in {platform_file}: {e}")

    return errors


def main():
    """Run validation."""
    integration_path = Path(__file__).parent / "custom_components" / "solarguardian"

    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                                                               ║")
    print("║              🔍 Hassfest-Style Validation 🔍                  ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()

    all_errors = []

    # Validate manifest
    print("📋 Validating manifest.json...")
    manifest_errors = validate_manifest(integration_path / "manifest.json")
    if manifest_errors:
        all_errors.extend(manifest_errors)
        for error in manifest_errors:
            print(f"  {error}")
    else:
        print("  ✅ manifest.json is valid")
    print()

    # Validate strings
    print("📝 Validating strings.json...")
    strings_errors = validate_strings(integration_path / "strings.json")
    if strings_errors:
        all_errors.extend(strings_errors)
        for error in strings_errors:
            print(f"  {error}")
    else:
        print("  ✅ strings.json is valid")
    print()

    # Validate translations
    print("🌍 Validating translations...")
    translation_errors = validate_translations(integration_path)
    if translation_errors:
        all_errors.extend(translation_errors)
        for error in translation_errors:
            print(f"  {error}")
    else:
        print("  ✅ Translations are valid")
    print()

    # Validate platforms
    print("🔌 Validating platform files...")
    platform_errors = validate_platforms(integration_path)
    if platform_errors:
        all_errors.extend(platform_errors)
        for error in platform_errors:
            print(f"  {error}")
    else:
        print("  ✅ Platform files are valid")
    print()

    # Summary
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                    📊 VALIDATION SUMMARY                      ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()

    if all_errors:
        print(f"❌ VALIDATION FAILED with {len(all_errors)} error(s)")
        print()
        for error in all_errors:
            print(f"  {error}")
        return 1
    else:
        print("✅ ALL HASSFEST-STYLE CHECKS PASSED!")
        print()
        print("Your integration meets Home Assistant requirements:")
        print("  ✅ Valid manifest.json")
        print("  ✅ Valid strings.json")
        print("  ✅ Valid translations")
        print("  ✅ Valid platform files")
        print("  ✅ Proper Python syntax")
        return 0


if __name__ == "__main__":
    sys.exit(main())
