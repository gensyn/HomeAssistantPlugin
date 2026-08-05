import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock, call, ANY

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.show_text import text_const
from HomeAssistantPlugin.actions.show_text.text_window import TextWindow
from HomeAssistantPlugin.actions.show_text.text_customization import TextCustomization


class TestTextWindow(unittest.TestCase):

    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.CustomizationWindow.__init__',
        autospec=True)
    @patch.object(TextWindow, "set_title")
    @patch.object(TextWindow, "_after_init")
    @patch.object(TextWindow, "_create_check_button")
    @patch.object(TextWindow, "_create_drop_down")
    @patch.object(TextWindow, "_create_entry")
    @patch.object(TextWindow, "_create_switch")
    @patch.object(TextWindow, "_create_color_button")
    @patch.object(TextWindow, "_create_scale")
    @patch.object(TextWindow, "_create_scale_entry")
    @patch.object(TextWindow, "_create_label")
    def test_init(self, create_label_mock, create_scale_entry_mock, create_scale_mock, create_color_button_mock,
                  create_switch_mock, create_entry_mock, create_drop_down_mock, create_check_button_mock,
                  after_init_mock, set_title_mock,
                  super_init_mock):
        lm = Mock()
        lm.get.return_value = "Test Title"
        attributes = ["attribute1", "attribute2"]
        attributes_expected = ["text_length", "attribute1", "attribute2"]
        callback = Mock()
        current = Mock()
        index = 1

        def super_init(instance, lm, *args, **kwargs):
            instance.lm = lm
            instance.grid_fields = Mock()
            instance.attributes = attributes

        super_init_mock.side_effect = super_init

        instance = TextWindow(lm, attributes, callback, current, index)

        super_init_mock.assert_called_once_with(instance, lm, attributes_expected, callback, current,
                                                index)  # with instance because of autospec
        set_title_mock.assert_called_once_with("Test Title")
        self.assertEqual(10, create_check_button_mock.call_count)
        self.assertEqual(10, create_label_mock.call_count)
        self.assertEqual(2, create_drop_down_mock.call_count)
        self.assertEqual(1, create_entry_mock.call_count)
        self.assertEqual(3, create_switch_mock.call_count)
        self.assertEqual(3, create_scale_mock.call_count)
        self.assertEqual(3, create_scale_entry_mock.call_count)
        self.assertEqual(2, create_color_button_mock.call_count)
        self.assertEqual(34, instance.grid_fields.attach.call_count)
        after_init_mock.assert_called_once()

    def test_on_change_attribute_custom_text_not_visible(self):
        instance = TextWindow.__new__(TextWindow)
        instance.attribute = Mock()
        instance.attribute.get_selected_item.get_string.return_value = text_const.STATE
        instance.custom_text = Mock()

        instance._on_change_attribute()

        instance.custom_text.set_visible.assert_called_once_with(False)

    def test_on_change_attribute_custom_text_visible(self):
        instance = TextWindow.__new__(TextWindow)
        instance.attribute = Mock()
        instance.attribute.get_selected_item.return_value = Mock()
        instance.attribute.get_selected_item.return_value.get_string.return_value = text_const.CUSTOM_CUSTOM_TEXT
        instance.custom_text = Mock()

        instance._on_change_attribute()

        instance.custom_text.set_visible.assert_called_once_with(True)

    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.CustomizationWindow.set_default_values')
    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.customization_helper')
    def testset_default_values(self, customization_helper_mock, super_set_default_values_mock):
        instance = TextWindow.__new__(TextWindow)

        position1 = Mock()
        position1.get_string.return_value = "a"
        position2 = Mock()
        position2.get_string.return_value = text_const.DEFAULT_POSITION
        position3 = Mock()
        position3.get_string.return_value = "c"
        instance.position = Mock()
        instance.position.get_model.return_value = [position1, position2, position3]

        attribute1 = Mock()
        attribute1.get_string.return_value = "1"
        attribute2 = Mock()
        attribute2.get_string.return_value = "2"
        attribute3 = Mock()
        attribute3.get_string.return_value = text_const.DEFAULT_ATTRIBUTE
        instance.attribute = Mock()
        instance.attribute.get_model.return_value = [attribute1, attribute2, attribute3]

        instance.custom_text = Mock()
        instance.round = Mock()
        instance.precision = Mock()
        instance.precision_entry = Mock()
        instance.text_size = Mock()
        instance.text_size_entry = Mock()
        instance.text_color = Mock()
        instance.outline_size = Mock()
        instance.outline_size_entry = Mock()
        instance.outline_color = Mock()
        instance.show_unit = Mock()
        instance.show_line_break = Mock()

        customization_helper_mock.convert_color_list_to_rgba.side_effect = ["color1", "color2"]

        instance.set_default_values()

        super_set_default_values_mock.assert_called_once_with()
        instance.position.set_selected.assert_called_once_with(1)
        instance.attribute.set_selected.assert_called_once_with(2)
        instance.custom_text.set_text.assert_called_once_with(text_const.DEFAULT_CUSTOM_TEXT)
        instance.custom_text.set_visible.assert_called_once_with(False)
        instance.round.set_active.assert_called_once_with(text_const.DEFAULT_ROUND)
        instance.precision.set_value.assert_called_once_with(text_const.DEFAULT_ROUND_PRECISION)
        instance.precision_entry.set_text.assert_called_once_with(str(text_const.DEFAULT_ROUND_PRECISION))
        instance.text_size.set_value.assert_called_once_with(text_const.DEFAULT_TEXT_SIZE)
        instance.text_size_entry.set_text.assert_called_once_with(str(text_const.DEFAULT_TEXT_SIZE))
        instance.text_color.set_rgba.assert_called_once_with("color1")
        instance.outline_size.set_value.assert_called_once_with(text_const.DEFAULT_OUTLINE_SIZE)
        instance.outline_size_entry.set_text.assert_called_once_with(str(text_const.DEFAULT_OUTLINE_SIZE))
        instance.outline_color.set_rgba.assert_called_once_with("color2")
        instance.show_unit.set_active.assert_called_once_with(text_const.DEFAULT_SHOW_UNIT)
        instance.show_line_break.set_active.assert_called_once_with(text_const.DEFAULT_UNIT_LINE_BREAK)

    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.CustomizationWindow.set_current_values')
    def test_set_current_values_no_current(self, super_current_values_mock):
        instance = TextWindow.__new__(TextWindow)
        instance.current = None

        instance.set_current_values()

        super_current_values_mock.assert_not_called()

    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.CustomizationWindow.set_current_values')
    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.customization_helper')
    def test_set_current_values_success(self, customization_helper_mock, super_current_values_mock):
        instance = TextWindow.__new__(TextWindow)
        instance.current = Mock()
        instance.current.get_position.return_value = "b"
        instance.current.get_text_attribute.return_value = "3"
        instance.current.get_custom_text.return_value = "custom text"
        instance.current.get_round.return_value = True
        instance.current.get_round_precision.return_value = 5
        instance.current.get_text_size.return_value = 15
        instance.current.get_text_color.return_value = [1, 2, 3, 4]
        instance.current.get_outline_size.return_value = 4
        instance.current.get_outline_color.return_value = [5, 6, 7, 8]
        instance.current.get_show_unit.return_value = True
        instance.current.get_line_break.return_value = False

        position1 = Mock()
        position1.get_string.return_value = "a"
        position2 = Mock()
        position2.get_string.return_value = "b"
        position3 = Mock()
        position3.get_string.return_value = "c"
        instance.position = Mock()
        instance.position.get_model.return_value = [position1, position2, position3]

        attribute1 = Mock()
        attribute1.get_string.return_value = "1"
        attribute2 = Mock()
        attribute2.get_string.return_value = "2"
        attribute3 = Mock()
        attribute3.get_string.return_value = "3"
        instance.attribute = Mock()
        instance.attribute.get_model.return_value = [attribute1, attribute2, attribute3]

        instance.check_position = Mock()
        instance.check_text_attribute = Mock()
        instance.check_round = Mock()
        instance.check_precision = Mock()
        instance.check_text_size = Mock()
        instance.check_text_color = Mock()
        instance.check_outline_size = Mock()
        instance.check_outline_color = Mock()
        instance.check_show_unit = Mock()
        instance.check_line_break = Mock()

        instance.custom_text = Mock()
        instance.round = Mock()
        instance.precision = Mock()
        instance.precision_entry = Mock()
        instance.text_size = Mock()
        instance.text_size_entry = Mock()
        instance.text_color = Mock()
        instance.outline_size = Mock()
        instance.outline_size_entry = Mock()
        instance.outline_color = Mock()
        instance.show_unit = Mock()
        instance.show_line_break = Mock()

        customization_helper_mock.convert_color_list_to_rgba.side_effect = ["color1", "color2"]

        instance.set_current_values()

        super_current_values_mock.assert_called_once()
        instance.position.set_selected.assert_called_once_with(1)
        instance.check_position.set_active.assert_called_once_with(True)
        instance.attribute.set_selected.assert_called_once_with(2)
        instance.check_text_attribute.set_active.assert_called_once_with(True)
        instance.custom_text.set_text.assert_called_once_with("custom text")
        instance.custom_text.set_visible.assert_called_once_with(True)
        instance.round.set_active.assert_called_once_with(True)
        instance.check_round.set_active.assert_called_once_with(True)
        instance.precision.set_value.assert_called_once_with(5)
        instance.precision_entry.set_text.assert_called_once_with("5")
        instance.check_precision.set_active.assert_called_once_with(True)
        instance.text_size.set_value.assert_called_once_with(15)
        instance.text_size_entry.set_text.assert_called_once_with("15")
        instance.check_text_size.set_active.assert_called_once_with(True)
        instance.text_color.set_rgba.assert_called_once_with("color1")
        instance.check_text_color.set_active.assert_called_once_with(True)
        instance.outline_size.set_value.assert_called_once_with(4)
        instance.outline_size_entry.set_text.assert_called_once_with("4")
        instance.check_outline_size.set_active.assert_called_once_with(True)
        instance.outline_color.set_rgba.assert_called_once_with("color2")
        instance.check_outline_color.set_active.assert_called_once_with(True)
        instance.show_unit.set_active.assert_called_once_with(True)
        instance.check_show_unit.set_active.assert_called_once_with(True)
        instance.show_line_break.set_active.assert_called_once_with(False)
        instance.check_line_break.set_active.assert_called_once_with(True)

    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.CustomizationWindow.on_add_button')
    def test_on_add_button_super_not_ok(self, super_on_add_button_mock):
        super_on_add_button_mock.return_value = False

        instance = TextWindow.__new__(TextWindow)
        instance.check_position = Mock()

        instance.on_add_button()

        super_on_add_button_mock.assert_called_once()
        instance.check_position.assert_not_called()

    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.CustomizationWindow.on_add_button')
    def test_on_add_button_wrong_position(self, super_on_add_button_mock):
        super_on_add_button_mock.return_value = True

        instance = TextWindow.__new__(TextWindow)
        instance.check_position = Mock()
        instance.check_position.get_active.return_value = True
        instance.position = Mock()
        instance.position.get_selected.return_value = -1
        instance.check_text_attribute = Mock()

        instance.on_add_button()

        super_on_add_button_mock.assert_called_once()
        instance.position.add_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_text_attribute.assert_not_called()

    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.CustomizationWindow.on_add_button')
    def test_on_add_button_wrong_attribute(self, super_on_add_button_mock):
        super_on_add_button_mock.return_value = True

        instance = TextWindow.__new__(TextWindow)
        instance.check_position = Mock()
        instance.check_position.get_active.return_value = True
        instance.position = Mock()
        instance.position.get_selected.return_value = 1
        instance.check_text_attribute = Mock()
        instance.check_text_attribute.get_active.return_value = True
        instance.attribute = Mock()
        instance.attribute.get_selected.return_value = -1
        instance.check_round = Mock()

        instance.on_add_button()

        super_on_add_button_mock.assert_called_once()
        instance.attribute.add_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_round.assert_not_called()

    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.CustomizationWindow.on_add_button')
    def test_on_add_button_no_check_selected(self, super_on_add_button_mock):
        super_on_add_button_mock.return_value = True

        instance = TextWindow.__new__(TextWindow)
        instance.check_position = Mock()
        instance.check_position.get_active.return_value = False
        instance.check_text_attribute = Mock()
        instance.check_text_attribute.get_active.return_value = False
        instance.check_round = Mock()
        instance.check_round.get_active.return_value = False
        instance.check_precision = Mock()
        instance.check_precision.get_active.return_value = False
        instance.check_text_size = Mock()
        instance.check_text_size.get_active.return_value = False
        instance.check_text_color = Mock()
        instance.check_text_color.get_active.return_value = False
        instance.check_outline_size = Mock()
        instance.check_outline_size.get_active.return_value = False
        instance.check_outline_color = Mock()
        instance.check_outline_color.get_active.return_value = False
        instance.check_show_unit = Mock()
        instance.check_show_unit.get_active.return_value = False
        instance.check_line_break = Mock()
        instance.check_line_break.get_active.return_value = False

        instance.on_add_button()

        super_on_add_button_mock.assert_called_once()
        instance.check_position.add_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_text_attribute.add_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_round.add_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_precision.add_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_text_size.add_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_text_color.add_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_outline_size.add_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_outline_color.add_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_show_unit.add_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_line_break.add_css_class.assert_called_once_with(text_const.ERROR)

    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.CustomizationWindow.on_add_button')
    def test_on_add_button_attribute_not_a_number(self, super_on_add_button_mock):
        super_on_add_button_mock.return_value = True

        instance = TextWindow.__new__(TextWindow)
        instance.check_position = Mock()
        instance.check_position.get_active.return_value = False
        instance.check_text_attribute = Mock()
        instance.check_text_attribute.get_active.return_value = False
        instance.check_round = Mock()
        instance.check_round.get_active.return_value = False
        instance.check_precision = Mock()
        instance.check_precision.get_active.return_value = False
        instance.check_text_size = Mock()
        instance.check_text_size.get_active.return_value = False
        instance.check_text_color = Mock()
        instance.check_text_color.get_active.return_value = False
        instance.check_outline_size = Mock()
        instance.check_outline_size.get_active.return_value = False
        instance.check_outline_color = Mock()
        instance.check_outline_color.get_active.return_value = False
        instance.check_show_unit = Mock()
        instance.check_show_unit.get_active.return_value = False
        instance.check_line_break = Mock()
        instance.check_line_break.get_active.return_value = True

        condition_attribute_item = Mock()
        condition_attribute_item.get_string.return_value = text_const.CUSTOM_TEXT_LENGTH

        instance.condition_attribute = Mock()
        instance.condition_attribute.get_selected_item.return_value = condition_attribute_item

        instance.entry_value = Mock()
        instance.entry_value.get_text.return_value = "not a number"

        instance.operator = Mock()

        instance.on_add_button()

        super_on_add_button_mock.assert_called_once()
        instance.operator.add_css_class.assert_called_once_with(text_const.ERROR)
        instance.entry_value.add_css_class.assert_called_once_with(text_const.ERROR)

    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.CustomizationWindow.on_add_button')
    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.customization_helper')
    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.TextCustomization')
    def test_on_add_button_success(self, text_customization_mock, customization_helper_mock, super_on_add_button_mock):
        super_on_add_button_mock.return_value = True

        instance = TextWindow.__new__(TextWindow)
        instance.check_position = Mock()
        instance.check_position.get_active.return_value = True
        instance.check_text_attribute = Mock()
        instance.check_text_attribute.get_active.return_value = True
        instance.check_round = Mock()
        instance.check_round.get_active.return_value = True
        instance.check_precision = Mock()
        instance.check_precision.get_active.return_value = True
        instance.check_text_size = Mock()
        instance.check_text_size.get_active.return_value = True
        instance.check_text_color = Mock()
        instance.check_text_color.get_active.return_value = True
        instance.check_outline_size = Mock()
        instance.check_outline_size.get_active.return_value = True
        instance.check_outline_color = Mock()
        instance.check_outline_color.get_active.return_value = True
        instance.check_show_unit = Mock()
        instance.check_show_unit.get_active.return_value = True
        instance.check_line_break = Mock()
        instance.check_line_break.get_active.return_value = True

        condition_attribute_item = Mock()
        condition_attribute_item.get_string.return_value = "attribute1"

        instance.condition_attribute = Mock()
        instance.condition_attribute.get_selected_item.return_value = condition_attribute_item

        instance.entry_value = Mock()
        instance.entry_value.get_text.return_value = "some_value"

        instance.operator = Mock()
        instance.operator.value = ">="
        instance.operator.get_selected_item.return_value = instance.operator

        color_mock = Mock()
        color_mock.get_rgba.return_value = Mock()

        customization_helper_mock.convert_rgba_to_color_list.side_effect = [[1, 2, 3, 4], [5, 6, 7, 8]]

        attribute_item = Mock()
        attribute_item.get_string.return_value = text_const.CUSTOM_CUSTOM_TEXT
        instance.attribute = Mock()
        instance.attribute.get_selected.return_value = 1
        instance.attribute.get_selected_item.return_value = attribute_item
        position_item = Mock()
        position_item.get_string.return_value = "top"
        instance.position = Mock()
        instance.position.get_selected.return_value = 1
        instance.position.get_selected_item.return_value = position_item
        instance.custom_text = Mock()
        instance.custom_text.get_text.return_value = "Custom Words"
        instance.round = Mock()
        instance.round.get_active.return_value = True
        instance.precision = Mock()
        instance.precision.get_value.return_value = 3
        instance.text_size = Mock()
        instance.text_size.get_value.return_value = 12
        instance.text_color = Mock()
        instance.text_color.get_rgba.return_value = color_mock
        instance.outline_size = Mock()
        instance.outline_size.get_value.return_value = 2
        instance.outline_color = Mock()
        instance.outline_color.get_rgba.return_value = color_mock
        instance.show_unit = Mock()
        instance.show_unit.get_active.return_value = False
        instance.show_line_break = Mock()
        instance.show_line_break.get_active.return_value = True

        instance.callback = Mock()
        instance.index = 17
        instance.destroy = Mock()

        instance.on_add_button()

        super_on_add_button_mock.assert_called_once()
        customization_helper_mock.convert_rgba_to_color_list.assert_has_calls([call(color_mock),
                                                                               call(color_mock)])
        instance.callback.assert_called_once_with(ANY, index=17)
        text_customization_mock.assert_called_once_with(attribute="attribute1",
                                                        operator=">=",
                                                        value="some_value",
                                                        position="top", text_attribute=text_const.CUSTOM_CUSTOM_TEXT,
                                                        custom_text="Custom Words",
                                                        do_round=True, round_precision=3,
                                                        text_size=12, text_color=[1, 2, 3, 4], outline_size=2,
                                                        outline_color=[5, 6, 7, 8], show_unit=False, line_break=True)
        instance.destroy.assert_called_once()

    @patch(
        'HomeAssistantPlugin.actions.show_text.text_window.CustomizationWindow.on_widget_changed')
    def test_on_widget_changed(self, super_on_widget_changed_mock):
        instance = TextWindow.__new__(TextWindow)
        instance.check_position = Mock()
        instance.position = Mock()
        instance.check_text_attribute = Mock()
        instance.attribute = Mock()
        instance.custom_text = Mock()
        instance.check_round = Mock()
        instance.check_precision = Mock()
        instance.check_text_size = Mock()
        instance.check_show_unit = Mock()
        instance.check_line_break = Mock()

        instance.on_widget_changed()

        super_on_widget_changed_mock.assert_called_once()
        instance.check_position.remove_css_class.assert_called_once_with(text_const.ERROR)
        instance.position.remove_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_text_attribute.remove_css_class.assert_called_once_with(text_const.ERROR)
        instance.attribute.remove_css_class.assert_called_once_with(text_const.ERROR)
        instance.custom_text.remove_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_round.remove_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_precision.remove_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_text_size.remove_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_show_unit.remove_css_class.assert_called_once_with(text_const.ERROR)
        instance.check_line_break.remove_css_class.assert_called_once_with(text_const.ERROR)
