"""Module to manage action settings."""

from copy import deepcopy

from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.cores.customization_core.customization_settings import CustomizationSettings
from HomeAssistantPlugin.actions.show_icon import icon_const
from HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization

DEFAULT_SETTINGS = {
    icon_const.SETTING_ICON: icon_const.EMPTY_STRING,
    icon_const.SETTING_COLOR: icon_const.DEFAULT_ICON_COLOR,
    icon_const.SETTING_SCALE: icon_const.DEFAULT_ICON_SCALE,
    icon_const.SETTING_OPACITY: icon_const.DEFAULT_ICON_OPACITY,
    customization_const.SETTING_CUSTOMIZATIONS: []
}


class ShowIconSettings(CustomizationSettings):
    """
    Class to manage all settings for a "Show Icon" action.
    :param action: the action whose settings are being managed
    """

    def __init__(self, action):
        super().__init__(action, icon_const.SETTING_ICON, IconCustomization)

        if not self._action.get_settings().get(icon_const.SETTING_ICON):
            settings = self._action.get_settings()
            settings[icon_const.SETTING_ICON] = deepcopy(DEFAULT_SETTINGS)
            self._action.set_settings(settings)

    def _get_icon_settings(self) -> dict:
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            return deepcopy(DEFAULT_SETTINGS)
        icon_settings = settings.get(icon_const.SETTING_ICON)
        if not isinstance(icon_settings, dict):
            icon_settings = deepcopy(DEFAULT_SETTINGS)
            settings[icon_const.SETTING_ICON] = icon_settings
            self._action.set_settings(settings)
        return icon_settings

    def get_icon(self) -> str:
        """
        Get the icon.
        :return: the icon
        """
        return self._get_icon_settings().get(icon_const.SETTING_ICON, icon_const.EMPTY_STRING)

    def get_color(self) -> tuple[int, int, int, int]:
        """
        Get the color.
        :return: the color
        """
        color = self._get_icon_settings().get(icon_const.SETTING_COLOR, icon_const.DEFAULT_ICON_COLOR)
        return tuple(color) if isinstance(color, (list, tuple)) else icon_const.DEFAULT_ICON_COLOR

    def get_scale(self) -> int:
        """
        Get the scale.
        :return: the scale
        """
        return int(self._get_icon_settings().get(icon_const.SETTING_SCALE, icon_const.DEFAULT_ICON_SCALE))

    def get_opacity(self) -> int:
        """
        Get the opacity.
        :return: the opacity
        """
        return int(self._get_icon_settings().get(icon_const.SETTING_OPACITY, icon_const.DEFAULT_ICON_OPACITY))
