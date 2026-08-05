import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from HomeAssistantPlugin.backend import backend_const


class TestBackendRemoveTrackedEntity(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    def test_remove_tracked_entity_no_entity(self, _):
        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"},
                                            backend_const.ACTIONS: {"123"}, backend_const.SUBSCRIPTION_ID: 2}},
            "sensor": {"sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C",
                                                                                    "friendly_name": "Temperature Sensor"},
                                              backend_const.ACTIONS: {"321"}, backend_const.SUBSCRIPTION_ID: 3}}
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities

        instance.remove_tracked_entity(backend_const.EMPTY_STRING, "123")

        self.assertEqual({"123"}, instance._entities["light"]["light.living_room"][backend_const.ACTIONS])
        self.assertEqual(2, instance._entities["light"]["light.living_room"][backend_const.SUBSCRIPTION_ID])

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=False)
    def test_remove_tracked_entity_not_connected(self, _, __):
        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"},
                                            backend_const.ACTIONS: {"123"}, backend_const.SUBSCRIPTION_ID: 2}},
            "sensor": {"sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C",
                                                                                    "friendly_name": "Temperature Sensor"},
                                              backend_const.ACTIONS: {"321"}, backend_const.SUBSCRIPTION_ID: 3}}
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities

        instance.remove_tracked_entity("light.living_room", "123")

        self.assertEqual({"123"}, instance._entities["light"]["light.living_room"][backend_const.ACTIONS])
        self.assertEqual(2, instance._entities["light"]["light.living_room"][backend_const.SUBSCRIPTION_ID])

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_remove_tracked_entity_still_tracked_by_other_action(self, _, __):
        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"},
                                            backend_const.ACTIONS: {"123", "321"}, backend_const.SUBSCRIPTION_ID: 2}},
            "sensor": {"sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C",
                                                                                    "friendly_name": "Temperature Sensor"},
                                              backend_const.ACTIONS: {"321"}, backend_const.SUBSCRIPTION_ID: 3}}
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities

        instance.remove_tracked_entity("light.living_room", "123")

        self.assertEqual({"321"}, instance._entities["light"]["light.living_room"][backend_const.ACTIONS])
        self.assertEqual(2, instance._entities["light"]["light.living_room"][backend_const.SUBSCRIPTION_ID])

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_remove_tracked_entity_success(self, _, __):
        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"},
                                            backend_const.ACTIONS: {"123"}, backend_const.SUBSCRIPTION_ID: 2}},
            "sensor": {"sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C",
                                                                                    "friendly_name": "Temperature Sensor"},
                                              backend_const.ACTIONS: {"321"}, backend_const.SUBSCRIPTION_ID: 3}}
        }

        create_message_mock = Mock()
        create_message_mock.return_value = {}

        send_mock = Mock()

        websocket_mock = Mock()
        websocket_mock.create_message = create_message_mock
        websocket_mock.send = send_mock

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._websocket = websocket_mock
        instance._entities = entities

        instance.remove_tracked_entity("light.living_room", "123")

        send_mock.assert_called_once_with({backend_const.SUBSCRIPTION_ID: 2})
        self.assertEqual(set(), instance._entities["light"]["light.living_room"][backend_const.ACTIONS])
        self.assertEqual(-1, instance._entities["light"]["light.living_room"][backend_const.SUBSCRIPTION_ID])

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_remove_tracked_entity_unknown_domain(self, _, __):
        entities = {
            "sensor": {"sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {},
                                              backend_const.ACTIONS: {"321"}, backend_const.SUBSCRIPTION_ID: 3}}
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities

        # Should not raise KeyError when domain is not in _entities
        instance.remove_tracked_entity("light.living_room", "123")

        self.assertEqual({"321"}, instance._entities["sensor"]["sensor.temperature"][backend_const.ACTIONS])

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_remove_tracked_entity_action_not_registered(self, _, __):
        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {},
                                            backend_const.ACTIONS: {"321"}, backend_const.SUBSCRIPTION_ID: 2}},
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities

        # Should not raise KeyError when action callback is not in the set
        instance.remove_tracked_entity("light.living_room", "999")

        self.assertEqual({"321"}, instance._entities["light"]["light.living_room"][backend_const.ACTIONS])
        self.assertEqual(2, instance._entities["light"]["light.living_room"][backend_const.SUBSCRIPTION_ID])

