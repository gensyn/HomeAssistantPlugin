import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.perform_action import perform_const
from HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction


class TestPerformActionSetEnabledDisabled(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    def test_set_enabled_disabled_not_initialized(self, _):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value="light")

        instance = PerformAction()
        instance.settings = settings_mock
        instance.initialized = False
        instance.set_enabled_disabled()

        settings_mock.get_domain.assert_not_called()

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    def test_set_enabled_disabled_domain_not_set(self, _):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value=None)

        action_combo_mock = Mock()
        action_combo_mock.widget = Mock()
        action_combo_mock.widget.set_sensitive = Mock()
        action_combo_mock.widget.set_subtitle = Mock()

        parameters_expander_mock = Mock()
        parameters_expander_mock.widget = Mock()
        parameters_expander_mock.widget.set_sensitive = Mock()
        parameters_expander_mock.widget.set_subtitle = Mock()

        locale_manager = {
            perform_const.LABEL_SERVICE_NO_DOMAIN: "No domain set"
        }

        instance = PerformAction()
        instance.settings = settings_mock
        instance.initialized = True
        instance.lm = locale_manager
        instance.action_combo = action_combo_mock
        instance.parameters_expander = parameters_expander_mock
        instance.set_enabled_disabled()

        settings_mock.get_domain.assert_called_once()
        action_combo_mock.widget.set_sensitive.assert_called_once_with(False)
        action_combo_mock.widget.set_subtitle.assert_called_once_with(locale_manager[perform_const.LABEL_SERVICE_NO_DOMAIN])
        parameters_expander_mock.widget.set_sensitive.assert_called_once_with(False)
        parameters_expander_mock.widget.set_subtitle.assert_called_once_with(
            locale_manager[perform_const.LABEL_SERVICE_NO_DOMAIN])

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    def test_set_enabled_disabled_no_actions(self, _):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value="light")

        action_combo_mock = Mock()
        action_combo_mock.widget = Mock()
        action_combo_mock.widget.set_sensitive = Mock()
        action_combo_mock.widget.set_subtitle = Mock()
        action_combo_mock.get_item_amount = Mock(return_value=0)

        parameters_expander_mock = Mock()
        parameters_expander_mock.widget = Mock()
        parameters_expander_mock.widget.set_sensitive = Mock()
        parameters_expander_mock.widget.set_subtitle = Mock()

        locale_manager = {
            perform_const.LABEL_SERVICE_NO_ACTIONS: "No actions available"
        }

        instance = PerformAction()
        instance.settings = settings_mock
        instance.initialized = True
        instance.lm = locale_manager
        instance.action_combo = action_combo_mock
        instance.parameters_expander = parameters_expander_mock
        instance.set_enabled_disabled()

        settings_mock.get_domain.assert_called_once()
        action_combo_mock.widget.set_sensitive.assert_called_once_with(False)
        action_combo_mock.widget.set_subtitle.assert_called_once_with(locale_manager[perform_const.LABEL_SERVICE_NO_ACTIONS])
        parameters_expander_mock.widget.set_sensitive.assert_called_once_with(False)
        parameters_expander_mock.widget.set_subtitle.assert_called_once_with(
            locale_manager[perform_const.LABEL_SERVICE_NO_ACTIONS])

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    def test_set_enabled_disabled_no_parameters_no_target_one_entity(self, _):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value="light")
        settings_mock.get_action = Mock(return_value="turn_on")

        action_combo_mock = Mock()
        action_combo_mock.widget = Mock()
        action_combo_mock.widget.set_sensitive = Mock()
        action_combo_mock.widget.set_subtitle = Mock()
        action_combo_mock.get_item_amount = Mock(return_value=3)

        parameters_expander_mock = Mock()
        parameters_expander_mock.widget = Mock()
        parameters_expander_mock.widget.set_sensitive = Mock()
        parameters_expander_mock.widget.set_subtitle = Mock()
        parameters_expander_mock.set_expanded = Mock()
        parameters_expander_mock.widget.get_rows = Mock(return_value=[])

        entity_combo_mock = Mock()
        entity_combo_mock.widget = Mock()
        entity_combo_mock.widget.set_sensitive = Mock()
        entity_combo_mock.get_item_amount = Mock(return_value=1)

        domain_combo_mock = Mock()
        domain_combo_mock.get_selected_item = Mock(return_value="light")

        locale_manager = {
            perform_const.LABEL_SERVICE_NO_PARAMETERS: "No parameters available"
        }

        plugin_base_mock = Mock()
        plugin_base_mock.backend = Mock()
        plugin_base_mock.backend.get_actions = Mock(return_value={"turn_on": {}})

        instance = PerformAction()
        instance.settings = settings_mock
        instance.initialized = True
        instance.lm = locale_manager
        instance.action_combo = action_combo_mock
        instance.parameters_expander = parameters_expander_mock
        instance.entity_combo = entity_combo_mock
        instance.domain_combo = domain_combo_mock
        instance.plugin_base = plugin_base_mock
        instance.set_enabled_disabled()

        settings_mock.get_domain.assert_called_once()
        action_combo_mock.widget.set_sensitive.assert_called_once_with(True)
        action_combo_mock.widget.set_subtitle.assert_called_once_with(perform_const.EMPTY_STRING)
        parameters_expander_mock.widget.set_sensitive.assert_called_once_with(False)
        parameters_expander_mock.set_expanded.assert_called_once_with(False)
        parameters_expander_mock.widget.set_subtitle.assert_called_once_with(
            locale_manager[perform_const.LABEL_SERVICE_NO_PARAMETERS])
        settings_mock.get_action.assert_called_once()
        domain_combo_mock.get_selected_item.assert_called_once()
        plugin_base_mock.backend.get_actions.assert_called_once_with(domain_combo_mock.get_selected_item.return_value)
        entity_combo_mock.widget.set_sensitive.assert_called_once_with(False)

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    def test_set_enabled_disabled_parameters_no_target_two_entities(self, _):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value="light")
        settings_mock.get_action = Mock(return_value="turn_on")

        action_combo_mock = Mock()
        action_combo_mock.widget = Mock()
        action_combo_mock.widget.set_sensitive = Mock()
        action_combo_mock.widget.set_subtitle = Mock()
        action_combo_mock.get_item_amount = Mock(return_value=3)

        parameters_expander_mock = Mock()
        parameters_expander_mock.widget = Mock()
        parameters_expander_mock.widget.set_sensitive = Mock()
        parameters_expander_mock.widget.set_subtitle = Mock()
        parameters_expander_mock.set_expanded = Mock()
        parameters_expander_mock.widget.get_rows = Mock(return_value=["row1", "row2"])

        entity_combo_mock = Mock()
        entity_combo_mock.widget = Mock()
        entity_combo_mock.widget.set_sensitive = Mock()
        entity_combo_mock.get_item_amount = Mock(return_value=2)

        domain_combo_mock = Mock()
        domain_combo_mock.get_selected_item = Mock(return_value="light")

        plugin_base_mock = Mock()
        plugin_base_mock.backend = Mock()
        plugin_base_mock.backend.get_actions = Mock(return_value={"turn_on": {}})

        instance = PerformAction()
        instance.settings = settings_mock
        instance.initialized = True
        instance.action_combo = action_combo_mock
        instance.parameters_expander = parameters_expander_mock
        instance.entity_combo = entity_combo_mock
        instance.domain_combo = domain_combo_mock
        instance.plugin_base = plugin_base_mock
        instance.set_enabled_disabled()

        settings_mock.get_domain.assert_called_once()
        action_combo_mock.widget.set_sensitive.assert_called_once_with(True)
        action_combo_mock.widget.set_subtitle.assert_called_once_with(perform_const.EMPTY_STRING)
        parameters_expander_mock.widget.set_sensitive.assert_called_once_with(True)
        parameters_expander_mock.set_expanded.assert_called_once_with(True)
        parameters_expander_mock.widget.set_subtitle.assert_called_once_with(perform_const.EMPTY_STRING)
        settings_mock.get_action.assert_called_once()
        domain_combo_mock.get_selected_item.assert_called_once()
        plugin_base_mock.backend.get_actions.assert_called_once_with(domain_combo_mock.get_selected_item.return_value)
        entity_combo_mock.widget.set_sensitive.assert_called_once_with(False)

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    def test_set_enabled_disabled_parameters_target_no_entity(self, _):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value="light")
        settings_mock.get_action = Mock(return_value="turn_on")

        action_combo_mock = Mock()
        action_combo_mock.widget = Mock()
        action_combo_mock.widget.set_sensitive = Mock()
        action_combo_mock.widget.set_subtitle = Mock()
        action_combo_mock.get_item_amount = Mock(return_value=3)

        parameters_expander_mock = Mock()
        parameters_expander_mock.widget = Mock()
        parameters_expander_mock.widget.set_sensitive = Mock()
        parameters_expander_mock.widget.set_subtitle = Mock()
        parameters_expander_mock.set_expanded = Mock()
        parameters_expander_mock.widget.get_rows = Mock(return_value=["row1", "row2"])

        entity_combo_mock = Mock()
        entity_combo_mock.widget = Mock()
        entity_combo_mock.widget.set_sensitive = Mock()
        entity_combo_mock.get_item_amount = Mock(return_value=1)

        domain_combo_mock = Mock()
        domain_combo_mock.get_selected_item = Mock(return_value="light")

        plugin_base_mock = Mock()
        plugin_base_mock.backend = Mock()
        plugin_base_mock.backend.get_actions = Mock(return_value={"turn_on": {"target": "yes"}})

        instance = PerformAction()
        instance.settings = settings_mock
        instance.initialized = True
        instance.action_combo = action_combo_mock
        instance.parameters_expander = parameters_expander_mock
        instance.entity_combo = entity_combo_mock
        instance.domain_combo = domain_combo_mock
        instance.plugin_base = plugin_base_mock
        instance.set_enabled_disabled()

        settings_mock.get_domain.assert_called_once()
        action_combo_mock.widget.set_sensitive.assert_called_once_with(True)
        action_combo_mock.widget.set_subtitle.assert_called_once_with(perform_const.EMPTY_STRING)
        parameters_expander_mock.widget.set_sensitive.assert_called_once_with(True)
        parameters_expander_mock.set_expanded.assert_called_once_with(True)
        parameters_expander_mock.widget.set_subtitle.assert_called_once_with(perform_const.EMPTY_STRING)
        settings_mock.get_action.assert_called_once()
        domain_combo_mock.get_selected_item.assert_called_once()
        plugin_base_mock.backend.get_actions.assert_called_once_with(domain_combo_mock.get_selected_item.return_value)
        entity_combo_mock.widget.set_sensitive.assert_called_once_with(True)

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    def test_set_enabled_disabled_parameters_target_two_entities(self, _):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value="light")
        settings_mock.get_action = Mock(return_value="turn_on")

        action_combo_mock = Mock()
        action_combo_mock.widget = Mock()
        action_combo_mock.widget.set_sensitive = Mock()
        action_combo_mock.widget.set_subtitle = Mock()
        action_combo_mock.get_item_amount = Mock(return_value=3)

        parameters_expander_mock = Mock()
        parameters_expander_mock.widget = Mock()
        parameters_expander_mock.widget.set_sensitive = Mock()
        parameters_expander_mock.widget.set_subtitle = Mock()
        parameters_expander_mock.set_expanded = Mock()
        parameters_expander_mock.widget.get_rows = Mock(return_value=["row1", "row2"])

        entity_combo_mock = Mock()
        entity_combo_mock.widget = Mock()
        entity_combo_mock.widget.set_sensitive = Mock()
        entity_combo_mock.get_item_amount = Mock(return_value=2)

        domain_combo_mock = Mock()
        domain_combo_mock.get_selected_item = Mock(return_value="light")

        plugin_base_mock = Mock()
        plugin_base_mock.backend = Mock()
        plugin_base_mock.backend.get_actions = Mock(return_value={"turn_on": {"target": "yes"}})

        instance = PerformAction()
        instance.settings = settings_mock
        instance.initialized = True
        instance.action_combo = action_combo_mock
        instance.parameters_expander = parameters_expander_mock
        instance.entity_combo = entity_combo_mock
        instance.domain_combo = domain_combo_mock
        instance.plugin_base = plugin_base_mock
        instance.set_enabled_disabled()

        settings_mock.get_domain.assert_called_once()
        action_combo_mock.widget.set_sensitive.assert_called_once_with(True)
        action_combo_mock.widget.set_subtitle.assert_called_once_with(perform_const.EMPTY_STRING)
        parameters_expander_mock.widget.set_sensitive.assert_called_once_with(True)
        parameters_expander_mock.set_expanded.assert_called_once_with(True)
        parameters_expander_mock.widget.set_subtitle.assert_called_once_with(perform_const.EMPTY_STRING)
        settings_mock.get_action.assert_called_once()
        domain_combo_mock.get_selected_item.assert_called_once()
        plugin_base_mock.backend.get_actions.assert_called_once_with(domain_combo_mock.get_selected_item.return_value)
        entity_combo_mock.widget.set_sensitive.assert_called_once_with(True)

