import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from HomeAssistantPlugin.backend import backend_const


class TestBackendGetActions(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    @patch.object(HomeAssistantBackend, '_load_actions')
    def test_get_actions_no_actions(self, load_actions_mock, _, __):
        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)

        load_actions_mock.side_effect = lambda: setattr(instance, '_actions', {})

        instance.get_actions("light")

        self.assertEqual({}, instance._actions)

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    @patch.object(HomeAssistantBackend, '_load_actions')
    def test_get_actions_success(self, load_actions_mock, _, __):
        light = {
            "turn_on": {
                "fields": {
                    "brightness": {"selector": {"number": {"min": 0, "max": 255}}},
                    "color_temp": {"selector": {"number": {"min": 153, "max": 500}}},
                }
            },
            "turn_off": {}
        }

        switch = {
            "toggle": {"fields": {
                "delay": {"selector": {"number": {"min": 0, "max": 60}}}
            }}
        }

        actions = {
            "light": light,
            "switch": switch
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)

        load_actions_mock.side_effect = lambda: setattr(instance, '_actions', actions)

        result = instance.get_actions("light")
        self.assertEqual(light, result)
        result = instance.get_actions("switch")
        self.assertEqual(switch, result)
