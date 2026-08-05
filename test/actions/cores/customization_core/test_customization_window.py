import sys
import types
import unittest
from functools import partial
from pathlib import Path
from unittest.mock import MagicMock, patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

class TestCustomizationWindow(unittest.TestCase):
    def setUp(self):
        # Patch all GTK/Adw/gi classes used in CustomizationWindow to allow headless testing
        self.gtk_patches = {}
        gtk_names = [
            "Align", "Box", "Button", "DropDown", "CssProvider",
            "Entry", "Grid", "Label", "ListStore", "Window", "ColorDialogButton",
            "CheckButton", "Scale", "Orientation", "Switch"
        ]
        for name in gtk_names:
            p = patch(f"HomeAssistantPlugin.actions.cores.customization_core.customization_window.{name}")
            self.gtk_patches[name] = p
            p.start()

        # Patch base_const and customization_const
        self.base_const_patch = patch("HomeAssistantPlugin.actions.cores.customization_core.customization_window.base_const")
        self.customization_const_patch = patch("HomeAssistantPlugin.actions.cores.customization_core.customization_window.customization_const")
        self.mock_base_const = self.base_const_patch.start()
        self.mock_customization_const = self.customization_const_patch.start()
        self.mock_base_const.CONNECT_CLICKED = "clicked"
        self.mock_base_const.CONNECT_CHANGED = "changed"
        self.mock_base_const.CONNECT_ACTIVATE = "activate"
        self.mock_base_const.CONNECT_VALUE_CHANGED = "value-changed"
        self.mock_base_const.CONNECT_NOTIFY_ACTIVE = "notify::active"
        self.mock_base_const.CONNECT_NOTIFY_COLOR_SET = "notify::color-set"
        self.mock_base_const.CONNECT_TOGGLED = "toggled"
        self.mock_customization_const.LABEL_CUSTOMIZATION_ATTRIBUTE = "attribute"
        self.mock_customization_const.LABEL_CUSTOMIZATION_OPERATOR = "operator"
        self.mock_customization_const.LABEL_CUSTOMIZATION_VALUE = "value"
        self.mock_customization_const.LABEL_CUSTOMIZATION_IF = "if"
        self.mock_customization_const.LABEL_CUSTOMIZATION_CANCEL = "cancel"
        self.mock_customization_const.LABEL_CUSTOMIZATION_ADD = "add"
        self.mock_customization_const.LABEL_CUSTOMIZATION_UPDATE = "update"
        self.mock_customization_const.LABEL_CUSTOMIZATION_OPERATORS = {
            "==": "Equals",
            "!=": "Not Equals",
            "<": "Less",
            "<=": "Less or Equal",
            ">": "Greater",
            ">=": "Greater or Equal"
        }
        self.mock_customization_const.ERROR = "error"
        self.mock_customization_const.EMPTY_STRING = ""

        # Patch Customization
        self.customization_patch = patch("HomeAssistantPlugin.actions.cores.customization_core.customization_window.Customization")
        self.MockCustomization = self.customization_patch.start()

        self.gtk_window_init_patch = patch(
            "gi.repository.Gtk.Window.__init__",
            return_value=None
        )
        self.mock_gtk_window_init = self.gtk_window_init_patch.start()

        # Import after patching
        from HomeAssistantPlugin.actions.cores.customization_core import customization_window
        self.customization_window = customization_window

        # Patch instance methods that would require real GTK widgets
        self.set_child_patch = patch.object(self.customization_window.CustomizationWindow, "set_child")
        self.mock_set_child = self.set_child_patch.start()
        self.destroy_patch = patch.object(self.customization_window.CustomizationWindow, "destroy")
        self.mock_destroy = self.destroy_patch.start()
        self.set_modal_patch = patch.object(self.customization_window.CustomizationWindow, "set_modal")
        self.mock_set_modal = self.set_modal_patch.start()

        # Patch Grid.attach and Box.append for layout logic
        self.grid_attach_patch = patch("HomeAssistantPlugin.actions.cores.customization_core.customization_window.Grid.attach")
        self.box_append_patch = patch("HomeAssistantPlugin.actions.cores.customization_core.customization_window.Box.append")
        self.mock_grid_attach = self.grid_attach_patch.start()
        self.mock_box_append = self.box_append_patch.start()

        # Patch Button/Entry/ComboBox/Label/etc widget methods for margin, halign, etc
        self.widget_patchers = {}
        for method in [
            "set_margin_top", "set_margin_bottom", "set_margin_start", "set_margin_end",
            "set_halign", "set_active", "set_text", "set_width_chars", "set_max_width_chars", "set_model",
            "pack_start", "add_attribute", "set_halign", "set_sensitive", "set_modal"
        ]:
            self.widget_patchers[method] = patch(
                f"HomeAssistantPlugin.actions.cores.customization_core.customization_window.Button.{method}"
            )
            self.widget_patchers[method].start()
            self.widget_patchers[method] = patch(
                f"HomeAssistantPlugin.actions.cores.customization_core.customization_window.Entry.{method}"
            )
            self.widget_patchers[method].start()
            self.widget_patchers[method] = patch(
                f"HomeAssistantPlugin.actions.cores.customization_core.customization_window.DropDown.{method}"
            )
            self.widget_patchers[method].start()
            self.widget_patchers[method] = patch(
                f"HomeAssistantPlugin.actions.cores.customization_core.customization_window.Label.{method}"
            )
            self.widget_patchers[method].start()

        # Patch methods for style context and get_model
        for name in ["condition_attribute", "operator", "entry_value"]:
            setattr(self, f"mock_{name}", MagicMock())
            sc = MagicMock()
            getattr(self, f"mock_{name}").get_style_context.return_value = sc
            sc.add_class = MagicMock()
            sc.remove_class = MagicMock()
            getattr(self, f"mock_{name}").get_model.return_value = [["attr1"], ["attr2"], ["attr3"]]
            getattr(self, f"mock_{name}").set_active = MagicMock()
            getattr(self, f"mock_{name}").set_text = MagicMock()

    def tearDown(self):
        for p in self.gtk_patches.values():
            p.stop()
        self.base_const_patch.stop()
        self.customization_const_patch.stop()
        self.customization_patch.stop()
        self.set_child_patch.stop()
        self.destroy_patch.stop()
        self.grid_attach_patch.stop()
        self.box_append_patch.stop()
        self.gtk_window_init_patch.stop()
        self.set_modal_patch.stop()
        for k in self.widget_patchers:
            try:
                self.widget_patchers[k].stop()
            except Exception:
                pass

    def get_window(self, current=None):
        mock_lm = MagicMock()
        mock_lm.get.side_effect = lambda x: str(x)
        attributes = ["attr1", "attr2", "attr3"]
        callback = MagicMock()
        window = self.customization_window.CustomizationWindow(
            lm=mock_lm,
            attributes=attributes,
            callback=callback,
            current=current,
            index=1
        )
        # Patch internal combo/entry widgets for style context and get_model
        window.condition_attribute = MagicMock()
        window.operator = MagicMock()
        window.entry_value = MagicMock()
        return window

    def test_init_sets_attributes_and_layout(self):
        window = self.get_window()
        self.assertEqual(window.attributes, ["attr1", "attr2", "attr3"])
        self.assertEqual(window.index, 1)
        self.assertIsNotNone(window.lm)
        self.assertIsNotNone(window.callback)
        self.mock_set_child.assert_called()

    def test_is_number(self):
        window = self.get_window()
        self.assertTrue(window._is_number("123"))
        self.assertTrue(window._is_number("12.5"))
        self.assertFalse(window._is_number("abc"))
        self.assertFalse(window._is_number(""))

    def test_on_add_button_invalid_states(self):
        window = self.get_window()
        window.condition_attribute.get_selected.return_value = -1
        window.operator.get_selected.return_value = 0
        window.entry_value.get_text.return_value = "foo"
        self.assertFalse(window.on_add_button(None))
        window.condition_attribute.add_css_class.assert_called_with(self.mock_customization_const.ERROR)

        window.condition_attribute.get_selected.return_value = 0
        window.operator.get_selected.return_value = -1
        self.assertFalse(window.on_add_button(None))
        window.operator.add_css_class.assert_called_with(self.mock_customization_const.ERROR)

        window.operator.get_selected.return_value = 0
        window.entry_value.get_text.return_value = ""
        self.assertFalse(window.on_add_button(None))
        window.entry_value.add_css_class.assert_called_with(self.mock_customization_const.ERROR)

        window.operator.get_selected.return_value = 2
        window.entry_value.get_text.return_value = "not_a_number"
        self.assertFalse(window.on_add_button(None))
        window.operator.add_css_class.assert_called_with(self.mock_customization_const.ERROR)
        window.entry_value.add_css_class.assert_called_with(self.mock_customization_const.ERROR)

    def test_on_add_button_valid(self):
        window = self.get_window()
        window.condition_attribute.get_selected.return_value = 0
        window.operator.get_selected.return_value = 0
        window.entry_value.get_text.return_value = "42"
        self.assertTrue(window.on_add_button(None))

    def test_on_widget_changed_removes_error(self):
        window = self.get_window()
        window.on_widget_changed(None)
        window.condition_attribute.remove_css_class.assert_called_with(self.mock_customization_const.ERROR)
        window.operator.remove_css_class.assert_called_with(self.mock_customization_const.ERROR)
        window.entry_value.remove_css_class.assert_called_with(self.mock_customization_const.ERROR)

    def test_set_default_values_and_current_values(self):
        window = self.get_window()
        window.condition_attribute.set_selected = MagicMock()
        window.operator.set_selected = MagicMock()
        window.set_default_values()
        window.condition_attribute.set_selected.assert_called_with(0)
        window.operator.set_selected.assert_called_with(0)

    def test_set_current_values_no_current(self):
        window = self.get_window(current=None)
        window.condition_attribute.set_active = MagicMock()
        window.operator.set_active = MagicMock()
        window.entry_value.set_text = MagicMock()
        window.condition_attribute.get_model.return_value = [["attr1"], ["attr2"], ["attr3"]]
        window.operator.get_model.return_value = [["attr1"], ["attr2"], ["attr3"]]
        window.set_current_values()
        window.condition_attribute.set_active.assert_not_called()
        window.operator.set_active.assert_not_called()
        window.entry_value.set_text.assert_not_called()

    def testset_current_values(self):
        attr1_mock = MagicMock()
        attr1_mock.get_string.return_value = "attr1"
        attr1_mock.value = "attr1"
        attr2_mock = MagicMock()
        attr2_mock.get_string.return_value = "attr2"
        attr2_mock.value = "attr2"
        attr3_mock = MagicMock()
        attr3_mock.get_string.return_value = "attr3"
        attr3_mock.value = "attr3"
        current = MagicMock()
        current.get_attribute.return_value = "attr2"
        current.get_operator.return_value = "attr3"
        current.get_value.return_value = "55"
        window = self.get_window(current=current)
        window.condition_attribute.set_selected = MagicMock()
        window.operator.set_selected = MagicMock()
        window.entry_value.set_text = MagicMock()
        window.condition_attribute.get_model.return_value = [attr1_mock, attr2_mock, attr3_mock]
        window.operator.get_model.return_value = [attr1_mock, attr2_mock, attr3_mock]
        window.set_current_values()
        window.condition_attribute.set_selected.assert_called_with(1)
        window.operator.set_selected.assert_called_with(2)
        window.entry_value.set_text.assert_called_with("55")

    def test_on_cancel_button_calls_destroy(self):
        window = self.get_window()
        window._on_cancel_button(None)
        self.mock_destroy.assert_called()

    def test_connect_rows(self):
        window = self.get_window()
        called = []
        def make_connect():
            def fn():
                called.append(True)
            return fn
        window.connect_rows = [make_connect(), make_connect()]
        window._connect_rows()
        self.assertEqual(len(called), 2)

    def test_create_button_returns_button(self):
        window = self.get_window()
        btn = window._create_button("label")
        self.assertTrue(btn)

    def test_create_combo_returns_combo(self):
        window = self.get_window()
        combo = window._create_drop_down(["a", "b", "c"])
        self.assertTrue(combo)

    def test_create_combo_with_check(self):
        window = self.get_window()
        check = MagicMock()
        combo = MagicMock()
        # Patch ComboBox so that window._create_combo uses our combo mock
        with patch("HomeAssistantPlugin.actions.cores.customization_core.customization_window.DropDown",
                   return_value=combo):
            combo.get_selected.return_value = 1  # Simulate selected
            # Clear previous connect_rows so we only have new ones for this call
            window.connect_rows = []
            result = window._create_drop_down(["a", "b", "c"], check=check)
            self.assertIs(result, combo)
            # Find the lambda for check.set_active in connect_rows and call it
            found = False
            for p in window.connect_rows:
                if isinstance(p, partial) and p.args and callable(p.args[-1]):
                    # This will be the lambda for check.set_active
                    p.args[-1](None, None)
                    try:
                        check.set_active.assert_called_with(True)
                        found = True
                        break
                    except AssertionError:
                        continue
            self.assertTrue(found, "Did not find partial with lambda for check.set_active")

    def test_create_combo_operator_returns_combo(self):
        window = self.get_window()
        combo = window._create_drop_down_operator()
        self.assertTrue(combo)

    def test_create_label_returns_label(self):
        window = self.get_window()
        lbl = window._create_label("hello")
        self.assertTrue(lbl)

    def test_create_entry_returns_entry(self):
        window = self.get_window()
        entry = window._create_entry()
        self.assertTrue(entry)

    def test_create_entry_with_check(self):
        window = self.get_window()
        check = MagicMock()
        entry = window._create_entry(check=check)
        self.assertTrue(entry)
        # Set .get_text.return_value to a string
        entry.get_text.return_value = "foo"
        found = False
        for p in window.connect_rows:
            if isinstance(p, partial) and p.args and isinstance(p.args[-1], types.LambdaType):
                # Now, this is the lambda for check.set_active
                p.args[-1](None)
                try:
                    check.set_active.assert_called_with(True)
                    found = True
                    break
                except AssertionError:
                    continue
        self.assertTrue(found, "Did not find partial with lambda for check.set_active")

    def test_create_scale_returns_scale(self):
        window = self.get_window()
        check = MagicMock()
        scale = window._create_scale(0, 10, 1, check)
        self.assertTrue(scale)

    def test_create_scale_entry_returns_entry(self):
        window = self.get_window()
        check = MagicMock()
        entry = window._create_scale_entry(check)
        self.assertTrue(entry)

    def test_create_switch_returns_switch(self):
        window = self.get_window()
        check = MagicMock()
        switch = window._create_switch(check)
        self.assertTrue(switch)

    def test_create_color_button_returns_color_button(self):
        window = self.get_window()
        check = MagicMock()
        btn = window._create_color_button(check)
        self.assertTrue(btn)

    def test_create_check_button_returns_check_button(self):
        window = self.get_window()
        check_btn = window._create_check_button()
        self.assertTrue(check_btn)

    def test_on_change_scale_and_entry(self):
        window = self.get_window()
        scale = MagicMock()
        entry = MagicMock()

        # _on_change_scale: value out of range, should call set_value
        scale.get_value.return_value = 20  # Out of range: max is 10
        entry.get_text.return_value = "7"
        scale.disconnect_by_func = MagicMock()
        scale.set_value = MagicMock()
        scale.connect = MagicMock()
        entry.disconnect_by_func = MagicMock()
        entry.set_text = MagicMock()
        entry.connect = MagicMock()
        window._on_change_scale(scale, entry, 0, 10)
        scale.set_value.assert_called()  # Now it should be called

        # _on_change_scale_entry: text is out of range, should call set_text
        entry.get_text.return_value = "15"  # Out of range: max is 10
        scale.get_value.return_value = 10
        window._on_change_scale_entry(entry, scale, 0, 10)
        entry.set_text.assert_called()  # Now it should be called
        scale.set_value.assert_called()

    def test_on_change_scale_entry_text_digits_empty(self):
        window = self.get_window()
        entry = MagicMock()
        scale = MagicMock()
        entry.get_text.return_value = "abc"  # No digits
        scale.get_value.return_value = 5  # Will not be used for empty text_digits
        entry.disconnect_by_func = MagicMock()
        entry.set_text = MagicMock()
        entry.connect = MagicMock()
        scale.set_value = MagicMock()
        scale.disconnect_by_func = MagicMock()
        scale.connect = MagicMock()
        # Set min_value to 5 so that set_text('5') is expected
        window._on_change_scale_entry(entry, scale, 5, 10)
        entry.set_text.assert_called_with('5')

    def test_after_init_calls_all_methods(self):
        """Test _after_init calls set_default_values, set_current_values, _connect_rows."""
        window = self.get_window()
        # Patch the called methods to monitor calls
        window.set_default_values = MagicMock()
        window.set_current_values = MagicMock()
        window._connect_rows = MagicMock()
        window.current = MagicMock()
        window._after_init()
        window.set_default_values.assert_called_once()
        window.set_current_values.assert_called_once()
        window._connect_rows.assert_called_once()