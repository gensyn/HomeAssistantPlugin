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
from HomeAssistantPlugin.actions.cores.customization_core.condition import Condition
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


class ConditionRow:
    """
    An additional condition that is combined with the preceding conditions using "and" or "or".
    """

    def __init__(self, window: "CustomizationWindow", condition: Condition = None):
        self.window = window

        self.logic = window.create_drop_down_items([
            DropDownItem(customization_const.AND, window.lm.get(customization_const.LABEL_CUSTOMIZATION_AND)),
            DropDownItem(customization_const.OR, window.lm.get(customization_const.LABEL_CUSTOMIZATION_OR)),
        ])
        self.entity = window.create_entity_drop_down()
        self.attribute = window.create_string_drop_down([])
        self.operator = window.create_drop_down_items(window.build_operator_items())
        self.entry_value = Entry()
        self.entry_value.set_margin_top(window.default_margin)
        self.entry_value.set_margin_bottom(window.default_margin)
        self.entry_value.set_margin_start(window.default_margin)
        self.entry_value.set_margin_end(window.default_margin)
        self.entry_value.set_hexpand(True)

        self.remove_button = Button(icon_name="list-remove")
        self.remove_button.set_valign(Align.CENTER)
        self.remove_button.set_tooltip_text(window.lm.get(customization_const.LABEL_CUSTOMIZATION_REMOVE_CONDITION))
        self.remove_button.set_margin_start(window.default_margin)
        self.remove_button.set_margin_end(window.default_margin)

        self.box = Box(orientation=Orientation.HORIZONTAL)
        for widget in (self.logic, self.entity, self.attribute, self.operator, self.entry_value, self.remove_button):
            self.box.append(widget)

        self.refresh_attributes()
        self.logic.set_selected(0)
        self.operator.set_selected(0)

        if condition is not None:
            self._set_condition(condition)

        self.entity.connect(base_const.CONNECT_NOTIFY_SELECTED_ITEM, self._on_entity_changed)
        for widget in (self.logic, self.attribute, self.operator):
            widget.connect(base_const.CONNECT_NOTIFY_SELECTED_ITEM, window.on_widget_changed)
        self.entry_value.connect(base_const.CONNECT_CHANGED, window.on_widget_changed)
        self.entry_value.connect(base_const.CONNECT_ACTIVATE, window.on_add_button)
        self.remove_button.connect(base_const.CONNECT_CLICKED, self._on_remove)

    def _set_condition(self, condition: Condition) -> None:
        window = self.window
        window.select_item(self.logic, condition.logic)
        window.select_item(self.entity, condition.entity or customization_const.EMPTY_STRING)
        self.refresh_attributes(condition.attribute)
        window.select_item(self.operator, condition.operator)
        self.entry_value.set_text(condition.value)

    def refresh_attributes(self, selected: str = None) -> None:
        """
        Load the attributes of the selected entity.
        :param selected: the attribute to select; the first attribute is selected if not available
        """
        entity = self.window.get_selected_value(self.entity)
        attributes = self.window.get_attributes_for_entity(entity)
        model = ListStore()
        for attribute in attributes:
            model.append(StringObject.new(attribute))
        self.attribute.set_model(model)
        self.attribute.set_selected(attributes.index(selected) if selected in attributes else 0)

    def _on_entity_changed(self, *_) -> None:
        previous = self.attribute.get_selected_item()
        self.refresh_attributes(previous.get_string() if previous is not None else None)

    def _on_remove(self, *_) -> None:
        self.window.remove_condition_row(self)

    def get_condition(self) -> Condition:
        """
        Get the condition as configured in the UI.
        """
        return Condition(
            attribute=self.attribute.get_selected_item().get_string(),
            operator=self.operator.get_selected_item().value,
            value=self.entry_value.get_text(),
            entity=self.window.get_selected_value(self.entity) or None,
            logic=self.logic.get_selected_item().value
        )

    def validate(self) -> bool:
        """
        Check whether the condition is valid and mark invalid fields.
        """
        if self.attribute.get_selected() < 0:
            self.attribute.add_css_class(customization_const.ERROR)
            return False

        if self.operator.get_selected() < 0:
            self.operator.add_css_class(customization_const.ERROR)
            return False

        if not self.entry_value.get_text():
            self.entry_value.add_css_class(customization_const.ERROR)
            return False

        if self.operator.get_selected() > 1 and not self.window._is_number(self.entry_value.get_text()):
            # operator needs a number
            self.operator.add_css_class(customization_const.ERROR)
            self.entry_value.add_css_class(customization_const.ERROR)
            return False

        return True

    def clear_errors(self) -> None:
        """
        Remove the error marks from all fields.
        """
        for widget in (self.attribute, self.operator, self.entry_value):
            widget.remove_css_class(customization_const.ERROR)


