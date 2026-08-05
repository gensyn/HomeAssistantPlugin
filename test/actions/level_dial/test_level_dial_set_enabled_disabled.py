import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.level_dial import level_const
from HomeAssistantPlugin.actions.level_dial.level_dial import LevelDial


class TestLevelDialSetEnabledDisabled(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_set_enabled_disabled_not_initialized(self, _):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value="light")

        instance = LevelDial()
        instance.settings = settings_mock
        instance.initialized = False
        instance.set_enabled_disabled()

        settings_mock.get_domain.assert_not_called()

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.set_enabled_disabled')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_set_enabled_disabled_no_entity(self, _, super_set_mock):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value="")
        settings_mock.get_entity = Mock(return_value="")

        label_entry_mock = Mock()
        label_entry_mock.widget = Mock()
        label_entry_mock.widget.set_sensitive = Mock()

        step_scale_mock = Mock()
        step_scale_mock.widget = Mock()
        step_scale_mock.widget.set_sensitive = Mock()
        step_scale_mock.widget.set_subtitle = Mock()

        locale_manager = {
            level_const.LABEL_LEVEL_NO_ENTITY: "No entity selected"
        }

        batch_delay_scale_mock = Mock()
        batch_delay_scale_mock.widget = Mock()
        batch_delay_scale_mock.widget.set_sensitive = Mock()
        batch_delay_scale_mock.widget.set_subtitle = Mock()

        instance = LevelDial()
        instance.settings = settings_mock
        instance.initialized = True
        instance.lm = locale_manager
        instance.label_entry = label_entry_mock
        instance.step_scale = step_scale_mock
        instance.batch_delay_scale = batch_delay_scale_mock
        instance.set_enabled_disabled()

        super_set_mock.assert_called_once()
        label_entry_mock.widget.set_sensitive.assert_called_once_with(False)
        step_scale_mock.widget.set_sensitive.assert_called_once_with(False)
        step_scale_mock.widget.set_subtitle.assert_called_once_with("No entity selected")
        batch_delay_scale_mock.widget.set_sensitive.assert_called_once_with(False)
        batch_delay_scale_mock.widget.set_subtitle.assert_called_once_with("No entity selected")

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.set_enabled_disabled')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_set_enabled_disabled_has_entity(self, _, super_set_mock):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value="light")
        settings_mock.get_entity = Mock(return_value="light.desk")

        label_entry_mock = Mock()
        label_entry_mock.widget = Mock()
        label_entry_mock.widget.set_sensitive = Mock()

        step_scale_mock = Mock()
        step_scale_mock.widget = Mock()
        step_scale_mock.widget.set_sensitive = Mock()
        step_scale_mock.widget.set_subtitle = Mock()

        batch_delay_scale_mock = Mock()
        batch_delay_scale_mock.widget = Mock()
        batch_delay_scale_mock.widget.set_sensitive = Mock()
        batch_delay_scale_mock.widget.set_subtitle = Mock()

        instance = LevelDial()
        instance.settings = settings_mock
        instance.initialized = True
        instance.lm = {}
        instance.label_entry = label_entry_mock
        instance.step_scale = step_scale_mock
        instance.batch_delay_scale = batch_delay_scale_mock
        instance.set_enabled_disabled()

        super_set_mock.assert_called_once()
        label_entry_mock.widget.set_sensitive.assert_called_once_with(True)
        step_scale_mock.widget.set_sensitive.assert_called_once_with(True)
        step_scale_mock.widget.set_subtitle.assert_called_once_with(level_const.EMPTY_STRING)
        batch_delay_scale_mock.widget.set_sensitive.assert_called_once_with(True)
        batch_delay_scale_mock.widget.set_subtitle.assert_called_once_with(level_const.EMPTY_STRING)

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.set_enabled_disabled')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_set_enabled_disabled_domain_only_no_entity(self, _, super_set_mock):
        """Domain set but entity empty -> disabled."""
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value="light")
        settings_mock.get_entity = Mock(return_value="")

        label_entry_mock = Mock()
        label_entry_mock.widget = Mock()
        label_entry_mock.widget.set_sensitive = Mock()

        step_scale_mock = Mock()
        step_scale_mock.widget = Mock()
        step_scale_mock.widget.set_sensitive = Mock()
        step_scale_mock.widget.set_subtitle = Mock()

        batch_delay_scale_mock = Mock()
        batch_delay_scale_mock.widget = Mock()
        batch_delay_scale_mock.widget.set_sensitive = Mock()
        batch_delay_scale_mock.widget.set_subtitle = Mock()

        locale_manager = {
            level_const.LABEL_LEVEL_NO_ENTITY: "No entity selected"
        }

        instance = LevelDial()
        instance.settings = settings_mock
        instance.initialized = True
        instance.lm = locale_manager
        instance.label_entry = label_entry_mock
        instance.step_scale = step_scale_mock
        instance.batch_delay_scale = batch_delay_scale_mock
        instance.set_enabled_disabled()

        label_entry_mock.widget.set_sensitive.assert_called_once_with(False)
        step_scale_mock.widget.set_sensitive.assert_called_once_with(False)
