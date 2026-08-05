"""
The module for the Home Assistant customization window.
"""
from functools import partial
from typing import Callable

import gi
from gi.repository import GObject
from gi.repository.GLib import Bytes
from gi.repository.Gio import ListStore

gi.require_version("Gtk", "4.0")
from gi.repository.Gtk import Align, Box, Button, CssProvider, Entry, \
    Grid, Label, Window, CheckButton, Scale, Orientation, Switch, ColorDialog, ColorDialogButton, DropDown, \
    StringObject, PropertyExpression

from HomeAssistantPlugin.actions import const as base_const
from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.cores.customization_core.customization import Customization

CSS = b"""
dropdown.error {
    background-color: #ffcccc; /* Light red */
}
"""
STYLE_PROVIDER = CssProvider()
STYLE_PROVIDER.load_from_bytes(Bytes.new(CSS))


class DropDownItem(GObject.Object):
    value = GObject.Property(type=str)
    label = GObject.Property(type=str)

    def __init__(self, value, label):
        super().__init__()
        self.value = value
        self.label = label


class CustomizationWindow(Window):
    """
    Base for customization windows
    """
    callback: Callable

    connect_rows: list = []
    default_margin = 3

    def __init__(self, lm, attributes: list, callback: Callable,
                 current: Customization = None, index: int = None):
        super().__init__()
        self.callback = callback
        self.lm = lm
        self.index: int = index
        self.attributes: list[str] = attributes
        self.current: Customization = current

        self.set_modal(True)

        label_attribute = self._create_label(lm.get(customization_const.LABEL_CUSTOMIZATION_ATTRIBUTE))
        label_operator = self._create_label(lm.get(customization_const.LABEL_CUSTOMIZATION_OPERATOR))
        label_value = self._create_label(lm.get(customization_const.LABEL_CUSTOMIZATION_VALUE))
        label_if = self._create_label(lm.get(customization_const.LABEL_CUSTOMIZATION_IF))

        self.condition_attribute = self._create_drop_down(self.attributes)
        self.operator = self._create_drop_down_operator()

        self.entry_value = self._create_entry()

        cancel_button = self._create_button(lm.get(customization_const.LABEL_CUSTOMIZATION_CANCEL))
        self.connect_rows.append(
            partial(cancel_button.connect, base_const.CONNECT_CLICKED, self._on_cancel_button))

        add_label = lm.get(customization_const.LABEL_CUSTOMIZATION_ADD) if not current else lm.get(
            customization_const.LABEL_CUSTOMIZATION_UPDATE)
        add_button = self._create_button(add_label)
        self.connect_rows.append(
            partial(add_button.connect, base_const.CONNECT_CLICKED, self.on_add_button))

        label_attribute.set_margin_top(15)
        label_operator.set_margin_top(15)
        label_value.set_margin_top(15)
        cancel_button.set_margin_bottom(15)
        add_button.set_margin_bottom(15)
        add_button.set_margin_end(15)
        label_if.set_margin_start(15)
        label_if.set_margin_bottom(30)
        self.condition_attribute.set_margin_bottom(30)
        self.operator.set_margin_bottom(30)
        self.entry_value.set_margin_end(15)
        self.entry_value.set_margin_bottom(30)

        self.grid_fields = Grid()
        self.grid_fields.attach(label_attribute, 1, 0, 1, 1)
        self.grid_fields.attach(label_operator, 4, 0, 1, 1)
        self.grid_fields.attach(label_value, 5, 0, 1, 1)
        self.grid_fields.attach(label_if, 0, 1, 1, 1)
        self.grid_fields.attach(self.condition_attribute, 1, 1, 3, 1)
        self.grid_fields.attach(self.operator, 4, 1, 1, 1)
        self.grid_fields.attach(self.entry_value, 5, 1, 1, 1)

        box_buttons = Box()
        box_buttons.append(cancel_button)
        box_buttons.append(add_button)
        box_buttons.set_halign(Align.END)

        grid = Grid()
        grid.attach(self.grid_fields, 0, 0, 1, 1)
        grid.attach(box_buttons, 0, 1, 1, 1)

        self.set_child(grid)

    def _after_init(self) -> None:
        self.set_default_values()
        self.set_current_values()
        self._connect_rows()

    def set_default_values(self) -> None:
        self.condition_attribute.set_selected(0)
        self.operator.set_selected(0)

    def set_current_values(self) -> None:
        if not self.current:
            return

        for index, entry in enumerate(self.condition_attribute.get_model()):
            if entry.get_string() == self.current.get_attribute():
                self.condition_attribute.set_selected(index)
                break

        for index, entry in enumerate(self.operator.get_model()):
            if entry.value == self.current.get_operator():
                self.operator.set_selected(index)
                break

        self.entry_value.set_text(self.current.get_value())

    def _create_button(self, label) -> Button:
        button = Button(label=label)
        button.set_margin_top(self.default_margin)
        button.set_margin_bottom(self.default_margin)
        button.set_margin_start(self.default_margin)
        button.set_margin_end(self.default_margin)
        return button

    def _create_drop_down(self, attributes: list, check: CheckButton = None) -> DropDown:
        drop_down = DropDown()
        drop_down.set_margin_top(self.default_margin)
        drop_down.set_margin_bottom(self.default_margin)
        drop_down.set_margin_start(self.default_margin)
        drop_down.set_margin_end(self.default_margin)

        model = ListStore()
        for option in attributes:
            model.append(StringObject.new(option))

        drop_down.set_model(model)

        self.connect_rows.append(
            partial(drop_down.connect, base_const.CONNECT_NOTIFY_SELECTED_ITEM, self.on_widget_changed))

        if check is not None:
            self.connect_rows.append(partial(drop_down.connect, base_const.CONNECT_NOTIFY_SELECTED_ITEM,
                                             lambda _=None, __=None: check.set_active(drop_down.get_selected() >= 0)))

        return drop_down

    def _create_drop_down_operator(self) -> DropDown:
        expression = PropertyExpression.new(DropDownItem, None, "label")

        drop_down = DropDown(expression=expression)
        drop_down.set_margin_top(self.default_margin)
        drop_down.set_margin_bottom(self.default_margin)
        drop_down.set_margin_start(self.default_margin)
        drop_down.set_margin_end(self.default_margin)

        model = ListStore()
        model.append(DropDownItem("==", self.lm.get(customization_const.LABEL_CUSTOMIZATION_OPERATORS["=="])))
        model.append(DropDownItem("!=", self.lm.get(customization_const.LABEL_CUSTOMIZATION_OPERATORS["!="])))
        model.append(DropDownItem("<", self.lm.get(customization_const.LABEL_CUSTOMIZATION_OPERATORS["<"])))
        model.append(DropDownItem("<=", self.lm.get(customization_const.LABEL_CUSTOMIZATION_OPERATORS["<="])))
        model.append(DropDownItem(">", self.lm.get(customization_const.LABEL_CUSTOMIZATION_OPERATORS[">"])))
        model.append(DropDownItem(">=", self.lm.get(customization_const.LABEL_CUSTOMIZATION_OPERATORS[">="])))

        drop_down.set_model(model)

        self.connect_rows.append(
            partial(drop_down.connect, base_const.CONNECT_NOTIFY_SELECTED_ITEM, self.on_widget_changed))

        return drop_down

    def _create_label(self, label: str):
        label = Label(label=label)
        label.set_margin_top(self.default_margin)
        label.set_margin_bottom(self.default_margin)
        label.set_margin_start(self.default_margin)
        label.set_margin_end(self.default_margin)
        label.set_halign(Align.START)
        return label

    def _create_entry(self, check: CheckButton = None) -> Entry:
        entry = Entry()
        entry.set_margin_top(self.default_margin)
        entry.set_margin_bottom(self.default_margin)
        entry.set_margin_start(self.default_margin)
        entry.set_margin_end(15)
        self.connect_rows.append(
            partial(entry.connect, base_const.CONNECT_CHANGED, self.on_widget_changed))
        self.connect_rows.append(
            partial(entry.connect, base_const.CONNECT_ACTIVATE, self.on_add_button))
        if check is not None:
            self.connect_rows.append(partial(entry.connect, base_const.CONNECT_CHANGED,
                                             lambda _=None, __=None: check.set_active(
                                                 entry.get_text() != customization_const.EMPTY_STRING)))
        return entry

    def _create_scale(self, min_value: int, max_value: int, step: int, check: CheckButton) -> Scale:
        scale = Scale.new_with_range(Orientation.HORIZONTAL, min_value, max_value, step)
        scale.set_margin_top(self.default_margin)
        scale.set_margin_bottom(self.default_margin)
        scale.set_margin_start(self.default_margin)
        scale.set_margin_end(self.default_margin)
        self.connect_rows.append(
            partial(scale.connect, base_const.CONNECT_VALUE_CHANGED, lambda _=None, __=None: check.set_active(True)))
        return scale

    def _create_scale_entry(self, check) -> Entry:
        entry = Entry()
        entry.set_margin_top(self.default_margin)
        entry.set_margin_bottom(self.default_margin)
        entry.set_margin_start(self.default_margin)
        entry.set_margin_end(180)
        entry.set_width_chars(4)
        entry.set_max_width_chars(4)
        self.connect_rows.append(
            partial(entry.connect, base_const.CONNECT_ACTIVATE, self.on_add_button))
        self.connect_rows.append(partial(entry.connect, base_const.CONNECT_CHANGED,
                                         lambda _=None, __=None: check.set_active(
                                             entry.get_text() != customization_const.EMPTY_STRING)))
        return entry

    def _create_switch(self, check: CheckButton) -> Switch:
        switch = Switch()
        switch.set_margin_top(self.default_margin)
        switch.set_margin_bottom(self.default_margin)
        switch.set_margin_start(self.default_margin)
        switch.set_margin_end(self.default_margin)
        switch.set_halign(Align.START)
        self.connect_rows.append(partial(switch.connect, base_const.CONNECT_NOTIFY_ACTIVE,
                                         lambda _=None, __=None: check.set_active(True)))
        return switch

    def _create_color_button(self, check: CheckButton) -> ColorDialogButton:
        dialog = ColorDialog(with_alpha=False)
        button = ColorDialogButton(dialog=dialog)
        button.set_margin_top(self.default_margin)
        button.set_margin_bottom(self.default_margin)
        button.set_margin_start(self.default_margin)
        button.set_margin_end(self.default_margin)
        self.connect_rows.append(partial(button.connect, base_const.CONNECT_NOTIFY_RGBA,
                                         lambda _=None, __=None: check.set_active(True)))
        return button

    def _on_cancel_button(self, _):
        self.destroy()

    def on_add_button(self, *_, **__) -> bool:
        if self.condition_attribute.get_selected() < 0:
            self.condition_attribute.add_css_class(customization_const.ERROR)
            return False

        if self.operator.get_selected() < 0:
            self.operator.add_css_class(customization_const.ERROR)
            return False

        if not self.entry_value.get_text():
            self.entry_value.add_css_class(customization_const.ERROR)
            return False

        if self.operator.get_selected() > 1 and not self._is_number(
                self.entry_value.get_text()):
            # operator needs a number
            self.operator.add_css_class(customization_const.ERROR)
            self.entry_value.add_css_class(customization_const.ERROR)
            return False

        return True

    def on_widget_changed(self, *_, **__) -> None:
        self.condition_attribute.remove_css_class(customization_const.ERROR)
        self.operator.remove_css_class(customization_const.ERROR)
        self.entry_value.remove_css_class(customization_const.ERROR)

    def _connect_rows(self) -> None:
        """
        Connect all input fields to functions to be called on changes.
        """
        for connect in self.connect_rows:
            connect()

    def _create_check_button(self) -> CheckButton:
        check = CheckButton()
        check.set_margin_top(self.default_margin)
        check.set_margin_bottom(self.default_margin)
        check.set_margin_start(self.default_margin)
        check.set_margin_end(self.default_margin)
        self.connect_rows.append(
            partial(check.connect, base_const.CONNECT_TOGGLED, self.on_widget_changed))
        return check

    def _on_change_scale(self, scale, *args):
        entry: Entry = args[0]
        min_value = args[1]
        max_value = args[2]

        value = scale.get_value()
        value_in_range = min(max(value, min_value), max_value)

        if value != value_in_range:
            scale.disconnect_by_func(self._on_change_scale)
            scale.set_value(value_in_range)
            scale.connect(base_const.CONNECT_VALUE_CHANGED, self._on_change_scale, entry, min_value,
                          max_value)

        entry.disconnect_by_func(self._on_change_scale_entry)
        entry.set_text(str(int(value)))
        entry.connect(base_const.CONNECT_CHANGED, self._on_change_scale_entry, scale, min_value,
                      max_value)

    def _on_change_scale_entry(self, entry, *args):
        scale: Scale = args[0]
        min_value = args[1]
        max_value = args[2]

        text = entry.get_text()
        # remove all non-digits
        text_digits = ''.join([char for char in text if char.isdigit()])

        if not text_digits:
            text_digits = min_value

        value = int(text_digits)
        value_in_range = min(max(value, min_value), max_value)

        if text != str(value_in_range):
            entry.disconnect_by_func(self._on_change_scale_entry)
            entry.set_text(str(value_in_range))
            entry.connect(base_const.CONNECT_CHANGED, self._on_change_scale_entry, scale, min_value,
                          max_value)

        scale.disconnect_by_func(self._on_change_scale)
        scale.set_value(value_in_range)
        scale.connect(base_const.CONNECT_VALUE_CHANGED, self._on_change_scale, entry, min_value,
                      max_value)

    def _is_number(self, value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False
