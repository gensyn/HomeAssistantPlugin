"""The module for the Level Dial customization row."""

from HomeAssistantPlugin.actions.cores.customization_core import customization_helper
from HomeAssistantPlugin.actions.cores.customization_core.customization_row import CustomizationRow
from HomeAssistantPlugin.actions.cores.customization_core.customization_settings import CustomizationSettings
from HomeAssistantPlugin.actions.level_dial import level_const
from HomeAssistantPlugin.actions.level_dial.level_customization import LevelDialCustomization


def get_value(state: dict, customization: LevelDialCustomization):
    """Gets the current value that the customization references."""
    if customization.get_attribute() == "state":
        return state.get("state")
    return state.get("attributes", {}).get(customization.get_attribute())


class LevelDialRow(CustomizationRow):
    """Row displaying a level dial customization."""

    def __init__(self, lm, customization: LevelDialCustomization, customization_count: int, index: int,
                 attributes: list, state: dict, settings: CustomizationSettings):
        super().__init__(lm, customization_count, index, attributes, state, settings)

        current_value = get_value(state, customization)
        title = self._init_title(customization, current_value)

        if customization.get_icon() is not None:
            title += (f"\n{self.lm.get(level_const.LABEL_LEVEL_ICON)} "
                      f"{customization.get_icon()}")

        if customization.get_color() is not None:
            color = customization_helper.convert_color_list_to_hex(customization.get_color())
            title += (f"\n{self.lm.get(level_const.LABEL_LEVEL_COLOR)} "
                      f"{color}")

        self.set_title(title)
