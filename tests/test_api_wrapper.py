"""
Wrapper to load SolarGuardian API modules for testing without Home Assistant.
This avoids import issues by loading modules in the correct order.
"""
import sys
import importlib.util
from pathlib import Path

def load_api_modules():
    """Load API modules without triggering Home Assistant imports."""
    
    # Get paths
    base_path = Path(__file__).parent / 'custom_components' / 'solarguardian'
    const_path = base_path / 'const.py'
    api_path = base_path / 'api.py'
    
    # Create a fake parent package to make relative imports work
    parent_spec = importlib.util.spec_from_loader(
        'custom_components.solarguardian',
        loader=None,
        is_package=True
    )
    parent_module = importlib.util.module_from_spec(parent_spec)
    sys.modules['custom_components.solarguardian'] = parent_module
    
    # Load const module
    const_spec = importlib.util.spec_from_file_location(
        'custom_components.solarguardian.const',
        const_path
    )
    const_module = importlib.util.module_from_spec(const_spec)
    sys.modules['custom_components.solarguardian.const'] = const_module
    const_spec.loader.exec_module(const_module)
    
    # Load api module
    api_spec = importlib.util.spec_from_file_location(
        'custom_components.solarguardian.api',
        api_path
    )
    api_module = importlib.util.module_from_spec(api_spec)
    sys.modules['custom_components.solarguardian.api'] = api_module
    api_spec.loader.exec_module(api_module)
    
    return api_module, const_module


if __name__ == '__main__':
    api_module, const_module = load_api_modules()
    print("✅ Successfully loaded API modules!")
    print(f"   - SolarGuardianAPI: {api_module.SolarGuardianAPI}")
    print(f"   - SolarGuardianAPIError: {api_module.SolarGuardianAPIError}")
    print(f"   - Constants: {len([x for x in dir(const_module) if not x.startswith('_')])} items")
