import sys
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from HomeAssistantPlugin.backend import backend_const


class TestBackendGetEntity(unittest.TestCase):

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_get_entity_no_id(self, is_connected_mock, _):
        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True,
                                        backend_const.EMPTY_STRING)
        result = instance.get_entity(backend_const.EMPTY_STRING)

        expected = {
            backend_const.STATE: backend_const.NA,
            backend_const.ATTRIBUTES: {},
            backend_const.HA_CONNECTED: True
        }

        self.assertEqual(expected, result)
        is_connected_mock.assert_called_once()

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_get_entity_no_dot_in_id(self, is_connected_mock, _):
        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True,
                                        backend_const.EMPTY_STRING)
        result = instance.get_entity("domainentitiy")

        expected = {
            backend_const.STATE: backend_const.NA,
            backend_const.ATTRIBUTES: {},
            backend_const.HA_CONNECTED: True
        }

        self.assertEqual(expected, result)
        is_connected_mock.assert_called_once()

    @patch.object(HomeAssistantBackend, 'connect')
    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_get_entity_success(self, is_connected_mock, _):
        entities: dict[str, dict[str, Any]] = {
            "domain1": {
                "domain1.entity1": {
                    "keys": {
                        "1.1": "1.2"
                    },
                    "subscription_id": "1.3"
                },
                "domain1.entity2": {
                    "keys": {
                        "2.1": "2.2"
                    },
                    "subscription_id": "2.3",
                    "state": "on",
                    "attributes": {
                        "brightness": 100,
                    }
                }
            },
            "domain2": {
                "domain2.entity3": {
                    "keys": {
                        "3.1": "3.2"
                    },
                    "subscription_id": "3.3"
                }
            }
        }

        instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True,
                                        backend_const.EMPTY_STRING)
        instance._entities = entities
        result = instance.get_entity("domain1.entity2")

        expected = entities["domain1"]["domain1.entity2"]
        expected[backend_const.HA_CONNECTED] = True

        self.assertEqual(expected, result)
        self.assertEqual(2, is_connected_mock.call_count)
