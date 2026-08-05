"""Module for the ParameterComboRow."""
from GtkHelper.ComboRow import BaseComboRowItem
from GtkHelper.GenerativeUI.ComboRow import ComboRow
from HomeAssistantPlugin.actions.perform_action.parameters.parameter_row import ParameterRow


class ParameterComboRow(ParameterRow, ComboRow):
    """ComboRow to display action call parameters with a check button."""

    def __init__(self, action_core, var_name: str, field_name: str, default_value: str, items: list, required: bool):
        ComboRow.__init__(self, action_core, var_name, default_value, items, title=field_name,
                          can_reset=False, complex_var_name=True)
        ParameterRow.__init__(self, action_core, field_name, required)

        self.widget.add_prefix(self.check)

    def get_parameter_value(self) -> str:
        """
        Get the value of the row.
        :return: the value
        """
        return str(self.get_selected_item())

    def set_value(self, item: BaseComboRowItem | str) -> None:
        """
        Set the item for the row.
        :param item: the new item
        """
        if self.check.get_active():
            ComboRow.set_value(self, item)

    def _value_changed(self, combo_row, _) -> None:
        if not self.required:
            self.check.set_active(bool(str(self.get_selected_item())))
        ComboRow._value_changed(self, combo_row, _)
        ParameterRow._on_change(self)
