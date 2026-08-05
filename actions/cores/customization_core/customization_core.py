"""The module for the Home Assistant action that is loaded in StreamController."""
from copy import deepcopy

import gi

gi.require_version("Gtk", "4.0")
from gi.repository.Gtk import Button, Align

from GtkHelper.GenerativeUI.ExpanderRow import ExpanderRow

from HomeAssistantPlugin.actions import const as base_const
from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore, requires_initialization


class CustomizationCore(BaseCore):
    """Action core for all Home Assistant Actions."""

    def __init__(self, window_implementation, customization_implementation, row_implementation, *args, **kwargs):
        # Must be set before create_ui_elements in BaseCore is called
        self.customization_expander = None
        # Flag set during on_remove() to prevent _load_customizations() from
        # adding child widgets to the expander while it is detached from the UI.
        self._clearing = False
        super().__init__(*args, **kwargs)
        self.window_implementation = window_implementation
        self.customization_implementation = customization_implementation
        self.row_implementation = row_implementation

    def on_ready(self) -> None:
        """Set up action when StreamController has finished loading."""
        super().on_ready()

        if not self.plugin_base.backend.is_connected():
            self.refresh()
            return

        self._reload()

    def create_ui_elements(self) -> None:
        """Get all action rows."""
        super().create_ui_elements()

        add_customization_button = Button(icon_name="list-add", valign=Align.CENTER)
        add_customization_button.set_size_request(15, 15)
        add_customization_button.connect(
            base_const.CONNECT_CLICKED,
            self._on_add_customization,
            self._add_customization
        )

        self.customization_expander: ExpanderRow = ExpanderRow(
            self, base_const.EMPTY_STRING, False,
            title=base_const.LABEL_CUSTOMIZATION, can_reset=False,
            auto_add=False
        )
        self.customization_expander.widget.add_suffix(add_customization_button)

    def _on_add_customization(self, _, callback, index: int = -1):
        attributes = self._get_attributes()
        current = None
        if index > -1:
            current = self.settings.get_customizations()[index]

        window = self.window_implementation(self.lm, attributes, callback, current=current, index=index)

        window.show()

    def _add_customization(
            self, customization, index: int
    ) -> None:
        customizations = deepcopy(self.settings.get_customizations())

        if index > -1:
            # we have to check for duplicates without the item being edited because it may have not changed
            customizations.pop(index)

        if customization in customizations:
            if index > -1:
                # edited item is identical to existing - delete it
                self.settings.remove_customization(index)
            self.refresh()
            return

        if index > -1:
            self.settings.replace_customization(index, customization)
        else:
            self.settings.add_customization(customization)

        self.refresh()

    def _on_delete_customization(self, _, index: int):
        self.settings.remove_customization(index)
        self.refresh()

    def _on_move_up(self, _, index: int):
        self.settings.move_customization(index, -1)
        self.refresh()

    def _on_move_down(self, _, index: int):
        self.settings.move_customization(index, 1)
        self.refresh()

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
            self.customization_expander.widget.set_sensitive(False)
            self.customization_expander.widget.set_subtitle(self.lm.get(base_const.LABEL_NO_ENTITY))
            self.customization_expander.set_expanded(False)
        else:
            self.customization_expander.widget.set_sensitive(True)
            self.customization_expander.widget.set_subtitle(base_const.EMPTY_STRING)
            self.customization_expander.set_expanded(
                len(self.settings.get_customizations()) > 0
            )

    def _get_attributes(self) -> list[str]:
        """
        Gets the list of attributes for the selected entity.
        :return: the list of attributes
        """
        ha_entity = self.plugin_base.backend.get_entity(self.settings.get_entity())
        attributes = [customization_const.STATE]
        attributes.extend(list(ha_entity.get(customization_const.ATTRIBUTES, {}).keys()))
        return attributes

    @requires_initialization
    def on_remove(self) -> None:
        """Clean up after action was removed.

        Prevents _load_customizations() from modifying the customization
        expander while it is being detached from the UI, which would corrupt
        GTK's internal widget-tree state and cause a crash on the next
        navigation back to this page.
        """
        self._clearing = True
        try:
            super().on_remove()
        finally:
            self.customization_expander.clear_rows()
            self._clearing = False

    def _load_customizations(self) -> None:
        if self._clearing:
            return
        self.customization_expander.clear_rows()
        attributes = self._get_attributes()
        state = self.plugin_base.backend.get_entity(self.settings.get_entity())

        for index, customization in enumerate(self.settings.get_customizations()):
            row = self.row_implementation(
                self.lm, customization, len(self.settings.get_customizations()), index,
                attributes, state, self.settings
            )
            row.edit_button.connect(
                base_const.CONNECT_CLICKED, self._on_add_customization,
                self._add_customization, index
            )
            row.delete_button.connect(
                base_const.CONNECT_CLICKED, self._on_delete_customization, index
            )
            row.up_button.connect(
                base_const.CONNECT_CLICKED, self._on_move_up, index
            )
            row.down_button.connect(
                base_const.CONNECT_CLICKED, self._on_move_down, index
            )
            self.customization_expander.add_row(row)
