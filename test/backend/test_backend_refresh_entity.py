import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from HomeAssistantPlugin.backend import backend_const


class TestBackendRefreshEntity(unittest.TestCase):

    def _create(self):
        with patch.object(HomeAssistantBackend, 'connect'):
            instance = HomeAssistantBackend(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, True,
                                            backend_const.EMPTY_STRING)
        instance._entities = {"light": {"light.a": {
            backend_const.STATE: "off", backend_const.ATTRIBUTES: {"old": 1},
            backend_const.ACTIONS: set(), backend_const.SUBSCRIPTION_ID: -1}}}
        instance._websocket = Mock()
        instance._websocket.create_message.return_value = {backend_const.ID: 1}
        return instance

    @patch("HomeAssistantPlugin.backend.home_assistant_backend.GLib")
    def test_refresh_entity_updates_cache(self, glib_mock):
        instance = self._create()
        callback = Mock()

        instance._refresh_entity("light.a", callback)
        on_response = instance._websocket.send_request.call_args[0][1]
        on_response(True, [{backend_const.ENTITY_ID: "light.a", backend_const.STATE: "on",
                            backend_const.ATTRIBUTES: {"new": 2}}], "")

        entity = instance._entities["light"]["light.a"]
        self.assertEqual("on", entity[backend_const.STATE])
        self.assertEqual({"new": 2}, entity[backend_const.ATTRIBUTES])
        glib_mock.idle_add.assert_called_once()

    @patch("HomeAssistantPlugin.backend.home_assistant_backend.GLib")
    def test_refresh_entity_missing_clears_cache(self, glib_mock):
        instance = self._create()
        callback = Mock()

        instance._refresh_entity("light.a", callback)
        instance._websocket.send_request.call_args[0][1](True, [], "")

        entity = instance._entities["light"]["light.a"]
        self.assertEqual(backend_const.NA, entity[backend_const.STATE])
        self.assertEqual({}, entity[backend_const.ATTRIBUTES])
        glib_mock.idle_add.assert_called_once()

    @patch("HomeAssistantPlugin.backend.home_assistant_backend.GLib")
    def test_refresh_entity_failure_keeps_cache(self, glib_mock):
        instance = self._create()

        instance._refresh_entity("light.a", Mock())
        instance._websocket.send_request.call_args[0][1](False, "", "error")

        entity = instance._entities["light"]["light.a"]
        self.assertEqual("off", entity[backend_const.STATE])
        self.assertEqual({"old": 1}, entity[backend_const.ATTRIBUTES])
        glib_mock.idle_add.assert_not_called()

    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_add_tracked_entity_use_cache_false_requests_refresh(self, _):
        instance = self._create()
        callback = Mock()

        instance.add_tracked_entity("light.a", callback, use_cache=False)

        self.assertIn(callback, instance._entities["light"]["light.a"][backend_const.ACTIONS])
        instance._websocket.send_request.assert_called_once()

    @patch.object(HomeAssistantBackend, 'is_connected', return_value=True)
    def test_add_tracked_entity_default_uses_cache(self, _):
        instance = self._create()

        instance.add_tracked_entity("light.a", Mock())

        instance._websocket.send_request.assert_not_called()
