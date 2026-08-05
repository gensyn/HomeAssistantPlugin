"""Module to manage level dial customizations."""

from typing import Any

from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.cores.customization_core.customization import Customization
from HomeAssistantPlugin.actions.level_dial import level_const


class LevelDialCustomization(Customization):
    """Class to represent a level dial customization."""

    def __init__(self, attribute: str, operator: str, value: str, icon: str,
                 color: tuple[int, int, int, int]):
        super().__init__(attribute, operator, value)
        self.icon: str = icon
        self.color: tuple[int, int, int, int] = color

    @classmethod
    def from_dict(cls, customization: dict):
        return cls(customization[customization_const.CONDITION][customization_const.ATTRIBUTE],
                   customization[customization_const.CONDITION][customization_const.OPERATOR],
                   customization[customization_const.CONDITION][customization_const.VALUE],
                   customization[level_const.CUSTOM_ICON], customization[level_const.CUSTOM_COLOR])

    def get_icon(self) -> str:
        return self.icon

    def get_color(self) -> tuple[int, int, int, int]:
        return self.color

    def export(self) -> dict[str, Any]:
        return {
            customization_const.CONDITION: {
                customization_const.ATTRIBUTE: self.attribute,
                customization_const.OPERATOR: self.operator,
                customization_const.VALUE: self.value
            },
            level_const.CUSTOM_ICON: self.icon,
            level_const.CUSTOM_COLOR: self.color
        }
