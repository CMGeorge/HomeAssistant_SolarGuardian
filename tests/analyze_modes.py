"""Analyze mode field in sensors to understand why some are Unknown."""
import json
import subprocess
import re

# Run the API test and capture output
print("Running API test...")
result = subprocess.run(
    ["python3", "run_real_api_tests.py"],
    capture_output=True,
    text=True,
    cwd="/Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian/tests"
)

output = result.stdout

# Find all parameters and their mode values
mode_0_count = 0
mode_1_count = 0
mode_0_sensors = []
mode_1_sensors = []

# Extract all variableNameE and mode pairs
lines = output.split('\n')
current_sensor = None

for i, line in enumerate(lines):
    if '"variableNameE":' in line:
        match = re.search(r'"variableNameE":\s*"([^"]+)"', line)
        if match:
            current_sensor = match.group(1)
    
    if '"mode":' in line and current_sensor:
        match = re.search(r'"mode":\s*"(\d+)"', line)
        if match:
            mode = match.group(1)
            if mode == "0":
                mode_0_count += 1
                mode_0_sensors.append(current_sensor)
            elif mode == "1":
                mode_1_count += 1
                mode_1_sensors.append(current_sensor)
            current_sensor = None  # Reset after finding mode

print("=" * 80)
print("  Mode Analysis")
print("=" * 80)
print()
print(f"mode='0' (Real-time sensors): {mode_0_count}")
print(f"mode='1' (Configuration parameters): {mode_1_count}")
print()

print("=" * 80)
print("  Configuration Parameters (mode='1') - These show 'Unknown'")
print("=" * 80)
print()
for sensor in mode_1_sensors[:30]:  # Show first 30
    print(f"  • {sensor}")

if len(mode_1_sensors) > 30:
    print(f"\n  ... and {len(mode_1_sensors) - 30} more")

print()
print("=" * 80)
print("  Real-time Sensors (mode='0') - These have values")
print("=" * 80)
print()
for sensor in mode_0_sensors[:20]:  # Show first 20
    print(f"  • {sensor}")

if len(mode_0_sensors) > 20:
    print(f"\n  ... and {len(mode_0_sensors) - 20} more")
