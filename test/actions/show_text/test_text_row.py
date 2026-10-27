import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.show_text import text_const
from HomeAssistantPlugin.actions.show_text.text_row import TextRow
from HomeAssistantPlugin.actions.show_text.text_customization import TextCustomization

class TestTextRow(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.show_text.text_row.CustomizationRow.__init__', autospec=True)
    @patch('HomeAssistantPlugin.actions.show_text.text_row.text_helper')
    @patch('HomeAssistantPlugin.actions.show_text.text_row.customization_helper')
    @patch.object(TextRow, '_init_title')
    @patch.object(TextRow, 'set_title')
    def test_init(self, set_title_mock, init_title_mock, customization_helper_mock, text_helper_mock, super_init_mock):
        lm = {
            text_const.LABEL_POSITION: "Position",
            text_const.LABEL_ATTRIBUTE: "Attribute",
            text_const.LABEL_ROUND: "Round",
            text_const.LABEL_ROUND_PRECISION: "Round Precision",
            text_const.LABEL_TEXT_SIZE: "Text Size",
            text_const.LABEL_TEXT_COLOR: "Text Color",
            text_const.LABEL_OUTLINE_SIZE: "Outline Size",
            text_const.LABEL_OUTLINE_COLOR: "Outline Color",
            text_const.LABEL_SHOW_UNIT_SHORT: "Show Unit Short",
            text_const.LABEL_UNIT_LINE_BREAK_SHORT: "Line Break Short",
        }

        def super_init(instance, lm, *args, **kwargs):
            instance.lm = lm

        super_init_mock.side_effect = super_init
        init_title_mock.return_value = "Title"
        customization_helper_mock.convert_color_list_to_hex.side_effect = ["#FF0000", "#0000FF"]

        customization_mock = Mock()
        customization_mock.get_position.return_value = "position_name"
        customization_mock.get_text_attribute.return_value = "text_name"
        customization_mock.get_custom_text.return_value = "custom text"
        customization_mock.get_round.return_value = 2
        customization_mock.get_round_precision.return_value = 1
        customization_mock.get_text_size.return_value = 150
        customization_mock.get_text_color.return_value = [255, 0, 0]
        customization_mock.get_outline_size.return_value = 3
        customization_mock.get_outline_color.return_value = [0, 0, 255]
        customization_mock.get_show_unit.return_value = True
        customization_mock.get_line_break.return_value = False

        customization_count = 5
        index = 3
        attributes = ['attr1', 'attr2']
        state = {'state_key': 'state_value'}
        settings = "settings"

        instance = TextRow(lm, customization_mock, customization_count, index, attributes, state, settings)

        super_init_mock.assert_called_once_with(instance, lm, customization_count, index, attributes, state, settings, None) # with instance because of autospec
        init_title_mock.assert_called_once()
        self.assertEqual(customization_mock, init_title_mock.call_args.args[0])
        condition = Mock()
        init_title_mock.call_args.args[1](condition)
        text_helper_mock.get_condition_value.assert_called_once_with(state, settings, condition, None)
        set_title_mock.assert_called_once_with(
            "Title\nPosition position_name\nAttribute text_name = \"custom text\"\nRound 2\nRound Precision 1\nText Size 150\nText Color #FF0000\nOutline Size 3\nOutline Color #0000FF\nShow Unit Short True\nLine Break Short False"
        )