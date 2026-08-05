import sys
import unittest
from pathlib import Path
from unittest.mock import patch, call

absolute_mock_path = str(Path(__file__).parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from src.backend.PluginManager.ActionInputSupport import ActionInputSupport
from src.backend.DeckManagement.InputIdentifier import Input

from HomeAssistantPlugin import const
from HomeAssistantPlugin.main import HomeAssistant
from HomeAssistantPlugin.actions.perform_action.perform_const import PERFORM_ACTION
from HomeAssistantPlugin.actions.show_icon.icon_const import SHOW_ICON
from HomeAssistantPlugin.actions.show_text.text_const import SHOW_TEXT
from HomeAssistantPlugin.actions.level_dial.level_const import LEVEL_DIAL


class TestMainInit(unittest.TestCase):

    @patch.object(HomeAssistant, "add_action_holder")
    @patch.object(HomeAssistant, "register")
    @patch("HomeAssistantPlugin.main.ConnectionSettings")
    @patch("HomeAssistantPlugin.main.HomeAssistantBackend")
    @patch("HomeAssistantPlugin.main.PerformAction")
    @patch("HomeAssistantPlugin.main.ShowIcon")
    @patch("HomeAssistantPlugin.main.ShowText")
    @patch("HomeAssistantPlugin.main.LevelDial")
    @patch("HomeAssistantPlugin.main.ActionHolder")
    def test_init_success(self, action_holder_mock, level_dial_mock, show_text_mock, show_icon_mock, perform_action_mock, backend_mock, settings_mock,
                  register_mock, add_action_holder_mock):
        action_holder_mock.side_effect = [perform_action_mock, show_icon_mock, show_text_mock, level_dial_mock]

        host: str = "localhost"
        port: str = "8123"
        ssl: bool = True
        verify_certificate: bool = False
        token: str = "abc"

        settings_mock.return_value = settings_mock
        settings_mock.get_host = lambda: host
        settings_mock.get_port = lambda: port
        settings_mock.get_ssl = lambda: ssl
        settings_mock.get_verify_certificate = lambda: verify_certificate
        settings_mock.get_token = lambda: token

        instance = HomeAssistant()

        self.assertIsNone(instance.host_entry)
        self.assertIsNone(instance.port_entry)
        self.assertIsNone(instance.ssl_switch)
        self.assertIsNone(instance.verify_certificate_switch)
        self.assertIsNone(instance.token_entry)

        self.assertEqual(4, action_holder_mock.call_count)
        action_holder_mock.assert_has_calls([
            call(
                plugin_base=instance,
                action_base=perform_action_mock,
                action_id="HomeAssistantPlugin::PerformAction",
                action_name=PERFORM_ACTION,
                action_support={
                    Input.Key: ActionInputSupport.SUPPORTED,
                    Input.Dial: ActionInputSupport.SUPPORTED,
                    Input.Touchscreen: ActionInputSupport.UNSUPPORTED
                }
            ),
            call(
                plugin_base=instance,
                action_base=show_icon_mock,
                action_id="HomeAssistantPlugin::ShowIcon",
                action_name=SHOW_ICON,
                action_support={
                    Input.Key: ActionInputSupport.SUPPORTED,
                    Input.Dial: ActionInputSupport.SUPPORTED,
                    Input.Touchscreen: ActionInputSupport.UNSUPPORTED
                }
            ),
            call(
                plugin_base=instance,
                action_base=show_text_mock,
                action_id="HomeAssistantPlugin::ShowText",
                action_name=SHOW_TEXT,
                action_support={
                    Input.Key: ActionInputSupport.SUPPORTED,
                    Input.Dial: ActionInputSupport.SUPPORTED,
                    Input.Touchscreen: ActionInputSupport.UNSUPPORTED
                }
            ),
            call(
                plugin_base=instance,
                action_base=level_dial_mock,
                action_id="HomeAssistantPlugin::LevelDial",
                action_name=LEVEL_DIAL,
                action_support={
                    Input.Key: ActionInputSupport.UNSUPPORTED,
                    Input.Dial: ActionInputSupport.SUPPORTED,
                    Input.Touchscreen: ActionInputSupport.UNSUPPORTED
                }
            )
        ])

        self.assertEqual(4, add_action_holder_mock.call_count)
        add_action_holder_mock.assert_has_calls([
            call(perform_action_mock),
            call(show_icon_mock),
            call(show_text_mock),
            call(level_dial_mock)
        ])

        self.assertEqual(1, register_mock.call_count)
        register_mock.assert_called_once_with(
            plugin_name=const.HOME_ASSISTANT,
            github_repo="https://github.com/gensyn/HomeAssistantPlugin",
            plugin_version="1.1.1",
            app_version="1.5.0-beta"
        )

        settings_mock.assert_called_once_with(instance)

        backend_mock.assert_called_once_with(host, port, ssl, verify_certificate, token)

