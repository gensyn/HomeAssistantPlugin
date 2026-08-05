import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.show_icon import icon_const
from HomeAssistantPlugin.actions.show_icon.icon_window import IconWindow
from HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization


class TestIconWindow(unittest.TestCase):

    @patch(
        'HomeAssistantPlugin.actions.show_icon.icon_window.CustomizationWindow.__init__',
        autospec=True)
    @patch.object(IconWindow, "set_title")
    @patch.object(IconWindow, "_after_init")
    @patch.object(IconWindow, "_create_check_button")
    @patch.object(IconWindow, "_create_entry")
    @patch.object(IconWindow, "_create_color_button")
    @patch.object(IconWindow, "_create_scale")
    @patch.object(IconWindow, "_create_scale_entry")
    @patch.object(IconWindow, "_create_label")
    @patch('HomeAssistantPlugin.actions.show_icon.icon_window.Button')
    def test_init(self, button_mock, create_label_mock, create_scale_entry_mock, create_scale_mock, create_color_button_mock,
                  create_entry_mock, create_check_button_mock, after_init_mock, set_title_mock,
                  customization_window_init_mock):
        lm = Mock()
        lm.get.return_value = "Test Title"
        attributes = Mock()
        callback = Mock()
        current = Mock()
        index = 1

        def super_init(instance, lm, *args, **kwargs):
            instance.lm = lm
            instance.grid_fields = Mock()

        customization_window_init_mock.side_effect = super_init

        instance = IconWindow(lm, attributes, callback, current, index)

        self.assertEqual(4, create_check_button_mock.call_count)
        self.assertEqual(1, create_entry_mock.call_count)
        self.assertEqual(1, create_color_button_mock.call_count)
        self.assertEqual(2, create_scale_mock.call_count)
        self.assertEqual(2, create_scale_entry_mock.call_count)
        self.assertEqual(4, create_label_mock.call_count)
        customization_window_init_mock.assert_called_once_with(instance, lm, attributes, callback, current,
                                                               index)  # with instance because of autospec
        set_title_mock.assert_called_once_with("Test Title")
        self.assertEqual(15, instance.grid_fields.attach.call_count)
        after_init_mock.assert_called_once()

    @patch(
        'HomeAssistantPlugin.actions.show_icon.icon_window.CustomizationWindow.set_default_values')
    def testset_default_values(self, super_set_default_values_mock):
        instance = IconWindow.__new__(IconWindow)
        instance.color = Mock()
        instance.scale = Mock()
        instance.scale_entry = Mock()
        instance.opacity = Mock()
        instance.opacity_entry = Mock()

        instance.set_default_values()

        super_set_default_values_mock.assert_called_once()
        instance.color.set_rgba.assert_called_once()
        instance.scale.set_value.assert_called_once_with(icon_const.DEFAULT_ICON_SCALE)
        instance.scale_entry.set_text.assert_called_once_with(str(icon_const.DEFAULT_ICON_SCALE))
        instance.opacity.set_value.assert_called_once_with(icon_const.DEFAULT_ICON_OPACITY)
        instance.opacity_entry.set_text.assert_called_once_with(str(icon_const.DEFAULT_ICON_OPACITY))

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_window.CustomizationWindow.set_current_values')
    def test_set_current_values_no_current(self, super_set_current_values_mock):
        instance = IconWindow.__new__(IconWindow)
        instance.current = None

        instance.set_current_values()

        super_set_current_values_mock.assert_not_called()

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_window.CustomizationWindow.set_current_values')
    def test_set_current_values_with_current(self, super_set_current_values_mock):
        instance = IconWindow.__new__(IconWindow)
        instance.current = Mock()
        instance.current.get_icon.return_value = "icon_name"
        instance.current.get_color.return_value = [255, 0, 0]
        instance.current.get_scale.return_value = 150
        instance.current.get_opacity.return_value = 200

        instance.icon = Mock()
        instance.check_icon = Mock()
        instance.color = Mock()
        instance.check_color = Mock()
        instance.scale = Mock()
        instance.scale_entry = Mock()
        instance.check_scale = Mock()
        instance.opacity = Mock()
        instance.opacity_entry = Mock()
        instance.check_opacity = Mock()

        instance.set_current_values()

        super_set_current_values_mock.assert_called_once()
        instance.icon.set_text.assert_called_once_with("icon_name")
        instance.check_icon.set_active.assert_called_once_with(True)
        instance.color.set_rgba.assert_called_once()
        instance.check_color.set_active.assert_called_once_with(True)
        instance.scale.set_value.assert_called_once_with(150)
        instance.check_scale.set_active.assert_called_once_with(True)
        instance.scale_entry.set_text.assert_called_once_with("150")
        instance.opacity.set_value.assert_called_once_with(200)
        instance.check_opacity.set_active.assert_called_once_with(True)
        instance.opacity_entry.set_text.assert_called_once_with("200")

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_window.CustomizationWindow.on_add_button')
    def test_on_add_button_super_false(self, super_on_add_button_mock):
        super_on_add_button_mock.return_value = False

        instance = IconWindow.__new__(IconWindow)
        instance.check_icon = Mock()
        instance.on_add_button()

        super_on_add_button_mock.assert_called_once()
        instance.check_icon.get_active.assert_not_called()

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_window.CustomizationWindow.on_add_button')
    def test_on_add_button_icon_checked_but_empty(self, super_on_add_button_mock):
        super_on_add_button_mock.return_value = True

        instance = IconWindow.__new__(IconWindow)
        instance.check_icon = Mock()
        instance.check_icon.get_active.return_value = True
        instance.icon = Mock()
        instance.icon.get_text.return_value = ""
        instance.on_add_button()

        super_on_add_button_mock.assert_called_once()
        instance.check_icon.get_active.assert_called_once()
        instance.icon.get_text.assert_called_once()
        instance.icon.add_css_class.assert_called_once_with(icon_const.ERROR)

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_window.CustomizationWindow.on_add_button')
    def test_on_add_button_no_customization_selected(self, super_on_add_button_mock):
        super_on_add_button_mock.return_value = True

        instance = IconWindow.__new__(IconWindow)
        instance.check_icon = Mock()
        instance.check_icon.get_active.return_value = False
        instance.check_color = Mock()
        instance.check_color.get_active.return_value = False
        instance.check_scale = Mock()
        instance.check_scale.get_active.return_value = False
        instance.check_opacity = Mock()
        instance.check_opacity.get_active.return_value = False
        instance.on_add_button()

        super_on_add_button_mock.assert_called_once()
        self.assertEqual(2, instance.check_icon.get_active.call_count)
        instance.check_icon.add_css_class.assert_called_once_with(icon_const.ERROR)
        instance.check_color.add_css_class.assert_called_once_with(icon_const.ERROR)
        instance.check_scale.add_css_class.assert_called_once_with(icon_const.ERROR)
        instance.check_opacity.add_css_class.assert_called_once_with(icon_const.ERROR)

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_window.CustomizationWindow.on_add_button')
    @patch(
        'HomeAssistantPlugin.actions.show_icon.icon_window.IconCustomization')
    def test_on_add_button_success(self, icon_customization_mock, super_on_add_button_mock):
        super_on_add_button_mock.return_value = True

        instance = IconWindow.__new__(IconWindow)
        instance.check_icon = Mock()
        instance.check_icon.get_active.return_value = True
        instance.condition_attribute = Mock()
        instance.condition_attribute.get_selected_item.return_value.get_string.return_value = "attribute_name"
        instance.operator = Mock()
        instance.operator.get_selected_item.return_value.value = "=="
        instance.entry_value = Mock()
        instance.entry_value.get_text.return_value = "some_value"
        instance.icon = Mock()
        instance.icon.get_text.return_value = "mdi:home"
        instance.icons = ["home"]
        instance.check_color = Mock()
        instance.check_color.get_active.return_value = True
        instance.color = Mock()
        rgba_mock = Mock()
        rgba_mock.red = 266
        rgba_mock.green = 0
        rgba_mock.blue = 0
        rgba_mock.alpha = 1
        instance.color.get_rgba.return_value = rgba_mock
        instance.check_scale = Mock()
        instance.check_scale.get_active.return_value = True
        instance.scale = Mock()
        instance.scale.get_value.return_value = 150
        instance.check_opacity = Mock()
        instance.check_opacity.get_active.return_value = True
        instance.opacity = Mock()
        instance.opacity.get_value.return_value = 200
        instance.index = 5
        instance.callback = Mock()
        instance.destroy = Mock()
        instance.on_add_button()

        super_on_add_button_mock.assert_called_once()
        self.assertEqual(3, instance.check_icon.get_active.call_count)
        self.assertEqual(2, instance.icon.get_text.call_count)
        instance.check_color.get_active.assert_called_once()
        instance.color.get_rgba.assert_called_once()
        instance.check_scale.get_active.assert_called_once()
        instance.scale.get_value.assert_called_once()
        instance.check_opacity.get_active.assert_called_once()
        instance.opacity.get_value.assert_called_once()
        instance.color.get_rgba.assert_called_once()
        instance.scale.get_value.assert_called_once()
        instance.opacity.get_value.assert_called_once()
        icon_customization_mock.assert_called_once_with(attribute="attribute_name", operator="==", value="some_value",
                                                        icon="mdi:home", color=(67830, 0, 0, 255), scale=150,
                                                        opacity=200)
        instance.callback.assert_called_once()
        instance.destroy.assert_called_once()

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_window.CustomizationWindow.on_widget_changed')
    def test_on_widget_changed(self, super_on_widget_changed_mock):
        instance = IconWindow.__new__(IconWindow)
        instance.icon = Mock()
        instance.check_icon = Mock()
        instance.check_color = Mock()
        instance.check_scale = Mock()
        instance.check_opacity = Mock()

        instance.on_widget_changed()

        super_on_widget_changed_mock.assert_called_once()
        instance.icon.remove_css_class.assert_called_once_with(icon_const.ERROR)
        instance.check_icon.remove_css_class.assert_called_once_with(icon_const.ERROR)
        instance.check_color.remove_css_class.assert_called_once_with(icon_const.ERROR)
        instance.check_scale.remove_css_class.assert_called_once_with(icon_const.ERROR)
        instance.check_opacity.remove_css_class.assert_called_once_with(icon_const.ERROR)
