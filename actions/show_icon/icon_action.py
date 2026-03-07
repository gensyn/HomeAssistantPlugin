"""
The module for the Home Assistant action that is loaded in StreamController.
"""

from typing import List

from GtkHelper.GenerativeUI.ColorButtonRow import ColorButtonRow
from GtkHelper.GenerativeUI.EntryRow import EntryRow
from GtkHelper.GenerativeUI.ScaleRow import ScaleRow
from HomeAssistantPlugin.actions.cores.base_core.base_core import requires_initialization
from HomeAssistantPlugin.actions.cores.customization_core.customization_core import CustomizationCore
from HomeAssistantPlugin.actions.show_icon import icon_const, icon_helper
from HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization
from HomeAssistantPlugin.actions.show_icon.icon_row import IconRow
from HomeAssistantPlugin.actions.show_icon.icon_window import IconWindow
from HomeAssistantPlugin.actions.show_icon.icon_settings import ShowIconSettings


class ShowIcon(CustomizationCore):
    """Action to be loaded by StreamController."""

    def __init__(self, *args, **kwargs):
        super().__init__(window_implementation=IconWindow, customization_implementation=IconCustomization,
                         row_implementation=IconRow, settings_implementation=ShowIconSettings, track_entity=True, *args, **kwargs)

    def get_config_rows(self) -> List:
        """Get the rows to be displayed in the UI."""
        return [self.domain_combo.widget, self.entity_combo.widget, self.icon.widget, self.color.widget,
                self.scale.widget, self.opacity.widget, self.customization_expander.widget]

    def _create_ui_elements(self) -> None:
        """Get all action rows."""
        super()._create_ui_elements()

        self.icon: EntryRow = EntryRow(
            self, icon_const.SETTING_ICON_ICON, icon_const.EMPTY_STRING,
            title=icon_const.LABEL_ICON_ICON, on_change=self._reload, can_reset=False,
            complex_var_name=True
        )

        self.color: ColorButtonRow = ColorButtonRow(
            self, icon_const.SETTING_ICON_COLOR, icon_const.DEFAULT_ICON_COLOR,
            title=icon_const.LABEL_ICON_COLOR, on_change=self._reload,
            can_reset=False, complex_var_name=True
        )

        self.scale: ScaleRow = ScaleRow(
            self, icon_const.SETTING_ICON_SCALE, icon_const.DEFAULT_ICON_SCALE,
            icon_const.ICON_MIN_SCALE, icon_const.ICON_MAX_SCALE, title=icon_const.LABEL_ICON_SCALE,
            step=1, digits=0, on_change=self._reload, can_reset=False,
            complex_var_name=True
        )

        self.opacity: ScaleRow = ScaleRow(
            self, icon_const.SETTING_ICON_OPACITY, icon_const.DEFAULT_ICON_OPACITY,
            icon_const.ICON_MIN_OPACITY, icon_const.ICON_MAX_OPACITY,
            title=icon_const.LABEL_ICON_OPACITY, step=1, digits=0, on_change=self._reload,
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
            self.icon.widget.set_sensitive(False)

            self.color.widget.set_sensitive(False)
            self.color.widget.set_subtitle(self.lm.get(icon_const.LABEL_ICON_NO_ENTITY))

            self.scale.widget.set_sensitive(False)
            self.scale.widget.set_subtitle(self.lm.get(icon_const.LABEL_ICON_NO_ENTITY))

            self.opacity.widget.set_sensitive(False)
            self.opacity.widget.set_subtitle(self.lm.get(icon_const.LABEL_ICON_NO_ENTITY))
        else:
            self.icon.widget.set_sensitive(True)

            self.color.widget.set_sensitive(True)
            self.color.widget.set_subtitle(icon_const.EMPTY_STRING)

            self.scale.widget.set_sensitive(True)
            self.scale.widget.set_subtitle(icon_const.EMPTY_STRING)

            self.opacity.widget.set_sensitive(True)
            self.opacity.widget.set_subtitle(icon_const.EMPTY_STRING)

    def refresh(self, state: dict = None) -> None:
        """
        Executed when an entity is updated to reflect the changes on the key.
        """
        if not self.initialized:
            if not self.plugin_base.backend.is_connected():
                icon, scale = icon_helper.get_icon(state, self.settings, False)
                scale = self._get_scale_adjusted_for_canvas(scale)
                self.set_media(media_path=icon, size=scale)
            return

        entity = self.settings.get_entity()
        if state is None:
            state = self.plugin_base.backend.get_entity(entity)

        if state is None:
            self.set_media()
            return

        icon, scale = icon_helper.get_icon(state, self.settings, self.plugin_base.backend.is_connected())
        scale = self._get_scale_adjusted_for_canvas(scale)
        self.set_media(media_path=icon, size=scale)

        self._load_customizations()
        self._set_enabled_disabled()

    def _get_scale_adjusted_for_canvas(self, scale: float) -> float:
        """
        Adjust the icon scale to compensate for landscape canvases (e.g., SD+ dial touchscreen).

        On landscape canvases the icon is constrained by the canvas height, so it fills far less
        of the canvas width than it does on square keys. Scaling by the canvas aspect ratio makes
        the icon fill the same horizontal proportion as it would on a square key.
        """
        canvas_w, canvas_h = self._get_canvas_size()
        if canvas_h > 0 and canvas_w > canvas_h:
            return scale * canvas_w / canvas_h
        return scale

    def _get_domains(self) -> List[str]:
        """This class needs all domains that provide actions in Home Assistant."""
        return self.plugin_base.backend.get_domains_for_entities()
