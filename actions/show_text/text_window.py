"""
The module for the Home Assistant customization text window.
"""

from functools import partial
from typing import Callable

from HomeAssistantPlugin.actions import const as base_const
from HomeAssistantPlugin.actions.cores.customization_core import customization_helper
from HomeAssistantPlugin.actions.cores.customization_core.customization_window import CustomizationWindow
from HomeAssistantPlugin.actions.show_text import text_const
from HomeAssistantPlugin.actions.show_text.text_customization import TextCustomization
from gi.repository.Gtk import StringObject


class TextWindow(CustomizationWindow):
    """
    Window to customize text.
    """

    def __init__(self, lm, attributes: list, callback: Callable,
                 current: TextCustomization = None, index: int = None):
        # add text_length to attributes
        attributes.insert(0, text_const.CUSTOM_TEXT_LENGTH)

        super().__init__(lm, attributes, callback, current, index)

        self.set_title(lm.get(text_const.CUSTOMIZATION_WINDOW_TITLE))

        #
        # check buttons
        #

        self.check_position = self._create_check_button()
        self.check_text_attribute = self._create_check_button()
        self.check_round = self._create_check_button()
        self.check_precision = self._create_check_button()
        self.check_text_size = self._create_check_button()
        self.check_text_color = self._create_check_button()
        self.check_outline_size = self._create_check_button()
        self.check_outline_color = self._create_check_button()
        self.check_show_unit = self._create_check_button()
        self.check_line_break = self._create_check_button()

        #
        # labels
        #

        label_position = self._create_label(self.lm.get(text_const.LABEL_POSITION))
        label_text_attribute = self._create_label(self.lm.get(text_const.LABEL_ATTRIBUTE))
        label_round = self._create_label(self.lm.get(text_const.LABEL_ROUND))
        label_precision = self._create_label(self.lm.get(text_const.LABEL_ROUND_PRECISION))
        label_text_size = self._create_label(self.lm.get(text_const.LABEL_TEXT_SIZE))
        label_text_color = self._create_label(self.lm.get(text_const.LABEL_TEXT_COLOR))
        label_outline_size = self._create_label(self.lm.get(text_const.LABEL_OUTLINE_SIZE))
        label_outline_color = self._create_label(self.lm.get(text_const.LABEL_OUTLINE_COLOR))
        label_show_unit = self._create_label(self.lm.get(text_const.LABEL_SHOW_UNIT_SHORT))
        label_line_break = self._create_label(self.lm.get(text_const.LABEL_UNIT_LINE_BREAK_SHORT))

        #
        # widgets
        #

        positions = [text_const.POSITION_TOP, text_const.POSITION_CENTER,
                     text_const.POSITION_BOTTOM]
        self.position = self._create_drop_down(positions, self.check_position)

        attributes = [text_const.CUSTOM_CUSTOM_TEXT]
        attributes.extend(self.attributes)
        self.attribute = self._create_drop_down(attributes, self.check_text_attribute)
        self.connect_rows.append(
            partial(self.attribute.connect, base_const.CONNECT_NOTIFY_SELECTED_ITEM,
                    self._on_change_attribute))
        self.custom_text = self._create_entry(None)

        self.round = self._create_switch(self.check_round)

        self.precision = self._create_scale(text_const.ROUND_MIN_PRECISION,
                                            text_const.ROUND_MAX_PRECISION, 1,
                                            self.check_precision)

        self.precision_entry = self._create_scale_entry(self.check_precision)
        self.precision_entry.set_hexpand(True)

        self.connect_rows.append(
            partial(self.precision.connect, base_const.CONNECT_VALUE_CHANGED,
                    self._on_change_scale, self.precision_entry, text_const.ROUND_MIN_PRECISION,
                    text_const.ROUND_MAX_PRECISION))
        self.connect_rows.append(
            partial(self.precision_entry.connect, base_const.CONNECT_CHANGED,
                    self._on_change_scale_entry, self.precision,
                    text_const.ROUND_MIN_PRECISION,
                    text_const.ROUND_MAX_PRECISION))

        self.text_size = self._create_scale(text_const.TEXT_MIN_SIZE,
                                            text_const.TEXT_MAX_SIZE, 1, self.check_text_size)

        self.text_size_entry = self._create_scale_entry(self.check_text_size)

        self.connect_rows.append(
            partial(self.text_size.connect, base_const.CONNECT_VALUE_CHANGED,
                    self._on_change_scale, self.text_size_entry, text_const.TEXT_MIN_SIZE,
                    text_const.TEXT_MAX_SIZE))
        self.connect_rows.append(
            partial(self.text_size_entry.connect, base_const.CONNECT_CHANGED,
                    self._on_change_scale_entry, self.text_size, text_const.TEXT_MIN_SIZE,
                    text_const.TEXT_MAX_SIZE))

        self.text_color = self._create_color_button(self.check_text_color)

        self.outline_size = self._create_scale(text_const.OUTLINE_MIN_SIZE,
                                               text_const.OUTLINE_MAX_SIZE, 1,
                                               self.check_outline_size)

        self.outline_size_entry = self._create_scale_entry(self.check_outline_size)

        self.connect_rows.append(
            partial(self.outline_size.connect, base_const.CONNECT_VALUE_CHANGED,
                    self._on_change_scale, self.outline_size_entry, text_const.OUTLINE_MIN_SIZE,
                    text_const.OUTLINE_MAX_SIZE))
        self.connect_rows.append(
            partial(self.outline_size_entry.connect, base_const.CONNECT_CHANGED,
                    self._on_change_scale_entry, self.outline_size,
                    text_const.OUTLINE_MIN_SIZE,
                    text_const.OUTLINE_MAX_SIZE))

        self.outline_color = self._create_color_button(self.check_outline_color)

        self.show_unit = self._create_switch(self.check_show_unit)

        self.show_line_break = self._create_switch(self.check_line_break)

        #
        # add to ui
        #

        self.grid_fields.attach(self.check_position, 2, 2, 1, 1)
        self.grid_fields.attach(label_position, 3, 2, 1, 1)
        self.grid_fields.attach(self.position, 4, 2, 1, 1)

        self.grid_fields.attach(self.check_text_attribute, 2, 3, 1, 1)
        self.grid_fields.attach(label_text_attribute, 3, 3, 1, 1)
        self.grid_fields.attach(self.attribute, 4, 3, 1, 1)
        self.grid_fields.attach(self.custom_text, 5, 3, 1, 1)

        self.grid_fields.attach(self.check_round, 2, 4, 1, 1)
        self.grid_fields.attach(label_round, 3, 4, 1, 1)
        self.grid_fields.attach(self.round, 4, 4, 1, 1)

        self.grid_fields.attach(self.check_precision, 2, 5, 1, 1)
        self.grid_fields.attach(label_precision, 3, 5, 1, 1)
        self.grid_fields.attach(self.precision, 4, 5, 1, 1)
        self.grid_fields.attach(self.precision_entry, 5, 5, 1, 1)

        self.grid_fields.attach(self.check_text_size, 2, 6, 1, 1)
        self.grid_fields.attach(label_text_size, 3, 6, 1, 1)
        self.grid_fields.attach(self.text_size, 4, 6, 1, 1)
        self.grid_fields.attach(self.text_size_entry, 5, 6, 1, 1)

        self.grid_fields.attach(self.check_text_color, 2, 7, 1, 1)
        self.grid_fields.attach(label_text_color, 3, 7, 1, 1)
        self.grid_fields.attach(self.text_color, 4, 7, 1, 1)

        self.grid_fields.attach(self.check_outline_size, 2, 8, 1, 1)
        self.grid_fields.attach(label_outline_size, 3, 8, 1, 1)
        self.grid_fields.attach(self.outline_size, 4, 8, 1, 1)
        self.grid_fields.attach(self.outline_size_entry, 5, 8, 1, 1)

        self.grid_fields.attach(self.check_outline_color, 2, 9, 1, 1)
        self.grid_fields.attach(label_outline_color, 3, 9, 1, 1)
        self.grid_fields.attach(self.outline_color, 4, 9, 1, 1)

        self.grid_fields.attach(self.check_show_unit, 2, 10, 1, 1)
        self.grid_fields.attach(label_show_unit, 3, 10, 1, 1)
        self.grid_fields.attach(self.show_unit, 4, 10, 1, 1)

        self.grid_fields.attach(self.check_line_break, 2, 11, 1, 1)
        self.grid_fields.attach(label_line_break, 3, 11, 1, 1)
        self.grid_fields.attach(self.show_line_break, 4, 11, 1, 1)

        self._after_init()

    def _on_change_attribute(self, *_, **__) -> None:
        custom_text_visible = self.attribute.get_selected_item().get_string() == text_const.CUSTOM_CUSTOM_TEXT
        self.custom_text.set_visible(custom_text_visible)

    def set_default_values(self) -> None:
        super().set_default_values()

        for index, entry in enumerate(self.position.get_model()):
            if entry.get_string() == text_const.DEFAULT_POSITION:
                self.position.set_selected(index)
                break

        for index, entry in enumerate(self.attribute.get_model()):
            if entry.get_string() == text_const.DEFAULT_ATTRIBUTE:
                self.attribute.set_selected(index)
                break

        self.custom_text.set_text(text_const.DEFAULT_CUSTOM_TEXT)
        self.custom_text.set_visible(False)
        self.round.set_active(text_const.DEFAULT_ROUND)
        self.precision.set_value(text_const.DEFAULT_ROUND_PRECISION)
        self.precision_entry.set_text(str(text_const.DEFAULT_ROUND_PRECISION))
        self.text_size.set_value(text_const.DEFAULT_TEXT_SIZE)
        self.text_size_entry.set_text(str(text_const.DEFAULT_TEXT_SIZE))

        text_rgba = customization_helper.convert_color_list_to_rgba(text_const.DEFAULT_TEXT_COLOR)
        self.text_color.set_rgba(text_rgba)

        self.outline_size.set_value(text_const.DEFAULT_OUTLINE_SIZE)
        self.outline_size_entry.set_text(str(text_const.DEFAULT_OUTLINE_SIZE))

        outline_rgba = customization_helper.convert_color_list_to_rgba(text_const.DEFAULT_OUTLINE_COLOR)
        self.outline_color.set_rgba(outline_rgba)

        self.show_unit.set_active(text_const.DEFAULT_SHOW_UNIT)

        self.show_line_break.set_active(text_const.DEFAULT_UNIT_LINE_BREAK)

    def set_current_values(self) -> None:
        if not self.current:
            return

        super().set_current_values()

        for index, entry in enumerate(self.position.get_model()):
            if entry.get_string() == self.current.get_position():
                self.position.set_selected(index)
                break
        self.check_position.set_active(self.current.get_position() is not None)

        for index, entry in enumerate(self.attribute.get_model()):
            if entry.get_string() == self.current.get_text_attribute():
                self.attribute.set_selected(index)
                break
        self.check_text_attribute.set_active(self.current.get_text_attribute() is not None)

        self.custom_text.set_text(
            self.current.get_custom_text() or text_const.DEFAULT_CUSTOM_TEXT)
        self.custom_text.set_visible(
            self.current.get_custom_text() is not None)

        self.round.set_active(self.current.get_round() or text_const.DEFAULT_ROUND)
        self.check_round.set_active(self.current.get_round() is not None)

        self.precision.set_value(
            self.current.get_round_precision() or text_const.DEFAULT_ROUND_PRECISION)
        self.precision_entry.set_text(
            str(self.current.get_round_precision() or text_const.DEFAULT_ROUND_PRECISION))
        self.check_precision.set_active(self.current.get_round_precision() is not None)

        self.text_size.set_value(
            self.current.get_text_size() or text_const.DEFAULT_TEXT_SIZE)
        self.text_size_entry.set_text(
            str(self.current.get_text_size() or text_const.DEFAULT_TEXT_SIZE))
        self.check_text_size.set_active(self.current.get_text_size() is not None)

        if self.current.get_text_color():
            text_rgba = customization_helper.convert_color_list_to_rgba(self.current.get_text_color())
            self.text_color.set_rgba(text_rgba)
        self.check_text_color.set_active(self.current.get_text_color() is not None)

        self.outline_size.set_value(
            self.current.get_outline_size() or text_const.DEFAULT_OUTLINE_SIZE)
        self.outline_size_entry.set_text(
            str(self.current.get_outline_size() or text_const.DEFAULT_OUTLINE_SIZE))
        self.check_outline_size.set_active(self.current.get_outline_size() is not None)

        if self.current.get_outline_color():
            outline_rgba = customization_helper.convert_color_list_to_rgba(
                self.current.get_outline_color())
            self.outline_color.set_rgba(outline_rgba)
        self.check_outline_color.set_active(self.current.get_outline_color() is not None)

        self.show_unit.set_active(
            self.current.get_show_unit() or text_const.DEFAULT_SHOW_UNIT)
        self.check_show_unit.set_active(self.current.get_show_unit() is not None)

        self.show_line_break.set_active(
            self.current.get_line_break() or text_const.DEFAULT_UNIT_LINE_BREAK)
        self.check_line_break.set_active(self.current.get_line_break() is not None)

    def on_add_button(self, *_, **__) -> None:
        if not super().on_add_button():
            return

        if self.check_position.get_active() and self.position.get_selected() < 0:
            self.position.add_css_class(text_const.ERROR)
            return

        if self.check_text_attribute.get_active() and self.attribute.get_selected() < 0:
            self.attribute.add_css_class(text_const.ERROR)
            return

        if (not self.check_position.get_active() and not self.check_text_attribute.get_active()
                and not self.check_round.get_active() and not self.check_precision.get_active()
                and not self.check_text_size.get_active() and not self.check_text_color.get_active()
                and not self.check_outline_size.get_active() and not
                self.check_outline_color.get_active()
                and not self.check_show_unit.get_active() and not
                self.check_line_break.get_active()):
            self.check_position.add_css_class(text_const.ERROR)
            self.check_text_attribute.add_css_class(text_const.ERROR)
            self.check_round.add_css_class(text_const.ERROR)
            self.check_precision.add_css_class(text_const.ERROR)
            self.check_text_size.add_css_class(text_const.ERROR)
            self.check_text_color.add_css_class(text_const.ERROR)
            self.check_outline_size.add_css_class(text_const.ERROR)
            self.check_outline_color.add_css_class(text_const.ERROR)
            self.check_show_unit.add_css_class(text_const.ERROR)
            self.check_line_break.add_css_class(text_const.ERROR)
            return

        attribute = self.condition_attribute.get_selected_item().get_string()
        value = self.entry_value.get_text()

        if attribute == text_const.CUSTOM_TEXT_LENGTH and not self._is_number(value):
            # operator needs a number
            self.operator.add_css_class(text_const.ERROR)
            self.entry_value.add_css_class(text_const.ERROR)
            return

        text_attribute = \
            self.attribute.get_selected_item().get_string() if self.check_text_attribute.get_active() else None
        position = self.position.get_selected_item().get_string() if self.check_position.get_active() else None
        custom_text = self.custom_text.get_text() \
            if (self.check_text_attribute.get_active() and
                self.attribute.get_selected_item().get_string()
                == text_const.CUSTOM_CUSTOM_TEXT) else None
        text_round = self.round.get_active() if self.check_round.get_active() else None
        precision = int(
            self.precision.get_value()) if self.check_precision.get_active() else None
        text_size = int(
            self.text_size.get_value()) if self.check_text_size.get_active() else None
        text_color = self.text_color.get_rgba() if self.check_text_color.get_active() else \
            None
        text_color_list = customization_helper.convert_rgba_to_color_list(text_color) if text_color else None
        outline_size = int(
            self.outline_size.get_value()) if self.check_outline_size.get_active() else None
        outline_color = self.outline_color.get_rgba() if (
            self.check_outline_color.get_active()) else None
        outline_color_list = customization_helper.convert_rgba_to_color_list(outline_color) if outline_color else None
        show_unit = self.show_unit.get_active() if self.check_show_unit.get_active() else \
            None
        line_break = self.show_line_break.get_active() if self.check_line_break.get_active() \
            else None

        self.callback(TextCustomization(
            attribute=attribute,
            operator=self.operator.get_selected_item().value,
            value=value,
            position=position, text_attribute=text_attribute, custom_text=custom_text,
            do_round=text_round, round_precision=precision,
            text_size=text_size, text_color=text_color_list, outline_size=outline_size,
            outline_color=outline_color_list, show_unit=show_unit, line_break=line_break),
            index=self.index)

        self.destroy()

    def on_widget_changed(self, *_, **__):
        super().on_widget_changed()

        self.check_position.remove_css_class(text_const.ERROR)
        self.position.remove_css_class(text_const.ERROR)
        self.check_text_attribute.remove_css_class(text_const.ERROR)
        self.attribute.remove_css_class(text_const.ERROR)
        self.custom_text.remove_css_class(text_const.ERROR)
        self.check_round.remove_css_class(text_const.ERROR)
        self.check_precision.remove_css_class(text_const.ERROR)
        self.check_text_size.remove_css_class(text_const.ERROR)
        self.check_show_unit.remove_css_class(text_const.ERROR)
        self.check_line_break.remove_css_class(text_const.ERROR)
