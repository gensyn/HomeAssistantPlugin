import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.level_dial.level_dial import LevelDial


class TestLevelDialRefresh(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_refresh_not_initialized(self, _):
        instance = LevelDial()
        instance.initialized = False
        instance.set_top_label = Mock()
        instance.refresh()

        instance.set_top_label.assert_not_called()

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_refresh_no_entity(self, _):
        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="")

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_media = Mock()
        instance.refresh()

        instance.set_top_label.assert_called_once_with("")
        instance.set_center_label.assert_called_once_with("")
        instance.set_media.assert_called_once_with()

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_refresh_entity_state_none_fetches_from_backend(self, _):
        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="light.desk")

        backend_mock = Mock()
        backend_mock.get_entity = Mock(return_value=None)
        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.plugin_base = plugin_base_mock
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_media = Mock()
        instance.refresh()

        backend_mock.get_entity.assert_called_once_with("light.desk")
        instance.set_top_label.assert_called_once_with("")
        instance.set_center_label.assert_called_once_with("N/A")
        instance.set_media.assert_called_once_with()

    @patch.object(LevelDial, 'set_enabled_disabled')
    @patch.object(LevelDial, '_load_customizations')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial._get_icon_image')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_refresh_entity_off(self, _, mock_get_icon, _load_cust, _set_ed):
        mock_get_icon.return_value = Mock(name="fake_image")

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="light.desk")
        settings_mock.get_label = Mock(return_value="Desk")
        settings_mock.get_customizations = Mock(return_value=[])

        state = {
            "state": "off",
            "attributes": {"friendly_name": "Desk Light", "brightness": None}
        }

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_media = Mock()
        instance.refresh(state=state)

        instance.set_top_label.assert_called_once_with("Desk", font_size=14)
        instance.set_center_label.assert_called_once_with(
            "Off", color=[100, 100, 100], font_size=28,
            outline_width=3, outline_color=[0, 0, 0]
        )
        instance.set_media.assert_called_once_with(image=mock_get_icon.return_value, size=0.75)

    @patch.object(LevelDial, 'set_enabled_disabled')
    @patch.object(LevelDial, '_load_customizations')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial._get_icon_image')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_refresh_entity_unavailable(self, _, mock_get_icon, _load_cust, _set_ed):
        mock_get_icon.return_value = Mock(name="fake_image")

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="light.desk")
        settings_mock.get_label = Mock(return_value="")
        settings_mock.get_customizations = Mock(return_value=[])

        state = {
            "state": "unavailable",
            "attributes": {"friendly_name": "Desk Light"}
        }

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_media = Mock()
        instance.refresh(state=state)

        instance.set_top_label.assert_called_once_with("Desk Light", font_size=14)
        instance.set_center_label.assert_called_once_with(
            "Off", color=[100, 100, 100], font_size=28,
            outline_width=3, outline_color=[0, 0, 0]
        )

    @patch.object(LevelDial, 'set_enabled_disabled')
    @patch.object(LevelDial, '_load_customizations')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial._get_icon_image')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_refresh_entity_on_with_brightness(self, _, mock_get_icon, _load_cust, _set_ed):
        mock_get_icon.return_value = Mock(name="fake_image")

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="light.desk")
        settings_mock.get_label = Mock(return_value="Desk")
        settings_mock.get_customizations = Mock(return_value=[])

        state = {
            "state": "on",
            "attributes": {"friendly_name": "Desk Light", "brightness": 128}
        }

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_media = Mock()
        instance.refresh(state=state)

        instance.set_top_label.assert_called_once_with("Desk", font_size=14)
        # 128/255 * 100 = 50.2 -> round to 50
        instance.set_center_label.assert_called_once_with(
            "50%", color=[255, 255, 255], font_size=28,
            outline_width=3, outline_color=[0, 0, 0]
        )

    @patch.object(LevelDial, 'set_enabled_disabled')
    @patch.object(LevelDial, '_load_customizations')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial._get_icon_image')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_refresh_fan_on_with_percentage(self, _, mock_get_icon, _load_cust, _set_ed):
        mock_get_icon.return_value = Mock(name="fake_image")

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="fan.bedroom")
        settings_mock.get_label = Mock(return_value="")
        settings_mock.get_customizations = Mock(return_value=[])

        state = {
            "state": "on",
            "attributes": {"friendly_name": "Bedroom Fan", "percentage": 75}
        }

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_media = Mock()
        instance.refresh(state=state)

        instance.set_top_label.assert_called_once_with("Bedroom Fan", font_size=14)
        instance.set_center_label.assert_called_once_with(
            "75%", color=[255, 255, 255], font_size=28,
            outline_width=3, outline_color=[0, 0, 0]
        )

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_refresh_unsupported_domain_shows_question_mark(self, _):
        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="switch.kitchen")
        settings_mock.get_label = Mock(return_value="Kitchen")
        settings_mock.get_customizations = Mock(return_value=[])

        state = {
            "state": "on",
            "attributes": {"friendly_name": "Kitchen Switch"}
        }

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_media = Mock()
        instance.refresh(state=state)

        instance.set_center_label.assert_called_once_with("?")

    @patch.object(LevelDial, 'set_enabled_disabled')
    @patch.object(LevelDial, '_load_customizations')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial._get_icon_image')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_refresh_level_none_shows_off(self, _, mock_get_icon, _load_cust, _set_ed):
        """Entity is 'on' but level attribute is missing -> shows Off."""
        mock_get_icon.return_value = Mock(name="fake_image")

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="light.desk")
        settings_mock.get_label = Mock(return_value="Desk")
        settings_mock.get_customizations = Mock(return_value=[])

        state = {
            "state": "on",
            "attributes": {"friendly_name": "Desk Light"}
        }

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_media = Mock()
        instance.refresh(state=state)

        instance.set_center_label.assert_called_once_with(
            "Off", color=[100, 100, 100], font_size=28,
            outline_width=3, outline_color=[0, 0, 0]
        )

    @patch.object(LevelDial, 'set_enabled_disabled')
    @patch.object(LevelDial, '_load_customizations')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial._get_icon_image')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_refresh_none_icon_does_not_set_media(self, _, mock_get_icon, _load_cust, _set_ed):
        mock_get_icon.return_value = None

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value="light.desk")
        settings_mock.get_label = Mock(return_value="Desk")
        settings_mock.get_customizations = Mock(return_value=[])

        state = {
            "state": "on",
            "attributes": {"friendly_name": "Desk Light", "brightness": 128}
        }

        instance = LevelDial()
        instance.initialized = True
        instance.settings = settings_mock
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_media = Mock()
        instance.refresh(state=state)

        instance.set_media.assert_not_called()
