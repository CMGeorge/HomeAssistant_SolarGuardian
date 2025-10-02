"""Integration test for existing test_integration.py script."""

import json
import os

# Add project root to path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "../../")
sys.path.insert(0, project_root)


class TestExistingIntegrationScript(unittest.IsolatedAsyncioTestCase):
    """Test the existing test_integration.py script."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up after test."""
        os.chdir(self.original_cwd)
        # Clean up temp directory
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_test_credentials_environment(self):
        """Test loading credentials from environment variables."""
        # Import after changing directory
        sys.path.insert(0, project_root)
        from test_integration import load_test_credentials

        with patch.dict(
            os.environ,
            {
                "SOLARGUARDIAN_DOMAIN": "test.domain.com",
                "SOLARGUARDIAN_APP_KEY": "test_key",
                "SOLARGUARDIAN_APP_SECRET": "test_secret",
            },
        ):
            credentials = load_test_credentials()

            self.assertIsNotNone(credentials)
            self.assertEqual(len(credentials), 3)
            self.assertEqual(credentials[0], "test.domain.com")
            self.assertEqual(credentials[1], "test_key")
            self.assertEqual(credentials[2], "test_secret")

    def test_load_test_credentials_short_env(self):
        """Test loading credentials from short environment variables."""
        sys.path.insert(0, project_root)
        from test_integration import load_test_credentials

        with patch.dict(
            os.environ, {"APPKEY": "short_key", "APPSECRET": "short_secret"}, clear=True
        ):
            # No domain, so should get None or partial
            credentials = load_test_credentials()
            # Should be None because domain is missing
            self.assertIsNone(credentials)

    def test_load_test_credentials_config_file(self):
        """Test loading credentials from config file."""
        sys.path.insert(0, project_root)
        from test_integration import load_test_credentials

        # Create test config file
        config_data = {
            "domain": "config.domain.com",
            "app_key": "config_key",
            "app_secret": "config_secret",
        }

        with open("test_config.json", "w") as f:
            json.dump(config_data, f)

        # Clear environment
        with patch.dict(os.environ, {}, clear=True):
            credentials = load_test_credentials()

            self.assertIsNotNone(credentials)
            self.assertEqual(credentials[0], "config.domain.com")
            self.assertEqual(credentials[1], "config_key")
            self.assertEqual(credentials[2], "config_secret")

    def test_create_test_config(self):
        """Test creating test config template."""
        sys.path.insert(0, project_root)
        from test_integration import create_test_config

        create_test_config()

        self.assertTrue(os.path.exists("test_config.json"))

        with open("test_config.json") as f:
            config = json.load(f)

        self.assertIn("domain", config)
        self.assertIn("app_key", config)
        self.assertIn("app_secret", config)
        self.assertEqual(config["domain"], "glapi.mysolarguardian.com")

    @patch("test_integration.input", return_value="n")
    async def test_main_no_credentials(self, mock_input):
        """Test main function with no credentials."""
        sys.path.insert(0, project_root)

        # Import and patch the main function
        with patch.dict(os.environ, {}, clear=True):
            from test_integration import main

            # Should exit gracefully when no credentials
            with patch("builtins.print") as mock_print:
                await main()

                # Verify error message was printed
                print_calls = [str(call) for call in mock_print.call_args_list]
                error_found = any(
                    "No test credentials found" in call for call in print_calls
                )
                self.assertTrue(error_found)

    async def test_api_connection_mock(self):
        """Test API connection with mocked responses."""
        sys.path.insert(0, project_root)
        from test_integration import test_api_connection

        # Mock the API class
        with patch("test_integration.SolarGuardianAPI") as mock_api_class:
            mock_api = MagicMock()
            mock_api_class.return_value = mock_api

            # Configure mock responses
            mock_api.authenticate.return_value = True
            mock_api.get_power_stations.return_value = {
                "data": {"list": [{"id": 123, "powerStationName": "Test Station"}]}
            }
            mock_api.get_devices.return_value = {
                "data": {"list": [{"id": 456, "equipmentName": "Test Device"}]}
            }
            mock_api.get_device_parameters.return_value = {
                "data": {"variableGroupList": []}
            }
            mock_api.close = MagicMock()

            # Test the connection
            await test_api_connection(
                domain="test.domain.com", app_key="test_key", app_secret="test_secret"
            )

            # Verify API was called
            mock_api.authenticate.assert_called_once()
            mock_api.get_power_stations.assert_called_once()
            mock_api.close.assert_called_once()

    def test_script_imports(self):
        """Test that the script can be imported without errors."""
        sys.path.insert(0, project_root)

        try:
            import test_integration

            # Verify key functions exist
            self.assertTrue(hasattr(test_integration, "load_test_credentials"))
            self.assertTrue(hasattr(test_integration, "create_test_config"))
            self.assertTrue(hasattr(test_integration, "test_api_connection"))
            self.assertTrue(hasattr(test_integration, "main"))

        except ImportError as e:
            self.fail(f"Failed to import test_integration: {e}")

    def test_constants_available(self):
        """Test that required constants are available."""
        sys.path.insert(0, project_root)

        try:
            from test_integration import DOMAIN_CHINA, DOMAIN_INTERNATIONAL

            self.assertIsInstance(DOMAIN_INTERNATIONAL, str)
            self.assertIsInstance(DOMAIN_CHINA, str)
            self.assertIn(".", DOMAIN_INTERNATIONAL)
            self.assertIn(".", DOMAIN_CHINA)

        except ImportError as e:
            self.fail(f"Failed to import constants: {e}")


class TestIntegrationScriptFunctionality(unittest.TestCase):
    """Test the functionality aspects of the integration script."""

    def test_credential_precedence(self):
        """Test that environment variables take precedence over config file."""
        import shutil
        import tempfile

        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()

        try:
            os.chdir(temp_dir)
            sys.path.insert(0, project_root)

            # Create config file
            config_data = {
                "domain": "config.domain.com",
                "app_key": "config_key",
                "app_secret": "config_secret",
            }

            with open("test_config.json", "w") as f:
                json.dump(config_data, f)

            from test_integration import load_test_credentials

            # Test with environment variables - should override config file
            with patch.dict(
                os.environ,
                {
                    "SOLARGUARDIAN_DOMAIN": "env.domain.com",
                    "SOLARGUARDIAN_APP_KEY": "env_key",
                    "SOLARGUARDIAN_APP_SECRET": "env_secret",
                },
            ):
                credentials = load_test_credentials()

                self.assertEqual(credentials[0], "env.domain.com")
                self.assertEqual(credentials[1], "env_key")

        finally:
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_error_handling_invalid_config(self):
        """Test error handling with invalid config file."""
        import shutil
        import tempfile

        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()

        try:
            os.chdir(temp_dir)
            sys.path.insert(0, project_root)

            # Create invalid JSON file
            with open("test_config.json", "w") as f:
                f.write("invalid json content")

            from test_integration import load_test_credentials

            with patch.dict(os.environ, {}, clear=True):
                with patch("builtins.print") as mock_print:
                    credentials = load_test_credentials()

                    self.assertIsNone(credentials)
                    # Should have printed error message
                    self.assertTrue(mock_print.called)

        finally:
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
