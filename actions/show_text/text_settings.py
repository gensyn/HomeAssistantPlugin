"""Module to manage action settings."""

from typing import Tuple

from HomeAssistantPlugin.actions.show_text.text_customization import TextCustomization
from HomeAssistantPlugin.actions.show_text import text_const
from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.cores.customization_core.customization_settings import CustomizationSettings

DEFAULT_SETTINGS = {
    text_const.SETTING_POSITION: text_const.DEFAULT_POSITION,
    text_const.SETTING_ATTRIBUTE: text_const.STATE,
    text_const.SETTING_ROUND: text_const.DEFAULT_ROUND,
    text_const.SETTING_ROUND_PRECISION: text_const.DEFAULT_ROUND_PRECISION,
    text_const.SETTING_TEXT_SIZE: text_const.DEFAULT_TEXT_SIZE,
    text_const.SETTING_TEXT_COLOR: text_const.DEFAULT_TEXT_COLOR,
    text_const.SETTING_OUTLINE_SIZE: text_const.DEFAULT_OUTLINE_SIZE,
    text_const.SETTING_OUTLINE_COLOR: text_const.DEFAULT_OUTLINE_COLOR,
    text_const.SETTING_SHOW_UNIT: text_const.DEFAULT_SHOW_UNIT,
    text_const.SETTING_UNIT_LINE_BREAK: text_const.DEFAULT_UNIT_LINE_BREAK,
    customization_const.SETTING_CUSTOMIZATIONS: []
}


class ShowTextSettings(CustomizationSettings):
    """
    Class to manage all settings for a "Show Text" action.
    :param action: the action whose settings are being managed
    """

    def __init__(self, action):
        super().__init__(action, text_const.SETTING_TEXT, TextCustomization)

        if not self._action.get_settings().get(text_const.SETTING_TEXT):
            settings = self._action.get_settings()
            settings[text_const.SETTING_TEXT] = DEFAULT_SETTINGS.copy()
            self._action.set_settings(settings)

    def _get_text_settings(self) -> dict:
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            return DEFAULT_SETTINGS.copy()
        text_settings = settings.get(text_const.SETTING_TEXT)
        if not isinstance(text_settings, dict):
            text_settings = DEFAULT_SETTINGS.copy()
            settings[text_const.SETTING_TEXT] = text_settings
            self._action.set_settings(settings)
        return text_settings

    def get_position(self) -> str:
        """
        Get the position.
        :return: the position
        """
        return self._get_text_settings().get(text_const.SETTING_POSITION, text_const.DEFAULT_POSITION)

    def get_attribute(self) -> str:
        """
        Get the attribute.
        :return: the attribute
        """
        return self._get_text_settings().get(text_const.SETTING_ATTRIBUTE, text_const.STATE)

    def get_round(self) -> bool:
        """
        Get the round.
        :return: the round
        """
        return bool(self._get_text_settings().get(text_const.SETTING_ROUND, text_const.DEFAULT_ROUND))

    def get_round_precision(self) -> int:
        """
        Get the round precision.
        :return: the round precision
        """
        return int(self._get_text_settings().get(text_const.SETTING_ROUND_PRECISION, text_const.DEFAULT_ROUND_PRECISION))

    def get_text_size(self) -> int:
        """
        Get the text size.
        :return: the text size
        """
        return int(self._get_text_settings().get(text_const.SETTING_TEXT_SIZE, text_const.DEFAULT_TEXT_SIZE))

    def get_text_color(self) -> Tuple[int, int, int, int]:
        """
        Get the text color.
        :return: the text color
        """
        return self._get_text_settings().get(text_const.SETTING_TEXT_COLOR, text_const.DEFAULT_TEXT_COLOR)

    def get_outline_size(self) -> int:
        """
        Get the outline size.
        :return: the outline size
        """
        return int(self._get_text_settings().get(text_const.SETTING_OUTLINE_SIZE, text_const.DEFAULT_OUTLINE_SIZE))

    def get_outline_color(self) -> Tuple[int, int, int, int]:
        """
        Get the outline color.
        :return: the outline color
        """
        return self._get_text_settings().get(text_const.SETTING_OUTLINE_COLOR, text_const.DEFAULT_OUTLINE_COLOR)

    def get_show_unit(self) -> bool:
        """
        Get the show unit.
        :return: the show unit
        """
        return bool(self._get_text_settings().get(text_const.SETTING_SHOW_UNIT, text_const.DEFAULT_SHOW_UNIT))

    def get_unit_line_break(self) -> bool:
        """
        Get the unit line break.
        :return: the unit line break
        """
        return bool(self._get_text_settings().get(text_const.SETTING_UNIT_LINE_BREAK, text_const.DEFAULT_UNIT_LINE_BREAK))
