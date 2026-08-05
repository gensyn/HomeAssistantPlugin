"""
Modul to manage icon customizations.
"""

from typing import Any

from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.cores.customization_core.customization import Customization
from HomeAssistantPlugin.actions.show_icon import icon_const


class IconCustomization(Customization):
    """
    Class to represent an icon customization.
    """

    def __init__(self, attribute: str, operator: str, value: str, icon: str, color: tuple[int, int, int, int],
                 scale: int, opacity: int):
        super().__init__(attribute, operator, value)
        self.icon: str = icon
        self.color: tuple[int, int, int, int] = color
        self.scale: int = scale
        self.opacity: int = opacity

    @classmethod
    def from_dict(cls, customization: dict):
        return cls(customization[customization_const.CONDITION][customization_const.ATTRIBUTE],
                   customization[customization_const.CONDITION][customization_const.OPERATOR],
                   customization[customization_const.CONDITION][customization_const.VALUE],
                   customization[icon_const.CUSTOM_ICON], customization[icon_const.CUSTOM_COLOR],
                   customization[icon_const.CUSTOM_SCALE], customization[icon_const.CUSTOM_OPACITY])

    def get_icon(self) -> str:
        """
        Get the icon.
        :return:the icon
        """
        return self.icon

    def get_color(self) -> tuple[int, int, int, int]:
        """
        Get the icon color.
        :return:the icon color
        """
        return self.color

    def get_scale(self) -> int:
        """
        Get the icon scale.
        :return: the icon scale
        """
        return self.scale

    def get_opacity(self) -> int:
        """
        Get the icon opacity.
        :return: the icon opacity
        """
        return self.opacity

    def export(self) -> dict[str, Any]:
        """
        Get this customization as a dict.
        :return: this customization as a dict
        """
        return {
            customization_const.CONDITION: {
                customization_const.ATTRIBUTE: self.attribute,
                customization_const.OPERATOR: self.operator,
                customization_const.VALUE: self.value
            },
            icon_const.CUSTOM_ICON: self.icon,
            icon_const.CUSTOM_COLOR: self.color,
            icon_const.CUSTOM_SCALE: self.scale,
            icon_const.CUSTOM_OPACITY: self.opacity
        }