import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.level_dial.level_dial import LevelDial


class TestLevelDialShortUp(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_short_up_not_initialized(self, _):
        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="light.desk")

        instance = LevelDial()
        instance.initialized = False
        instance.settings = settings_mock
        instance._on_dial_short_up()

        settings_mock.get_entity.assert_not_called()

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_short_up_no_entity(self, _):
        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="")

        backend_mock = Mock()
        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.plugin_base = plugin_base_mock
        instance._on_dial_short_up()

        backend_mock.perform_action.assert_not_called()

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_short_up_unsupported_domain(self, _):
        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="switch.kitchen")

        backend_mock = Mock()
        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.plugin_base = plugin_base_mock
        instance._on_dial_short_up()

        backend_mock.perform_action.assert_not_called()

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_short_up_light_toggles(self, _):
        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="light.desk")

        backend_mock = Mock()
        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.plugin_base = plugin_base_mock
        instance._on_dial_short_up()

        backend_mock.perform_action.assert_called_once_with("light", "toggle", "light.desk", {})

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_short_up_fan_toggles(self, _):
        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="fan.bedroom")

        backend_mock = Mock()
        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.plugin_base = plugin_base_mock
        instance._on_dial_short_up()

        backend_mock.perform_action.assert_called_once_with("fan", "toggle", "fan.bedroom", {})

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_short_up_media_player_play_pause(self, _):
        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="media_player.speaker")

        backend_mock = Mock()
        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.plugin_base = plugin_base_mock
        instance._on_dial_short_up()

        backend_mock.perform_action.assert_called_once_with(
            "media_player", "media_play_pause", "media_player.speaker", {}
        )

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_short_up_cover_toggles(self, _):
        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="cover.garage")

        backend_mock = Mock()
        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.plugin_base = plugin_base_mock
        instance._on_dial_short_up()

        backend_mock.perform_action.assert_called_once_with("cover", "toggle", "cover.garage", {})
