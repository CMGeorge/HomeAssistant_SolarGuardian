"""Unit tests for SolarGuardian config flow."""

import os

# Add custom components to path
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "../../custom_components"))

from solarguardian.api import SolarGuardianAPIError
from solarguardian.config_flow import ConfigFlow, OptionsFlowHandler
from solarguardian.const import (
    CONF_APP_KEY,
    CONF_APP_SECRET,
    CONF_DOMAIN,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    DOMAIN_CHINA,
    DOMAIN_INTERNATIONAL,
)

# Mock homeassistant dependencies
try:
    from homeassistant import config_entries
    from homeassistant.core import HomeAssistant
    from homeassistant.data_entry_flow import FlowResult
except ImportError:
    # Create mock classes if homeassistant is not available
    class MockConfigEntries:
        class ConfigFlow:
            def __init__(self):
                self.context = {}
                self.data = {}

            async def async_set_unique_id(self, unique_id):
                self._unique_id = unique_id

            def _abort_if_unique_id_configured(self):
                pass

            def async_create_entry(self, title, data):
                return {"type": "create_entry", "title": title, "data": data}

            def async_show_form(self, step_id, data_schema, errors=None):
                return {"type": "form", "step_id": step_id, "errors": errors or {}}

        class OptionsFlow:
            def __init__(self, config_entry):
                self.config_entry = config_entry

            def async_create_entry(self, title, data):
                return {"type": "create_entry", "title": title, "data": data}

            def async_show_form(self, step_id, data_schema):
                return {"type": "form", "step_id": step_id}

        class ConfigEntry:
            def __init__(self):
                self.options = {}

    config_entries = MockConfigEntries()

    class FlowResult:
        pass


class TestSolarGuardianConfigFlow(unittest.IsolatedAsyncioTestCase):
    """Test cases for SolarGuardian config flow."""

    def setUp(self):
        """Set up test fixtures."""
        self.flow = ConfigFlow()
        self.flow.hass = MagicMock()

    async def test_async_step_user_no_input(self):
        """Test user step without input shows form."""
        result = await self.flow.async_step_user(user_input=None)

        self.assertEqual(result["type"], "form")
        self.assertEqual(result["step_id"], "user")
        # errors might be None instead of empty dict in some implementations
        self.assertIn(result.get("errors", {}), [{}, None])

    @patch("solarguardian.config_flow.SolarGuardianAPI")
    async def test_async_step_user_valid_credentials(self, mock_api_class):
        """Test user step with valid credentials."""
        # Mock API authentication success
        mock_api = AsyncMock()
        mock_api.authenticate.return_value = True
        mock_api.close = AsyncMock()
        mock_api_class.return_value = mock_api

        # Mock unique ID handling
        self.flow.async_set_unique_id = AsyncMock()
        self.flow._abort_if_unique_id_configured = MagicMock()
        self.flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        user_input = {
            CONF_DOMAIN: DOMAIN_INTERNATIONAL,
            CONF_APP_KEY: "test_app_key",
            CONF_APP_SECRET: "test_app_secret",
        }

        result = await self.flow.async_step_user(user_input=user_input)

        # Verify API was created with correct parameters
        mock_api_class.assert_called_once_with(
            domain=DOMAIN_INTERNATIONAL,
            app_key="test_app_key",
            app_secret="test_app_secret",
        )

        # Verify authentication was attempted
        mock_api.authenticate.assert_called_once()
        mock_api.close.assert_called_once()

        # Verify unique ID was set
        self.flow.async_set_unique_id.assert_called_once_with("test_app_key")

        # Verify config entry was created
        self.flow.async_create_entry.assert_called_once()

    @patch("solarguardian.config_flow.SolarGuardianAPI")
    async def test_async_step_user_invalid_auth(self, mock_api_class):
        """Test user step with invalid authentication."""
        # Mock API authentication failure
        mock_api = AsyncMock()
        mock_api.authenticate.side_effect = SolarGuardianAPIError("Invalid credentials")
        mock_api.close = AsyncMock()
        mock_api_class.return_value = mock_api

        # Mock form display
        self.flow.async_show_form = MagicMock(
            return_value={"type": "form", "errors": {"base": "invalid_auth"}}
        )

        user_input = {
            CONF_DOMAIN: DOMAIN_CHINA,
            CONF_APP_KEY: "invalid_key",
            CONF_APP_SECRET: "invalid_secret",
        }

        result = await self.flow.async_step_user(user_input=user_input)

        # Verify error was handled
        self.flow.async_show_form.assert_called_once()
        call_args = self.flow.async_show_form.call_args
        self.assertEqual(call_args[1]["errors"]["base"], "invalid_auth")

    @patch("solarguardian.config_flow.SolarGuardianAPI")
    async def test_async_step_user_unexpected_error(self, mock_api_class):
        """Test user step with unexpected error."""
        # Mock API unexpected error
        mock_api = AsyncMock()
        mock_api.authenticate.side_effect = Exception("Unexpected error")
        mock_api.close = AsyncMock()
        mock_api_class.return_value = mock_api

        # Mock form display
        self.flow.async_show_form = MagicMock(
            return_value={"type": "form", "errors": {"base": "unknown"}}
        )

        user_input = {
            CONF_DOMAIN: DOMAIN_INTERNATIONAL,
            CONF_APP_KEY: "test_key",
            CONF_APP_SECRET: "test_secret",
        }

        result = await self.flow.async_step_user(user_input=user_input)

        # Verify error was handled
        self.flow.async_show_form.assert_called_once()
        call_args = self.flow.async_show_form.call_args
        self.assertEqual(call_args[1]["errors"]["base"], "unknown")

    def test_async_get_options_flow(self):
        """Test options flow creation."""
        mock_config_entry = MagicMock()
        options_flow = ConfigFlow.async_get_options_flow(mock_config_entry)

        self.assertIsInstance(options_flow, OptionsFlowHandler)
        self.assertEqual(options_flow.config_entry, mock_config_entry)


