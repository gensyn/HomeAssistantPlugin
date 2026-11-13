import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from HomeAssistantPlugin.backend import backend_const


class TestBackendLoadEntities(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    @patch("HomeAssistantPlugin.backend.home_assistant_backend.log.error")
    def test_load_entities_send_recv_not_successful(self, log_mock, _):
        send_and_recv_mock = Mock()
        send_and_recv_mock.return_value = (False, {}, "test_error")

        websocket_mock = Mock()
        websocket_mock.send_and_recv = send_and_recv_mock

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._websocket = websocket_mock
        instance._load_entities()

        send_and_recv_mock.assert_called_once()
        self.assertEqual(backend_const.GET_STATES, send_and_recv_mock.call_args.args[0])
        send_and_recv_mock.call_args.kwargs["on_response"](False, {}, "test_error")
        log_mock.assert_called_once_with(backend_const.ERROR_STATES.format("test_error"))
        self.assertEqual({}, instance._entities)

    @patch.object(HomeAssistantBackend, 'connect')
    def test_load_entities_success(self, _):
        existing_entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"}, backend_const.ACTIONS: {"123"}, backend_const.SUBSCRIPTION_ID: 2}},
            "sensor": {"sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C", "friendly_name": "Temperature Sensor"}, backend_const.ACTIONS: {"321"}, backend_const.SUBSCRIPTION_ID: 3}}
        }

        updated_entities = [
            {backend_const.ENTITY_ID: "light.living_room", backend_const.STATE: backend_const.OFF, backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"}},
            {backend_const.ENTITY_ID: "sensor.humidity", backend_const.STATE: "45", backend_const.ATTRIBUTES: {"unit_of_measurement": "%", "friendly_name": "Humidity Sensor"}}
        ]

        send_and_recv_mock = Mock()
        send_and_recv_mock.return_value = (True, updated_entities, backend_const.EMPTY_STRING)

        websocket_mock = Mock()
        websocket_mock.send_and_recv = send_and_recv_mock

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = existing_entities
        instance._websocket = websocket_mock
        instance._load_entities()
        send_and_recv_mock.call_args.kwargs["on_response"](True, updated_entities, backend_const.EMPTY_STRING)

        expected_entities = {
            "light": {"light.living_room": {backend_const.STATE: backend_const.OFF, backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"}, backend_const.ACTIONS: {"123"}, backend_const.SUBSCRIPTION_ID: 2}},
            "sensor": {"sensor.humidity": {backend_const.STATE: "45", backend_const.ATTRIBUTES: {"unit_of_measurement": "%", "friendly_name": "Humidity Sensor"}, backend_const.ACTIONS: set(), backend_const.SUBSCRIPTION_ID: -1}}
        }

        send_and_recv_mock.assert_called_once()
        self.assertEqual(backend_const.GET_STATES, send_and_recv_mock.call_args.args[0])
        self.assertEqual(expected_entities, instance._entities)
