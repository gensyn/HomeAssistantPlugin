import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.perform_action import perform_const
from HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction


class TestPerformActionCreateUiElements(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.create_ui_elements')
    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.ComboRow')
    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.ExpanderRow')
    def test_create_ui_elements_success(self, expander_row_mock, combo_row_mock, create_ui_elements_mock, _):
        instance = PerformAction()
        instance.create_ui_elements()

        create_ui_elements_mock.assert_called_once()
        combo_row_mock.assert_called_once_with(
            instance,
            perform_const.SETTING_ACTION_ACTION,
            perform_const.EMPTY_STRING,
            [],
            perform_const.LABEL_SERVICE_SERVICE,
            enable_search=True,
            on_change=instance._on_change_action,
            can_reset=False,
            complex_var_name=True
        )
        expander_row_mock.assert_called_once_with(
            instance,
            perform_const.EMPTY_STRING,
            False,
            title=perform_const.LABEL_SERVICE_PARAMETERS,
            can_reset=False,
            auto_add=False
        )
        self.assertEqual(combo_row_mock.return_value, instance.action_combo)
        self.assertEqual(expander_row_mock.return_value, instance.parameters_expander)

