"""
Modul to manage text customizations.
"""

from typing import Any

from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.cores.customization_core.customization import Customization
from HomeAssistantPlugin.actions.show_text import text_const


class TextCustomization(Customization):
    """
    Class to represent a text customization.
    """

    def __init__(self, attribute: str, operator: str, value: str, position: str, text_attribute: str, custom_text: str,
                 do_round: bool, round_precision: int, text_size: int, text_color: tuple[int, int, int, int],
                 outline_size: int, outline_color: tuple[int, int, int, int], show_unit: bool, line_break: bool):
        super().__init__(attribute, operator, value)
        self.position: str = position
        self.text_attribute: str = text_attribute
        self.custom_text: str = custom_text
        self.round: bool = do_round
        self.round_precision: int = round_precision
        self.text_size: int = text_size
        self.text_color: tuple[int, int, int, int] = text_color
        self.outline_size: int = outline_size
        self.outline_color: tuple[int, int, int, int] = outline_color
        self.show_unit: bool = show_unit
        self.line_break: bool = line_break

    @classmethod
    def from_dict(cls, customization: dict):
        return cls(customization[customization_const.CONDITION][customization_const.ATTRIBUTE],
                   customization[customization_const.CONDITION][customization_const.OPERATOR],
                   customization[customization_const.CONDITION][customization_const.VALUE],
                   customization[text_const.CUSTOM_POSITION],
                   customization[text_const.CUSTOM_ATTRIBUTE],
                   customization[text_const.CUSTOM_CUSTOM_TEXT],
                   customization[text_const.CUSTOM_ROUND],
                   customization[text_const.CUSTOM_ROUND_PRECISION],
                   customization[text_const.CUSTOM_TEXT_SIZE],
                   customization[text_const.CUSTOM_TEXT_COLOR],
                   customization[text_const.CUSTOM_OUTLINE_SIZE],
                   customization[text_const.CUSTOM_OUTLINE_COLOR],
                   customization[text_const.CUSTOM_SHOW_UNIT],
                   customization[text_const.CUSTOM_LINE_BREAK])

    def get_position(self) -> str:
        """
        Get the text position.
        :return: the text position
        """
        return self.position

    def get_text_attribute(self) -> str:
        """
        Get the text attribute.
        :return: the text attribute
        """
        return self.text_attribute

    def get_custom_text(self) -> str:
        """
        Get the custom text.
        :return: the custom text
        """
        return self.custom_text

    def get_round(self) -> bool:
        """
        Get whether to round the text value.
        :return: whether to round the text value
        """
        return self.round

    def get_round_precision(self) -> int:
        """
        Get the text round precision.
        :return: the text round precision
        """
        return self.round_precision

    def get_text_size(self) -> int:
        """
        Get the text size.
        :return: the text size
        """
        return self.text_size

    def get_text_color(self) -> tuple[int, int, int, int]:
        """
        Get the text color.
        :return: the text color
        """
        return self.text_color

    def get_outline_size(self) -> int:
        """
        Get the text outline size.
        :return: the text outline size
        """
        return self.outline_size

    def get_outline_color(self) -> tuple[int, int, int, int]:
        """
        Get the text outline color.
        :return: the text outline color
        """
        return self.outline_color

    def get_show_unit(self) -> bool:
        """
        Get whether to show the unit of measurement.
        :return: whether to show the unit of measurement
        """
        return self.show_unit

    def get_line_break(self) -> bool:
        """
        Get whether to show a line break between value and unit.
        :return: whether to show a line break between value and unit
        """
        return self.line_break

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
            text_const.CUSTOM_POSITION: self.position,
            text_const.CUSTOM_ATTRIBUTE: self.text_attribute,
            text_const.CUSTOM_CUSTOM_TEXT: self.custom_text,
            text_const.CUSTOM_ROUND: self.round,
            text_const.CUSTOM_ROUND_PRECISION: self.round_precision,
            text_const.CUSTOM_TEXT_SIZE: self.text_size,
            text_const.CUSTOM_TEXT_COLOR: self.text_color,
            text_const.CUSTOM_OUTLINE_SIZE: self.outline_size,
            text_const.CUSTOM_OUTLINE_COLOR: self.outline_color,
            text_const.CUSTOM_SHOW_UNIT: self.show_unit,
            text_const.CUSTOM_LINE_BREAK: self.line_break,
        }