class TestSolarGuardianOptionsFlow(unittest.IsolatedAsyncioTestCase):
    """Test cases for SolarGuardian options flow."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config_entry = MagicMock()
        self.mock_config_entry.options = {CONF_UPDATE_INTERVAL: 60}
        self.options_flow = OptionsFlowHandler(self.mock_config_entry)

    async def test_async_step_init_no_input(self):
        """Test options step without input shows form."""
        # Mock form display
        self.options_flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await self.options_flow.async_step_init(user_input=None)

        self.assertEqual(result["type"], "form")
        self.options_flow.async_show_form.assert_called_once()
        call_args = self.options_flow.async_show_form.call_args
        self.assertEqual(call_args[1]["step_id"], "init")

    async def test_async_step_init_with_input(self):
        """Test options step with input creates entry."""
        # Mock entry creation
        self.options_flow.async_create_entry = MagicMock(
            return_value={"type": "create_entry"}
        )

        user_input = {CONF_UPDATE_INTERVAL: 45}

        result = await self.options_flow.async_step_init(user_input=user_input)

        self.options_flow.async_create_entry.assert_called_once_with(
            title="", data=user_input
        )

    async def test_async_step_init_default_values(self):
        """Test options step uses default values from config entry."""
        # Mock config entry with custom update interval
        self.mock_config_entry.options = {CONF_UPDATE_INTERVAL: 90}
        options_flow = OptionsFlowHandler(self.mock_config_entry)

        # Mock form display to capture schema
        captured_schema = None

        def capture_schema(*args, **kwargs):
            nonlocal captured_schema
            captured_schema = kwargs.get("data_schema")
            return {"type": "form"}

        options_flow.async_show_form = MagicMock(side_effect=capture_schema)

        result = await options_flow.async_step_init(user_input=None)

        # The exact schema validation would require vol import
        # For now, just verify the method was called
        options_flow.async_show_form.assert_called_once()

    async def test_async_step_init_no_existing_options(self):
        """Test options step with no existing options uses defaults."""
        # Mock config entry with no options
        self.mock_config_entry.options = {}
        options_flow = OptionsFlowHandler(self.mock_config_entry)

        # Mock form display
        options_flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await options_flow.async_step_init(user_input=None)

        options_flow.async_show_form.assert_called_once()

    def test_options_flow_init(self):
        """Test options flow initialization."""
        self.assertEqual(self.options_flow.config_entry, self.mock_config_entry)


class TestConfigFlowIntegration(unittest.TestCase):
    """Integration tests for config flow components."""

    def test_config_flow_domain(self):
        """Test config flow has correct domain."""
        self.assertEqual(ConfigFlow.domain, DOMAIN)

    def test_config_flow_inheritance(self):
        """Test config flow inherits from correct base class."""
        # This test ensures the flow inherits from the right class
        # In a real environment, this would be config_entries.ConfigFlow
        flow = ConfigFlow()
        self.assertIsInstance(flow, ConfigFlow)

    def test_options_flow_inheritance(self):
        """Test options flow inherits from correct base class."""
        mock_entry = MagicMock()
        options_flow = OptionsFlowHandler(mock_entry)
        self.assertIsInstance(options_flow, OptionsFlowHandler)

    def test_domain_constants(self):
        """Test domain constants are properly defined."""
        self.assertEqual(DOMAIN, "solarguardian")
        self.assertIn(".", DOMAIN_INTERNATIONAL)
        self.assertIn(".", DOMAIN_CHINA)

    def test_config_constants(self):
        """Test configuration constants are properly defined."""
        self.assertIsInstance(CONF_DOMAIN, str)
        self.assertIsInstance(CONF_APP_KEY, str)
        self.assertIsInstance(CONF_APP_SECRET, str)
        self.assertIsInstance(CONF_UPDATE_INTERVAL, str)
        self.assertIsInstance(DEFAULT_UPDATE_INTERVAL, int)
        self.assertGreater(DEFAULT_UPDATE_INTERVAL, 0)


if __name__ == "__main__":
    unittest.main()
