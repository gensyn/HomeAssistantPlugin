import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.absolute()))

from HomeAssistantPlugin.backend import backend_const
from HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend


class TestBackendAsyncReload(unittest.TestCase):
    def setUp(self):
        with patch.object(HomeAssistantBackend, "connect"):
            self.backend = HomeAssistantBackend("", "", True, True, "")
        self.websocket = Mock()
        self.websocket.connected = True
        self.websocket.send_request.return_value = True
        self.backend._websocket = self.websocket

    @patch("HomeAssistantPlugin.backend.home_assistant_backend.GLib.idle_add")
    def test_entities_keep_subscriptions_and_notify_on_main_loop(self, idle_add):
        tracked = Mock()
        self.backend._entities = {"light": {"light.a": {
            backend_const.ACTIONS: {tracked}, backend_const.SUBSCRIPTION_ID: 42,
        }}}
        complete = Mock()
        self.backend.reload_entities(complete)
        self.websocket.send_and_recv.assert_not_called()
        request, response = self.websocket.send_request.call_args.args
        self.assertEqual(backend_const.GET_STATES, request)
        response(True, [{backend_const.ENTITY_ID: "light.a", backend_const.STATE: "on"}], "")
        complete.assert_not_called()
        entity = self.backend._entities["light"]["light.a"]
        self.assertEqual("on", entity[backend_const.STATE])
        self.assertEqual({tracked}, entity[backend_const.ACTIONS])
        self.assertEqual(42, entity[backend_const.SUBSCRIPTION_ID])
        entity[backend_const.STATE] = "off"
        self.assertFalse(idle_add.call_args.args[0]())
        self.assertEqual("off", entity[backend_const.STATE])
        complete.assert_called_once_with()

    @patch("HomeAssistantPlugin.backend.home_assistant_backend.GLib.idle_add")
    def test_out_of_order_responses_keep_newest_result_and_notify_both(self, idle_add):
        first, second = Mock(), Mock()
        self.backend.reload_actions(first)
        response1 = self.websocket.send_request.call_args.args[1]
        self.backend.reload_actions(second)
        response2 = self.websocket.send_request.call_args.args[1]
        response2(True, {"new": {}}, "")
        response1(True, {"old": {}}, "")
        for call in idle_add.call_args_list:
            call.args[0]()
        self.assertEqual({"new": {}}, self.backend._actions)
        first.assert_called_once_with()
        second.assert_called_once_with()

    @patch("HomeAssistantPlugin.backend.home_assistant_backend.log.error")
    @patch("HomeAssistantPlugin.backend.home_assistant_backend.GLib.idle_add")
    def test_failure_retains_cache(self, idle_add, log_error):
        self.backend._actions = {"light": {}}
        self.backend.reload_actions(Mock())
        self.websocket.send_request.call_args.args[1](False, "", "error")
        self.assertEqual({"light": {}}, self.backend._actions)
        log_error.assert_called_once_with(backend_const.ERROR_SERVICES.format("error"))
        idle_add.assert_not_called()

    @patch("HomeAssistantPlugin.backend.home_assistant_backend.GLib.idle_add")
    def test_old_connection_response_is_ignored(self, idle_add):
        complete = Mock()
        self.backend.reload_entities(complete)
        self.websocket.send_request.call_args.args[1](True, [], "")
        self.backend._websocket = Mock(connected=True)
        idle_add.call_args.args[0]()
        complete.assert_not_called()

    @patch("HomeAssistantPlugin.backend.home_assistant_backend.GLib.idle_add")
    def test_empty_results_do_not_cause_synchronous_reload(self, idle_add):
        self.backend.reload_entities()
        self.websocket.send_request.call_args.args[1](True, [], "")
        self.backend.reload_actions()
        self.websocket.send_request.call_args.args[1](True, {}, "")
        for call in idle_add.call_args_list:
            call.args[0]()
        self.assertEqual([], self.backend.get_entities("light", load_if_empty=False))
        self.assertEqual({}, self.backend.get_actions("light", load_if_empty=False))
        self.websocket.send_and_recv.assert_not_called()

    def test_cache_only_getters_never_request_on_empty_cache(self):
        with patch.object(self.backend, "_load_entities") as entities, \
                patch.object(self.backend, "_load_actions") as actions:
            self.assertEqual([], self.backend.get_domains_for_entities(load_if_empty=False))
            self.assertEqual([], self.backend.get_domains_for_actions(load_if_empty=False))
            self.assertEqual([], self.backend.get_entities("light", load_if_empty=False))
            self.assertEqual({}, self.backend.get_actions("light", load_if_empty=False))
            entities.assert_not_called()
            actions.assert_not_called()
