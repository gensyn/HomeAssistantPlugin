import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.level_dial import level_const
from HomeAssistantPlugin.actions.level_dial.level_settings import LevelDialSettings
from HomeAssistantPlugin.actions.level_dial.level_settings import DEFAULT_SETTINGS


class TestLevelDialSettingsInit(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.cores.base_core.base_settings.BaseSettings.__init__', autospec=True)
    def test_init_with_default(self, super_init_mock):
        action_mock = Mock()

        settings = {
            "other_setting": {
                "key": "value",
            },
        }

        action_mock.get_settings.return_value = deepcopy(settings)

        settings_expected = deepcopy(settings)
        settings_expected[level_const.SETTING_LEVEL] = deepcopy(DEFAULT_SETTINGS)

        def super_init(instance, action):
            instance._action = action

        super_init_mock.side_effect = super_init

        instance = LevelDialSettings(action_mock)

        self.assertEqual(settings_expected, instance._action.get_settings())
        super_init_mock.assert_called_once_with(instance, action_mock)
        action_mock.set_settings.assert_called_once_with(settings_expected)

    @patch('HomeAssistantPlugin.actions.cores.base_core.base_settings.BaseSettings.__init__', autospec=True)
    def test_init_existing_settings_preserved(self, super_init_mock):
        action_mock = Mock()

        settings = {
            level_const.SETTING_LEVEL: {
                level_const.SETTING_STEP: 20,
                level_const.SETTING_LABEL: "Custom Label",
            },
        }

        action_mock.get_settings.return_value = deepcopy(settings)

        def super_init(instance, action):
            instance._action = action

        super_init_mock.side_effect = super_init

        instance = LevelDialSettings(action_mock)

        # Should not overwrite existing settings
        action_mock.set_settings.assert_not_called()
        self.assertEqual(20, instance._action.get_settings()[level_const.SETTING_LEVEL][level_const.SETTING_STEP])

    @patch('HomeAssistantPlugin.actions.cores.base_core.base_settings.BaseSettings.__init__', autospec=True)
    def test_get_step(self, super_init_mock):
        action_mock = Mock()

        settings = {
            level_const.SETTING_LEVEL: {
                level_const.SETTING_STEP: 15,
                level_const.SETTING_LABEL: "",
            },
        }

        action_mock.get_settings.return_value = deepcopy(settings)

        def super_init(instance, action):
            instance._action = action

        super_init_mock.side_effect = super_init

        instance = LevelDialSettings(action_mock)
        self.assertEqual(15, instance.get_step())

    @patch('HomeAssistantPlugin.actions.cores.base_core.base_settings.BaseSettings.__init__', autospec=True)
    def test_get_label(self, super_init_mock):
        action_mock = Mock()

        settings = {
            level_const.SETTING_LEVEL: {
                level_const.SETTING_STEP: 10,
                level_const.SETTING_LABEL: "My Light",
            },
        }

        action_mock.get_settings.return_value = deepcopy(settings)

        def super_init(instance, action):
            instance._action = action

        super_init_mock.side_effect = super_init

        instance = LevelDialSettings(action_mock)
        self.assertEqual("My Light", instance.get_label())

    @patch('HomeAssistantPlugin.actions.cores.base_core.base_settings.BaseSettings.__init__', autospec=True)
    def test_get_label_default_when_missing(self, super_init_mock):
        action_mock = Mock()

        settings = {
            level_const.SETTING_LEVEL: {
                level_const.SETTING_STEP: 10,
            },
        }

        action_mock.get_settings.return_value = deepcopy(settings)

        def super_init(instance, action):
            instance._action = action

        super_init_mock.side_effect = super_init

        instance = LevelDialSettings(action_mock)
        self.assertEqual(level_const.DEFAULT_LABEL, instance.get_label())

    @patch('HomeAssistantPlugin.actions.cores.base_core.base_settings.BaseSettings.__init__', autospec=True)
    def test_get_batch_delay(self, super_init_mock):
        action_mock = Mock()

        settings = {
            level_const.SETTING_LEVEL: {
                level_const.SETTING_STEP: 10,
                level_const.SETTING_LABEL: "",
                level_const.SETTING_BATCH_DELAY: 200,
            },
        }

        action_mock.get_settings.return_value = deepcopy(settings)

        def super_init(instance, action):
            instance._action = action

        super_init_mock.side_effect = super_init

        instance = LevelDialSettings(action_mock)
        self.assertEqual(200, instance.get_batch_delay())

    @patch('HomeAssistantPlugin.actions.cores.base_core.base_settings.BaseSettings.__init__', autospec=True)
    def test_get_batch_delay_default_when_missing(self, super_init_mock):
        action_mock = Mock()

        settings = {
            level_const.SETTING_LEVEL: {
                level_const.SETTING_STEP: 10,
            },
        }

        action_mock.get_settings.return_value = deepcopy(settings)

        def super_init(instance, action):
            instance._action = action

        super_init_mock.side_effect = super_init

        instance = LevelDialSettings(action_mock)
        self.assertEqual(level_const.DEFAULT_BATCH_DELAY, instance.get_batch_delay())

    @patch('HomeAssistantPlugin.actions.cores.base_core.base_settings.BaseSettings.__init__', autospec=True)
    @patch('HomeAssistantPlugin.actions.cores.base_core.base_settings.BaseSettings.reset')
    def test_reset(self, super_reset_mock, super_init_mock):
        action_mock = Mock()

        settings = {
            level_const.SETTING_LEVEL: {
                level_const.SETTING_STEP: 25,
                level_const.SETTING_LABEL: "Custom",
                level_const.SETTING_BATCH_DELAY: 300,
            },
        }

        action_mock.get_settings.return_value = deepcopy(settings)

        def super_init(instance, action):
            instance._action = action

        super_init_mock.side_effect = super_init

        instance = LevelDialSettings(action_mock)

        domain = "light"
        instance.reset(domain)

        super_reset_mock.assert_called_once_with(domain)

        expected_settings = {
            level_const.SETTING_LEVEL: {
                level_const.SETTING_STEP: level_const.DEFAULT_STEP,
                level_const.SETTING_LABEL: level_const.DEFAULT_LABEL,
                level_const.SETTING_BATCH_DELAY: level_const.DEFAULT_BATCH_DELAY,
            },
        }

        self.assertEqual(expected_settings, instance._action.get_settings())
        action_mock.set_settings.assert_called_with(expected_settings)
