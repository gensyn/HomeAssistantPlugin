import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction


class TestPerformActionOnChangeAction(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.parameters.parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_action_not_initialized(self, reload_mock, load_parameters_mock, _):
        settings_mock = Mock()
        settings_mock.clear_parameters = Mock()

        instance = PerformAction()
        instance.settings = settings_mock
        instance.initialized = False
        instance._on_change_action(None, None, None)

        settings_mock.clear_parameters.assert_not_called()
        load_parameters_mock.assert_not_called()
        reload_mock.assert_not_called()

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.parameters.parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_action_success(self, reload_mock, load_parameters_mock, _):
        settings_mock = Mock()
        settings_mock.clear_parameters = Mock()

        instance = PerformAction()
        instance.settings = settings_mock
        instance.initialized = True
        instance._on_change_action(None, "turn_on", "turn_off")

        settings_mock.clear_parameters.assert_called_once()
        load_parameters_mock.assert_called_once_with(instance)
        reload_mock.assert_called_once()

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.parameters.parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_action_same_value_no_op(self, reload_mock, load_parameters_mock, _):
        settings_mock = Mock()
        settings_mock.clear_parameters = Mock()

        instance = PerformAction()
        instance.settings = settings_mock
        instance.initialized = True
        instance._on_change_action(None, "turn_on", "turn_on")

        settings_mock.clear_parameters.assert_not_called()
        load_parameters_mock.assert_not_called()
        reload_mock.assert_not_called()

