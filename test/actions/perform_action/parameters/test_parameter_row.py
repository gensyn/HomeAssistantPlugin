import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, call

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin import const as base_const
from HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row import ParameterRow


class TestParameterEntryRow(unittest.TestCase):

    def test_init_field_not_in_parameters_not_required(self):
        required = False
        parameters = {"test_field": "test_value"}
        field_name = "other_field"
        instance = create_instance(required, parameters, field_name)

        instance.check.assert_called_once()
        instance.check.set_active.assert_not_called()
        instance.check.set_sensitive.assert_not_called()
        instance.check.connect.assert_called_once_with(base_const.CONNECT_TOGGLED, instance._on_change)

    def test_init_field_in_parameters_not_required(self):
        required = False
        parameters = {"test_field": "test_value"}
        field_name = "test_field"
        instance = create_instance(required, parameters, field_name)

        instance.check.assert_called_once()
        instance.check.set_active.assert_called_once_with(True)
        instance.check.set_sensitive.assert_not_called()
        instance.check.connect.assert_called_once_with(base_const.CONNECT_TOGGLED, instance._on_change)

    def test_init_field_not_in_parameters_required(self):
        required = True
        parameters = {"test_field": "test_value"}
        field_name = "other_field"
        instance = create_instance(required, parameters, field_name)

        instance.check.assert_called_once()
        instance.check.set_active.assert_called_once_with(True)
        instance.check.set_sensitive.assert_called_once_with(False)
        instance.check.connect.assert_called_once_with(base_const.CONNECT_TOGGLED, instance._on_change)

    def test_init_field_in_parameters_required(self):
        required = True
        parameters = {"test_field": "test_value"}
        field_name = "test_field"
        instance = create_instance(required, parameters, field_name)

        instance.check.assert_called_once()
        self.assertEqual(2, instance.check.set_active.call_count)
        instance.check.set_active.assert_has_calls([call(True), call(True)])
        instance.check.set_sensitive.assert_called_once_with(False)
        instance.check.connect.assert_called_once_with(base_const.CONNECT_TOGGLED, instance._on_change)

    def test_get_parameter_value(self):
        required = False
        instance = create_instance(required)

        self.assertRaises(NotImplementedError, instance.get_parameter_value)

    def test_set_value(self):
        required = False
        instance = create_instance(required)

        self.assertRaises(NotImplementedError, instance.set_value, "test_value")

    @patch(
        'HomeAssistantPlugin.actions.perform_action.parameters.parameter_row.ParameterRow.get_parameter_value')
    def test_on_change_active(self, get_parameter_value_mock):
        get_parameter_value_mock.return_value = "test_value"
        required = False
        instance = create_instance(required)
        instance.check.get_active = Mock(return_value=True)
        instance._on_change()

        instance.action.settings.set_parameter.assert_called_once_with(instance.field_name, "test_value")

    @patch(
        'HomeAssistantPlugin.actions.perform_action.parameters.parameter_row.ParameterRow.get_parameter_value')
    def test_on_change_not_active(self, get_parameter_value_mock):
        get_parameter_value_mock.return_value = "test_value"
        required = False
        instance = create_instance(required)
        instance.check.get_active = Mock(return_value=False)
        instance._on_change()

        instance.action.settings.remove_parameter.assert_called_once_with(instance.field_name)


def create_instance(required: bool, parameters=None, field_name: str = "test_field") -> ParameterRow:
    if parameters is None:
        parameters = {}
    action_core_mock = Mock()
    action_core_mock.settings = Mock()
    action_core_mock.settings.get_parameters = Mock(return_value=parameters)
    action_core_mock.settings.set_parameter = Mock()
    action_core_mock.settings.remove_parameter = Mock()
    field_name = field_name

    with patch('HomeAssistantPlugin.actions.perform_action.parameters.parameter_row.CheckButton') as check_button_mock:
        check_button_mock.return_value = check_button_mock
        check_button_mock.set_active = Mock()
        check_button_mock.set_sensitive = Mock()
        check_button_mock.connect = Mock()
        return ParameterRow(action_core_mock, field_name, required)
