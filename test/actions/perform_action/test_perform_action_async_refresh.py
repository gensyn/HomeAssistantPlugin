import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "stream_controller_mock"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.absolute()))

from HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction
from HomeAssistantPlugin.backend import backend_const
from HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend


class TestPerformActionAsyncRefresh(unittest.TestCase):
    @patch("HomeAssistantPlugin.backend.home_assistant_backend.GLib.idle_add")
    @patch("HomeAssistantPlugin.actions.perform_action.perform_action.parameters_helper.load_parameters")
    @patch("HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__")
    def test_open_returns_before_responses_and_updates_widgets(self, _, load_parameters, idle_add):
        with patch.object(HomeAssistantBackend, "connect"):
            backend = HomeAssistantBackend("", "", True, True, "")
        backend._websocket = Mock(connected=True)
        backend._websocket.send_request.return_value = True
        action = PerformAction()
        action.initialized = True
        action.is_removed = False
        action.plugin_base = Mock(backend=backend)
        action.settings = Mock()
        action.settings.get_domain.return_value = "light"
        action.settings.get_entity.return_value = "light.a"
        action.settings.get_action.return_value = "turn_on"
        action.domain_combo = Mock()
        action.entity_combo = Mock()
        action.action_combo = Mock()
        action.parameters_expander = Mock()
        action._last_loaded_domains = None
        action._last_loaded_entities = None
        action._reload = Mock()

        rows = action.get_config_rows()
        self.assertEqual([action.domain_combo.widget, action.action_combo.widget,
                          action.entity_combo.widget, action.parameters_expander.widget], rows)
        self.assertEqual(2, backend._websocket.send_request.call_count)
        backend._websocket.send_and_recv.assert_not_called()
        action.action_combo.populate.assert_not_called()
        load_parameters.assert_not_called()

        requests = dict(call.args for call in backend._websocket.send_request.call_args_list)
        requests[backend_const.GET_SERVICES](True, {"light": {"turn_on": {}}}, "")
        requests[backend_const.GET_STATES](True, [{backend_const.ENTITY_ID: "light.a"}], "")
        action.action_combo.populate.assert_not_called()
        load_parameters.assert_not_called()
        for call in idle_add.call_args_list:
            call.args[0]()
        action.domain_combo.populate.assert_called_once_with(["light"], "light", trigger_callback=False)
        action.entity_combo.populate.assert_called_once_with(["light.a"], "light.a", trigger_callback=False)
        action.action_combo.populate.assert_called_with(
            ["turn_on"], "turn_on", update_settings=False, trigger_callback=False)
        self.assertEqual(2, load_parameters.call_count)
        self.assertEqual(2, action._reload.call_count)

    @patch("HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__")
    def test_removed_action_ignores_completed_refreshes(self, _):
        action = PerformAction()
        action._refresh_cancelled = True
        action.plugin_base = Mock()
        action._load_domains = Mock()
        action._load_entities = Mock()
        action._load_actions = Mock()
        action._reload = Mock()
        action._on_actions_refreshed()
        action._on_entities_refreshed()
        action._load_domains.assert_not_called()
        action._load_entities.assert_not_called()
        action._load_actions.assert_not_called()
        action._reload.assert_not_called()

    @patch("HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__")
    def test_completed_refresh_uses_current_selection(self, _):
        action = PerformAction()
        action.initialized = True
        action.is_removed = False
        action.plugin_base = Mock()
        action.settings = Mock()
        action.settings.get_domain.return_value = "switch"
        action.settings.get_action.return_value = "toggle"
        action.plugin_base.backend.get_actions.return_value = {"toggle": {}}
        action.action_combo = Mock()
        action._load_domains = Mock()
        action._reload = Mock()
        with patch("HomeAssistantPlugin.actions.perform_action.perform_action.parameters_helper.load_parameters"):
            action._on_actions_refreshed()
        action.plugin_base.backend.get_actions.assert_called_once_with("switch", load_if_empty=False)
        action.action_combo.populate.assert_called_once_with(
            ["toggle"], "toggle", update_settings=False, trigger_callback=False)
