"""
The module for the Home Assistant action that is loaded in StreamController.
"""

import os

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio
from gi.repository.Gtk import Align, Button, FileDialog, FileFilter

from loguru import logger as log

from HomeAssistantPlugin.actions.cores.base_core.base_core import requires_initialization
from HomeAssistantPlugin.actions.cores.customization_core.customization_core import CustomizationCore
from HomeAssistantPlugin.actions.show_icon import icon_const, icon_helper
from HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization
from HomeAssistantPlugin.actions.show_icon.icon_row import IconRow
from HomeAssistantPlugin.actions.show_icon.icon_settings import ShowIconSettings
from HomeAssistantPlugin.actions.show_icon.icon_window import IconWindow

from GtkHelper.GenerativeUI.ColorButtonRow import ColorButtonRow
from GtkHelper.GenerativeUI.EntryRow import EntryRow
from GtkHelper.GenerativeUI.ScaleRow import ScaleRow


class ShowIcon(CustomizationCore):
    """Action to be loaded by StreamController."""

    def __init__(self, *args, **kwargs):
        # Must be set before create_ui_elements in BaseCore is called
        self.icon = None
        self.color = None
        self.scale = None
        self.opacity = None
        super().__init__(window_implementation=IconWindow, customization_implementation=IconCustomization,
                         row_implementation=IconRow, settings_implementation=ShowIconSettings, track_entity=True, *args,
                         **kwargs)

    def get_config_rows(self) -> list:
        """Get the rows to be displayed in the UI."""
        return [self.domain_combo.widget, self.entity_combo.widget, self.icon.widget, self.color.widget,
                self.scale.widget, self.opacity.widget, self.customization_expander.widget]

    def create_ui_elements(self) -> None:
        """Get all action rows."""
        super().create_ui_elements()

        self.icon: EntryRow = EntryRow(
            self, icon_const.SETTING_ICON_ICON, icon_const.EMPTY_STRING,
            title=icon_const.LABEL_ICON_ICON, on_change=self._reload, can_reset=False,
            complex_var_name=True
        )

        browse_button = Button(label=self.lm.get(icon_const.LABEL_ICON_BROWSE))
        browse_button.set_valign(Align.CENTER)
        browse_button.connect("clicked", self._on_browse_clicked)
        self.icon.widget.add_suffix(browse_button)

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
    def set_enabled_disabled(self) -> None:
        """
        Set the active/inactive state for all rows.
        """
        super().set_enabled_disabled()

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
            icon_value = self.settings.get_icon()
            has_icon = bool(icon_value) and icon_value in icon_helper.MDI_ICONS
            not_supported = self.lm.get(icon_const.LABEL_ICON_ONLY_SUPPORTED_FOR_ICONS) if not has_icon else icon_const.EMPTY_STRING

            self.icon.widget.set_sensitive(True)

            self.color.widget.set_sensitive(has_icon)
            self.color.widget.set_subtitle(not_supported)

            self.scale.widget.set_sensitive(True)
            self.scale.widget.set_subtitle(icon_const.EMPTY_STRING)

            self.opacity.widget.set_sensitive(has_icon)
            self.opacity.widget.set_subtitle(not_supported)

    def refresh(self, state: dict = None) -> None:
        """
        Executed when an entity is updated to reflect the changes on the key.
        """
        if not self.initialized:
            if not self.plugin_base.backend.is_connected():
                icon, scale = icon_helper.get_icon(state, self.settings, False)
                self.set_media(media_path=icon, size=scale)
            return

        entity = self.settings.get_entity()
        if state is None:
            state = self.plugin_base.backend.get_entity(entity)

        if state is None:
            self.set_media()
            return

        icon, scale = icon_helper.get_icon(state, self.settings, self.plugin_base.backend.is_connected())
        self.set_media(media_path=icon, size=scale)

        self._load_customizations()
        self.set_enabled_disabled()

    def _on_browse_clicked(self, *_) -> None:
        dialog = FileDialog()
        dialog.set_title(self.lm.get(icon_const.LABEL_ICON_IMAGE))

        filter_images = FileFilter()
        filter_images.set_name("Images")
        for mime in ("image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml"):
            filter_images.add_mime_type(mime)

        filters = Gio.ListStore.new(FileFilter)
        filters.append(filter_images)
        dialog.set_filters(filters)
        dialog.set_default_filter(filter_images)

        current_path = self.icon.widget.get_text()
        if current_path:
            current_dir = os.path.dirname(current_path)
            if os.path.isdir(current_dir):
                dialog.set_initial_folder(Gio.File.new_for_path(current_dir))

        dialog.open(None, None, self._on_file_chosen)

    def _on_file_chosen(self, dialog, result) -> None:
        try:
            file = dialog.open_finish(result)
            if file:
                self.icon.widget.set_text(file.get_path())
                self._reload()
        except Exception as e:
            log.error(f"Error choosing file: {e}")

    def _get_domains(self) -> list[str]:
        """This class needs all domains that provide actions in Home Assistant."""
        return self.plugin_base.backend.get_domains_for_entities()
