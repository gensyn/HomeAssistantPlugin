"""
The module for the Home Assistant customization row.
"""
from typing import Any

import gi
from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.cores.customization_core.customization import Customization
from HomeAssistantPlugin.actions.cores.customization_core.customization_settings import CustomizationSettings

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository.Adw import ActionRow
from gi.repository.Gtk import Button, Align, Box, Orientation


class CustomizationRow(ActionRow):
    """
    Base for customization rows
    """

    def __init__(self, lm, customization_count: int, index: int, attributes: list, state: dict,
                 settings: CustomizationSettings):
        super().__init__()

        self.lm = lm
        self.attributes = attributes
        self.state = state
        self.settings = settings

        self.edit_button = Button(icon_name="edit", valign=Align.CENTER)
        self.edit_button.set_size_request(15, 15)

        self.delete_button = Button(icon_name="user-trash", valign=Align.CENTER)
        self.delete_button.set_size_request(15, 15)

        box_operations = Box(orientation=Orientation.VERTICAL, spacing=1)
        box_operations.append(self.edit_button)
        box_operations.append(self.delete_button)

        self.up_button = Button(icon_name="go-up", valign=Align.CENTER)
        self.up_button.set_size_request(15, 7)
        self.up_button.set_sensitive(index != 0)

        self.down_button = Button(icon_name="go-down", valign=Align.CENTER)
        self.down_button.set_size_request(15, 7)
        self.down_button.set_sensitive(index != customization_count - 1)

        box_arrows = Box(orientation=Orientation.VERTICAL, spacing=1)
        box_arrows.append(self.up_button)
        box_arrows.append(self.down_button)

        self.add_suffix(box_operations)
        self.add_suffix(box_arrows)

    def _init_title(self, customization: Customization, current_value: Any) -> str:
        operator = self.lm.get(
            customization_const.LABEL_CUSTOMIZATION_OPERATORS[customization.get_operator()])

        return (f"{self.lm.get(customization_const.LABEL_CUSTOMIZATION_IF)} "
                f"\"{customization.get_attribute()}\" "
                f"{operator} "
                f"\"{customization.get_value()}\" "
                f"({self.lm.get(customization_const.LABEL_CUSTOMIZATION_CURRENT)}: {current_value}):\n")
