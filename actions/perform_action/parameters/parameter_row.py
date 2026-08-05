"""Module for the ParameterRow."""
from typing import Any

import gi

gi.require_version('Gtk', '4.0')
from gi.repository.Gtk import CheckButton

from HomeAssistantPlugin import const as base_const


class ParameterRow:
    """Row to display action call parameters with a check button."""

    def __init__(self, action_core, field_name: str, required: bool):
        self.action = action_core
        self.field_name = field_name
        self.required = required

        self.check = CheckButton()

        if self.field_name in self.action.settings.get_parameters():
            # we already have a value for this parameter
            self.check.set_active(True)

        if self.required:
            self.check.set_active(True)
            self.check.set_sensitive(False)

        self.check.connect(base_const.CONNECT_TOGGLED, self._on_change)

    def get_parameter_value(self) -> Any:
        """
        Get the value of the row. Must be implemented in a subclass.
        :return: the value
        """
        raise NotImplementedError()

    def set_value(self, value: Any) -> None:
        """
        Set the value for the row. Must be implemented in a subclass.
        :param value: the new value
        """
        raise NotImplementedError()

    def _on_change(self, _=None) -> None:
        """Handle changes to the check button or the value."""
        if self.check.get_active():
            self.action.settings.set_parameter(self.field_name, self.get_parameter_value())
        else:
            self.action.settings.remove_parameter(self.field_name)
