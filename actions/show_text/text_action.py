"""
The module for the Home Assistant action that is loaded in StreamController.
"""
from collections import Counter
from typing import List

from GtkHelper.GenerativeUI.ColorButtonRow import ColorButtonRow
from GtkHelper.GenerativeUI.ComboRow import ComboRow
from GtkHelper.GenerativeUI.ExpanderRow import ExpanderRow
from GtkHelper.GenerativeUI.ScaleRow import ScaleRow
from GtkHelper.GenerativeUI.SwitchRow import SwitchRow
from HomeAssistantPlugin.actions.cores.base_core.base_core import requires_initialization
from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.cores.customization_core.customization_core import CustomizationCore
from HomeAssistantPlugin.actions.show_text import text_const
from HomeAssistantPlugin.actions.show_text import text_helper
from HomeAssistantPlugin.actions.show_text.text_customization import TextCustomization
from HomeAssistantPlugin.actions.show_text.text_row import TextRow
from HomeAssistantPlugin.actions.show_text.text_settings import ShowTextSettings
from HomeAssistantPlugin.actions.show_text.text_window import TextWindow


class ShowText(CustomizationCore):
    """Action to be loaded by StreamController."""

    def __init__(self, *args, **kwargs):
        super().__init__(window_implementation=TextWindow, customization_implementation=TextCustomization,
                         row_implementation=TextRow, settings_implementation=ShowTextSettings, track_entity=True, *args, **kwargs)

    def get_config_rows(self) -> List:
        """Get the rows to be displayed in the UI."""
        return [self.domain_combo.widget, self.entity_combo.widget, self.position.widget, self.attribute.widget,
                self.round.widget, self.text_size.widget, self.text_color.widget,
                self.outline_size.widget, self.outline_color.widget, self.show_unit.widget, self.unit_line_break.widget,
                self.customization_expander.widget]

    def _create_ui_elements(self) -> None:
        """Get all action rows."""
        super()._create_ui_elements()

        # Text position
        text_position_model = [
            text_const.POSITION_TOP, text_const.POSITION_CENTER, text_const.POSITION_BOTTOM
        ]

        self.position: ComboRow = ComboRow(
            self, text_const.SETTING_TEXT_POSITION, text_const.POSITION_CENTER,
            text_position_model, title=text_const.LABEL_POSITION,
            on_change=self._reload, can_reset=False, complex_var_name=True
        )

        # Text attribute
        self.attribute: ComboRow = ComboRow(
            self, text_const.SETTING_TEXT_ATTRIBUTE, text_const.DEFAULT_ATTRIBUTE,
            [], title=text_const.LABEL_ATTRIBUTE, on_change=self._reload,
            can_reset=False, complex_var_name=True
        )

        # Text round
        self.round: ExpanderRow = ExpanderRow(
            self, text_const.SETTING_TEXT_ROUND, text_const.DEFAULT_ROUND,
            title=text_const.LABEL_ROUND, show_enable_switch=True,
            on_change=self._reload, can_reset=False, complex_var_name=True
        )

        # Text round precision
        self.round_precision: ScaleRow = ScaleRow(
            self, text_const.SETTING_TEXT_ROUND_PRECISION, text_const.DEFAULT_ROUND_PRECISION,
            text_const.ROUND_MIN_PRECISION, text_const.ROUND_MAX_PRECISION,
            title=text_const.LABEL_ROUND, step=1, digits=0,
            on_change=self._reload, can_reset=False, complex_var_name=True
        )

        self.round.add_row(self.round_precision.widget)

        # Text size
        self.text_size: ScaleRow = ScaleRow(
            self, text_const.SETTING_TEXT_TEXT_SIZE, text_const.DEFAULT_TEXT_SIZE,
            text_const.TEXT_MIN_SIZE, text_const.TEXT_MAX_SIZE,
            title=text_const.LABEL_TEXT_SIZE, step=1, digits=0,
            on_change=self._reload, can_reset=False, complex_var_name=True
        )

        # Text color
        self.text_color: ColorButtonRow = ColorButtonRow(
            self, text_const.SETTING_TEXT_TEXT_COLOR, text_const.DEFAULT_TEXT_COLOR,
            title=text_const.LABEL_TEXT_COLOR, on_change=self._reload,
            can_reset=False, complex_var_name=True
        )

        # Text outline size
        self.outline_size: ScaleRow = ScaleRow(
            self, text_const.SETTING_TEXT_OUTLINE_SIZE, text_const.DEFAULT_OUTLINE_SIZE,
            text_const.OUTLINE_MIN_SIZE, text_const.OUTLINE_MAX_SIZE,
            title=text_const.LABEL_OUTLINE_SIZE, step=1, digits=0,
            on_change=self._reload, can_reset=False, complex_var_name=True
        )

        # Text outline color
        self.outline_color: ColorButtonRow = ColorButtonRow(
            self, text_const.SETTING_TEXT_OUTLINE_COLOR, text_const.DEFAULT_OUTLINE_COLOR,
            title=text_const.LABEL_OUTLINE_COLOR, on_change=self._reload,
            can_reset=False, complex_var_name=True
        )

        # Text show unit
        self.show_unit: SwitchRow = SwitchRow(
            self, text_const.SETTING_TEXT_SHOW_UNIT, text_const.DEFAULT_SHOW_UNIT,
            title=text_const.LABEL_SHOW_UNIT, on_change=self._reload,
            can_reset=False, complex_var_name=True
        )

        # Text unit line break
        self.unit_line_break: SwitchRow = SwitchRow(
            self, text_const.SETTING_TEXT_UNIT_LINE_BREAK, text_const.DEFAULT_UNIT_LINE_BREAK,
            title=text_const.LABEL_UNIT_LINE_BREAK, on_change=self._reload,
            can_reset=False, complex_var_name=True
        )

    @requires_initialization
    def _set_enabled_disabled(self) -> None:
        """
        Set the active/inactive state for all rows.
        """
        super()._set_enabled_disabled()

        domain = self.settings.get_domain()
        is_domain_set = bool(domain)

        entity = self.settings.get_entity()
        is_entity_set = bool(entity)

        if not is_domain_set or not is_entity_set:
            self.position.widget.set_sensitive(False)
            self.position.widget.set_subtitle(self.lm.get(text_const.LABEL_NO_ENTITY))

            self.attribute.widget.set_sensitive(False)
            self.attribute.widget.set_subtitle(self.lm.get(text_const.LABEL_NO_ENTITY))

            self.round.widget.set_sensitive(False)
            self.round.widget.set_subtitle(self.lm.get(text_const.LABEL_NO_ENTITY))

            self.round_precision.widget.set_sensitive(False)
            self.round_precision.widget.set_subtitle(self.lm.get(text_const.LABEL_NO_ENTITY))

            self.text_size.widget.set_sensitive(False)
            self.text_size.widget.set_subtitle(self.lm.get(text_const.LABEL_NO_ENTITY))

            self.text_color.widget.set_sensitive(False)
            self.text_color.widget.set_subtitle(self.lm.get(text_const.LABEL_NO_ENTITY))

            self.outline_size.widget.set_sensitive(False)
            self.outline_size.widget.set_subtitle(self.lm.get(text_const.LABEL_NO_ENTITY))

            self.outline_color.widget.set_sensitive(False)
            self.outline_color.widget.set_subtitle(self.lm.get(text_const.LABEL_NO_ENTITY))

            self.show_unit.widget.set_sensitive(False)
            self.show_unit.widget.set_subtitle(self.lm.get(text_const.LABEL_NO_ENTITY))

            self.unit_line_break.widget.set_sensitive(False)
            self.unit_line_break.widget.set_subtitle(self.lm.get(text_const.LABEL_NO_ENTITY))
        else:
            self.position.widget.set_sensitive(True)
            self.position.widget.set_subtitle(text_const.EMPTY_STRING)

            self.attribute.widget.set_sensitive(self.attribute.get_item_amount() > 1)
            self.attribute.widget.set_subtitle(text_const.EMPTY_STRING)

            self.round.widget.set_sensitive(True)
            self.round.widget.set_subtitle(text_const.EMPTY_STRING)

            self.round_precision.widget.set_sensitive(True)
            self.round_precision.widget.set_subtitle(text_const.EMPTY_STRING)

            self.text_size.widget.set_sensitive(True)
            self.text_size.widget.set_subtitle(text_const.EMPTY_STRING)

            self.text_color.widget.set_sensitive(True)
            self.text_color.widget.set_subtitle(text_const.EMPTY_STRING)

            self.outline_size.widget.set_sensitive(True)
            self.outline_size.widget.set_subtitle(text_const.EMPTY_STRING)

            self.outline_color.widget.set_sensitive(True)
            self.outline_color.widget.set_subtitle(text_const.EMPTY_STRING)

            self.show_unit.widget.set_subtitle(text_const.EMPTY_STRING)

            self.unit_line_break.widget.set_subtitle(text_const.EMPTY_STRING)

            ha_entity = self.plugin_base.backend.get_entity(self.settings.get_entity())
            has_unit = bool(
                ha_entity.get(customization_const.ATTRIBUTES, {}).get(customization_const.UNIT_OF_MEASUREMENT, False)
            )

            if has_unit:
                self.show_unit.widget.set_sensitive(True)
                self.unit_line_break.widget.set_sensitive(True)
            else:
                self.show_unit.set_active(False)
                self.show_unit.widget.set_sensitive(False)
                self.unit_line_break.set_active(False)
                self.unit_line_break.widget.set_sensitive(False)

            if not self.show_unit.get_active():
                self.unit_line_break.set_active(False)
                self.unit_line_break.widget.set_sensitive(False)

    @requires_initialization
    def _on_change_entity(self, _, entity, old_entity):
        self._load_attributes()
        super()._on_change_entity(_, entity, old_entity)

    def _load_attributes(self):
        attribute = self.settings.get_attribute()
        attributes = self._get_attributes()
        if attribute is not None and attribute not in attributes:
            attributes.append(attribute)
        if Counter(attributes) != Counter(self._get_current_attributes()):
            self.attribute.populate(attributes, attribute, trigger_callback=False)

    def _get_current_attributes(self) -> List[str]:
        """
        Gets the list of attributes set on the Combo as strings.
        :return: the list of attributes set on the Combo as strings
        """
        return [
            str(self.attribute.get_item_at(i))
            for i in range(self.attribute.get_item_amount())
        ]

    def refresh(self, state: dict = None) -> None:
        """
        Executed when an entity is updated to reflect the changes on the key.
        """
        self.set_top_label(text_const.EMPTY_STRING)
        self.set_center_label(text_const.EMPTY_STRING)
        self.set_bottom_label(text_const.EMPTY_STRING)

        if not self.initialized:
            if not self.plugin_base.backend.is_connected():
                text, position, text_size, text_color, outline_size, outline_color = text_helper.get_text(
                    state, self.settings, False)
                text_size, outline_size = self._get_sizes_adjusted_for_canvas(text_size, outline_size)
                self.set_label(
                    text, position, text_color, None, text_size, outline_size, outline_color,
                    None, None, True)
            return

        entity = self.settings.get_entity()

        if not entity:
            return

        # the attributes of the entity might have changed
        self._load_attributes()

        if state is None:
            state = self.plugin_base.backend.get_entity(entity)

        if state is None:
            return

        text, position, text_size, text_color, outline_size, outline_color = text_helper.get_text(
            state, self.settings, self.plugin_base.backend.is_connected()
        )
        text_size, outline_size = self._get_sizes_adjusted_for_canvas(text_size, outline_size)
        self.set_label(
            text, position, text_color, None, text_size, outline_size, outline_color,
            None, None, True
        )

        self._load_customizations()
        self._set_enabled_disabled()

    def _get_sizes_adjusted_for_canvas(self, text_size: int, outline_size: int) -> tuple:
        """
        Scale text and outline sizes to compensate for larger canvases (e.g., SD+ dial touchscreen).

        Font sizes are absolute pixel values, so the same size appears proportionally smaller on a
        taller canvas than on a standard square key. Scaling by the canvas-height to key-height
        ratio preserves the visual proportion the user configured.
        """
        canvas_w, canvas_h = self._get_canvas_size()
        if canvas_h > text_const.KEY_REFERENCE_SIZE:
            scale_factor = canvas_h / text_const.KEY_REFERENCE_SIZE
            return round(text_size * scale_factor), round(outline_size * scale_factor)
        return text_size, outline_size

    def _get_domains(self) -> List[str]:
        """This class needs all domains that provide actions in Home Assistant."""
        return self.plugin_base.backend.get_domains_for_entities()
