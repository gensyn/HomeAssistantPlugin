import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from HomeAssistantPlugin.backend import backend_const


class TestBackendGetEntities(unittest.TestCase):

    def test_get_entities_domain_empty(self):
        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        result = instance.get_entities(backend_const.EMPTY_STRING)

        self.assertEqual([], result)

    def test_get_entities_already_loaded(self):
        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"}, backend_const.ACTIONS: {"abc": "123"}, backend_const.SUBSCRIPTION_ID: 2}},
            "sensor": {
                "sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C", "friendly_name": "Temperature Sensor"}, backend_const.ACTIONS: {"cba": "321"}, backend_const.SUBSCRIPTION_ID: 3},
                "sensor.humidity": {backend_const.STATE: "45", backend_const.ATTRIBUTES: {"unit_of_measurement": "%", "friendly_name": "Humidity Sensor"}, backend_const.ACTIONS: {"bac": "213"}, backend_const.SUBSCRIPTION_ID: 4}
            }
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        instance._entities = entities
        result = instance.get_entities("light")
        self.assertEqual(["light.living_room"], result)
        result = instance.get_entities("sensor")
        self.assertEqual(["sensor.temperature", "sensor.humidity"], result)

    @patch.object(HomeAssistantBackend, '_load_entities')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_get_entities_load_entities(self, _, load_entities_mock):
        entities = {
            "light": {"light.living_room": {backend_const.STATE: "on", backend_const.ATTRIBUTES: {"friendly_name": "Living Room Light"}, backend_const.ACTIONS: {"abc": "123"}, backend_const.SUBSCRIPTION_ID: 2}},
            "sensor": {
                "sensor.temperature": {backend_const.STATE: "23", backend_const.ATTRIBUTES: {"unit_of_measurement": "°C", "friendly_name": "Temperature Sensor"}, backend_const.ACTIONS: {"cba": "321"}, backend_const.SUBSCRIPTION_ID: 3},
                "sensor.humidity": {backend_const.STATE: "45", backend_const.ATTRIBUTES: {"unit_of_measurement": "%", "friendly_name": "Humidity Sensor"}, backend_const.ACTIONS: {"bac": "213"}, backend_const.SUBSCRIPTION_ID: 4}
            }
        }

        load_entities_mock.side_effect = lambda: setattr(instance, '_entities', entities)

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True, backend_const.EMPTY_STRING)
        result = instance.get_entities("light")
        self.assertEqual(["light.living_room"], result)
        result = instance.get_entities("sensor")
        self.assertEqual(["sensor.temperature", "sensor.humidity"], result)
