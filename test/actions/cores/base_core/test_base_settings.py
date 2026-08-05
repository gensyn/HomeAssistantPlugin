import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions import const
from HomeAssistantPlugin.actions.cores.base_core.base_settings import BaseSettings
from HomeAssistantPlugin.actions.cores.base_core.base_settings import DEFAULT_SETTINGS


class TestBaseSettingsInit(unittest.TestCase):

    def test_init_with_default(self):
        settings = {
            "other_setting": {
                "key": "value",
            },
        }

        action_mock = Mock()
        action_mock.get_settings.return_value = settings

        settings_expected = deepcopy(settings)
        settings_expected[const.SETTING_ENTITY] = deepcopy(DEFAULT_SETTINGS)

        BaseSettings(action_mock)

        action_mock.set_settings.assert_called_once_with(settings_expected)

    def test_base_settings_success(self):
        domain = "light"
        entity = "light.kitchen"

        settings = {
            const.SETTING_ENTITY: {
                const.SETTING_DOMAIN: domain,
                const.SETTING_ENTITY: entity
            },
        }

        action_mock = Mock()
        action_mock.get_settings.return_value = settings

        # test init
        instance = BaseSettings(action_mock)

        action_mock.get_settings.assert_called_once()

        # test get_domain
        self.assertEqual(domain, instance.get_domain())

        # test get_entity
        self.assertEqual(entity, instance.get_entity())

        # test reset
        settings_expected_for_reset = {
            const.SETTING_ENTITY: {
                const.SETTING_DOMAIN: "switch",
                const.SETTING_ENTITY: const.EMPTY_STRING
            }
        }

        instance.reset("switch")

        action_mock.set_settings.assert_called_once_with(settings_expected_for_reset)

    def test_missing_entity_key(self):
        settings = {}
        action_mock = Mock()
        action_mock.get_settings.return_value = settings

        instance = BaseSettings(action_mock)
        # Clear settings to simulate runtime loss of entity key
        action_mock.get_settings.return_value = {}

        self.assertEqual(const.EMPTY_STRING, instance.get_entity())
        self.assertEqual(const.EMPTY_STRING, instance.get_domain())