class CustomizationWindow(Window):
    """
    Base for customization windows
    """
    callback: Callable

    connect_rows: list = []
    default_margin = 3

    def __init__(self, lm, attributes: list, callback: Callable,
                 current: Customization = None, index: int = None,
                 entities: list[str] = None, get_attributes: Callable[[str], list[str]] = None):
        super().__init__()
        self.callback = callback
        self.lm = lm
        self.index: int = index
        self.attributes: list[str] = attributes
        self.current: Customization = current
        self.entities: list[str] = entities or []
        self.get_attributes: Callable[[str], list[str]] = get_attributes
        self.condition_rows: list[ConditionRow] = []

        self.set_modal(True)

        label_attribute = self._create_label(lm.get(customization_const.LABEL_CUSTOMIZATION_ATTRIBUTE))
        label_operator = self._create_label(lm.get(customization_const.LABEL_CUSTOMIZATION_OPERATOR))
        label_value = self._create_label(lm.get(customization_const.LABEL_CUSTOMIZATION_VALUE))
        label_if = self._create_label(lm.get(customization_const.LABEL_CUSTOMIZATION_IF))
        label_entity = self._create_label(lm.get(customization_const.LABEL_CUSTOMIZATION_ENTITY))

        self.condition_entity = self.create_entity_drop_down()
        self.condition_entity.connect(base_const.CONNECT_NOTIFY_SELECTED_ITEM, self._on_condition_entity_changed)
        self.condition_attribute = self._create_drop_down(self.attributes)
        self.operator = self.create_drop_down_items(self.build_operator_items())
        self.connect_rows.append(
            partial(self.operator.connect, base_const.CONNECT_NOTIFY_SELECTED_ITEM, self.on_widget_changed))

        self.entry_value = self._create_entry()

        cancel_button = self._create_button(lm.get(customization_const.LABEL_CUSTOMIZATION_CANCEL))
        self.connect_rows.append(
            partial(cancel_button.connect, base_const.CONNECT_CLICKED, self._on_cancel_button))

        add_label = lm.get(customization_const.LABEL_CUSTOMIZATION_ADD) if not current else lm.get(
            customization_const.LABEL_CUSTOMIZATION_UPDATE)
        add_button = self._create_button(add_label)
        self.connect_rows.append(
            partial(add_button.connect, base_const.CONNECT_CLICKED, self.on_add_button))

        label_entity.set_margin_top(15)
        label_attribute.set_margin_top(15)
        label_operator.set_margin_top(15)
        label_value.set_margin_top(15)
        cancel_button.set_margin_bottom(15)
        add_button.set_margin_bottom(15)
        add_button.set_margin_end(15)
        label_if.set_margin_start(15)
        self.entry_value.set_margin_end(15)

        self.grid_condition = Grid()
        self.grid_condition.attach(label_entity, 1, 0, 1, 1)
        self.grid_condition.attach(label_attribute, 2, 0, 1, 1)
        self.grid_condition.attach(label_operator, 3, 0, 1, 1)
        self.grid_condition.attach(label_value, 4, 0, 1, 1)
        self.grid_condition.attach(label_if, 0, 1, 1, 1)
        self.grid_condition.attach(self.condition_entity, 1, 1, 1, 1)
        self.grid_condition.attach(self.condition_attribute, 2, 1, 1, 1)
        self.grid_condition.attach(self.operator, 3, 1, 1, 1)
        self.grid_condition.attach(self.entry_value, 4, 1, 1, 1)

        self.box_conditions = Box(orientation=Orientation.VERTICAL)
        self.box_conditions.set_margin_start(15)
        self.box_conditions.set_margin_end(15)

        add_condition_button = self._create_button(lm.get(customization_const.LABEL_CUSTOMIZATION_ADD_CONDITION))
        add_condition_button.set_halign(Align.START)
        add_condition_button.set_margin_start(15)
        add_condition_button.set_margin_bottom(30)
        self.connect_rows.append(
            partial(add_condition_button.connect, base_const.CONNECT_CLICKED, self._on_add_condition_button))

        self.grid_fields = Grid()

        box_buttons = Box()
        box_buttons.append(cancel_button)
        box_buttons.append(add_button)
        box_buttons.set_halign(Align.END)

        grid = Grid()
        grid.attach(self.grid_condition, 0, 0, 1, 1)
        grid.attach(self.box_conditions, 0, 1, 1, 1)
        grid.attach(add_condition_button, 0, 2, 1, 1)
        grid.attach(self.grid_fields, 0, 3, 1, 1)
        grid.attach(box_buttons, 0, 4, 1, 1)

        self.set_child(grid)

    def _after_init(self) -> None:
        self.set_default_values()
        self.set_current_values()
        self._connect_rows()

    def set_default_values(self) -> None:
        self.condition_entity.set_selected(0)
        self.condition_attribute.set_selected(0)
        self.operator.set_selected(0)

    def set_current_values(self) -> None:
        if not self.current:
            return

        self.select_item(self.condition_entity, self.current.get_entity() or customization_const.EMPTY_STRING)

        for index, entry in enumerate(self.condition_attribute.get_model()):
            if entry.get_string() == self.current.get_attribute():
                self.condition_attribute.set_selected(index)
                break

        for index, entry in enumerate(self.operator.get_model()):
            if entry.value == self.current.get_operator():
                self.operator.set_selected(index)
                break

        self.entry_value.set_text(self.current.get_value())

        for condition in self.current.get_conditions():
            self._add_condition_row(condition)

    def _create_button(self, label) -> Button:
        button = Button(label=label)
        button.set_margin_top(self.default_margin)
        button.set_margin_bottom(self.default_margin)
        button.set_margin_start(self.default_margin)
        button.set_margin_end(self.default_margin)
        return button

    def create_string_drop_down(self, attributes: list) -> DropDown:
        """
        Create a drop down that shows strings.
        """
        drop_down = DropDown()
        drop_down.set_margin_top(self.default_margin)
        drop_down.set_margin_bottom(self.default_margin)
        drop_down.set_margin_start(self.default_margin)
        drop_down.set_margin_end(self.default_margin)

        model = ListStore()
        for option in attributes:
            model.append(StringObject.new(option))

        drop_down.set_model(model)

        return drop_down

    def _create_drop_down(self, attributes: list, check: CheckButton = None) -> DropDown:
        drop_down = self.create_string_drop_down(attributes)

        self.connect_rows.append(
            partial(drop_down.connect, base_const.CONNECT_NOTIFY_SELECTED_ITEM, self.on_widget_changed))

        if check is not None:
            self.connect_rows.append(partial(drop_down.connect, base_const.CONNECT_NOTIFY_SELECTED_ITEM,
                                             lambda _=None, __=None: check.set_active(drop_down.get_selected() >= 0)))

        return drop_down

    def build_operator_items(self) -> list[DropDownItem]:
        """
        Build the items for the operator drop downs.
        """
        return [DropDownItem(operator, self.lm.get(customization_const.LABEL_CUSTOMIZATION_OPERATORS[operator]))
                for operator in ("==", "!=", "<", "<=", ">", ">=")]

    def create_drop_down_items(self, items: list[DropDownItem], enable_search: bool = False) -> DropDown:
        """
        Create a drop down that shows the labels of the items.
        """
        expression = PropertyExpression.new(DropDownItem, None, "label")

        drop_down = DropDown(expression=expression)
        drop_down.set_margin_top(self.default_margin)
        drop_down.set_margin_bottom(self.default_margin)
        drop_down.set_margin_start(self.default_margin)
        drop_down.set_margin_end(self.default_margin)
        drop_down.set_enable_search(enable_search)

        model = ListStore()
        for item in items:
            model.append(item)

        drop_down.set_model(model)

        return drop_down

    def create_entity_drop_down(self) -> DropDown:
        """
        Create a drop down to select the entity that a condition refers to.
        The first item is the entity of the action.
        """
        items = [DropDownItem(customization_const.EMPTY_STRING,
                              self.lm.get(customization_const.LABEL_CUSTOMIZATION_THIS_ENTITY))]
        items.extend(DropDownItem(entity, entity) for entity in self.entities)
        return self.create_drop_down_items(items, enable_search=True)

    @staticmethod
    def get_selected_value(drop_down: DropDown) -> str:
        """
        Get the value of the selected item of a drop down with DropDownItems.
        """
        item = drop_down.get_selected_item()
        return item.value if item is not None else customization_const.EMPTY_STRING

    @staticmethod
    def select_item(drop_down: DropDown, value: str) -> None:
        """
        Select the item with the value in a drop down with DropDownItems.
        """
        for index, entry in enumerate(drop_down.get_model()):
            if entry.value == value:
                drop_down.set_selected(index)
                break

    def get_attributes_for_entity(self, entity: str) -> list[str]:
        """
        Get the attributes that can be used in a condition for an entity.
        :param entity: the entity or an empty value for the entity of the action
        """
        if not entity:
            return self.attributes
        if self.get_attributes is None:
            return [customization_const.STATE]
        return self.get_attributes(entity)

    def _refresh_condition_attributes(self, selected: str = None) -> None:
        attributes = self.get_attributes_for_entity(self.get_selected_value(self.condition_entity))
        model = ListStore()
        for attribute in attributes:
            model.append(StringObject.new(attribute))
        self.condition_attribute.set_model(model)
        self.condition_attribute.set_selected(attributes.index(selected) if selected in attributes else 0)

    def _on_condition_entity_changed(self, *_) -> None:
        previous = self.condition_attribute.get_selected_item()
        self._refresh_condition_attributes(previous.get_string() if previous is not None else None)

    def _add_condition_row(self, condition: Condition = None) -> None:
        row = ConditionRow(self, condition)
        self.condition_rows.append(row)
        self.box_conditions.append(row.box)

    def remove_condition_row(self, row: ConditionRow) -> None:
        """
        Remove an additional condition.
        """
        self.condition_rows.remove(row)
        self.box_conditions.remove(row.box)

    def _on_add_condition_button(self, *_) -> None:
        self._add_condition_row()

    def get_condition_kwargs(self) -> dict:
        """
        Get the condition as configured in the UI as keyword arguments for a customization.
        """
        return {
            "attribute": self.condition_attribute.get_selected_item().get_string(),
            "operator": self.operator.get_selected_item().value,
            "value": self.entry_value.get_text(),
            "entity": self.get_selected_value(self.condition_entity) or None,
            "conditions": [row.get_condition() for row in self.condition_rows],
        }

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

        return all([row.validate() for row in self.condition_rows])

    def on_widget_changed(self, *_, **__) -> None:
        self.condition_attribute.remove_css_class(customization_const.ERROR)
        self.operator.remove_css_class(customization_const.ERROR)
        self.entry_value.remove_css_class(customization_const.ERROR)
        for row in self.condition_rows:
            row.clear_errors()

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
