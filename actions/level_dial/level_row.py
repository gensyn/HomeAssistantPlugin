"""The module for the Level Dial customization row."""

from HomeAssistantPlugin.actions.cores.customization_core import customization_helper, condition
from HomeAssistantPlugin.actions.cores.customization_core.customization_row import CustomizationRow
from HomeAssistantPlugin.actions.cores.customization_core.customization_settings import CustomizationSettings
from HomeAssistantPlugin.actions.level_dial import level_const
from HomeAssistantPlugin.actions.level_dial.level_customization import LevelDialCustomization


def get_value(state: dict, condition_: condition.Condition, get_entity=None):
    """Gets the current value that the condition references."""
    return condition.get_state_value(condition.resolve_state(state, condition_.entity, get_entity),
                                     condition_.attribute)


class LevelDialRow(CustomizationRow):
    """Row displaying a level dial customization."""

    def __init__(self, lm, customization: LevelDialCustomization, customization_count: int, index: int,
                 attributes: list, state: dict, settings: CustomizationSettings, get_entity=None):
        super().__init__(lm, customization_count, index, attributes, state, settings, get_entity)

        title = self._init_title(customization, lambda c: get_value(state, c, get_entity))

        if customization.get_icon() is not None:
            title += (f"\n{self.lm.get(level_const.LABEL_LEVEL_ICON)} "
                      f"{customization.get_icon()}")

        if customization.get_color() is not None:
            color = customization_helper.convert_color_list_to_hex(customization.get_color())
            title += (f"\n{self.lm.get(level_const.LABEL_LEVEL_COLOR)} "
                      f"{color}")

        self.set_title(title)
