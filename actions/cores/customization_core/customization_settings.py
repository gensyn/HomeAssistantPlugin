"""Module to manage HomeAssistantPlugin action settings."""

from HomeAssistantPlugin.actions.cores.base_core.base_settings import BaseSettings
from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.cores.customization_core.customization import Customization


class CustomizationSettings(BaseSettings):
    """
    Class to manage all settings for an HomeAssistantPlugin action.
    :param action: the action whose settings are being managed
    """

    def __init__(self, action, customization_name, customization_implementation):
        super().__init__(action)

        self.customization_name = customization_name
        self.customization_implementation = customization_implementation

    def _get_customization_settings(self) -> dict:
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            return {customization_const.SETTING_CUSTOMIZATIONS: []}
        customization_section = settings.get(self.customization_name)
        if not isinstance(customization_section, dict):
            customization_section = {customization_const.SETTING_CUSTOMIZATIONS: []}
            settings[self.customization_name] = customization_section
            self._action.set_settings(settings)
        return customization_section

    def get_customizations(self):
        customization_section = self._get_customization_settings()
        customizations = customization_section.get(customization_const.SETTING_CUSTOMIZATIONS, [])
        return [self.customization_implementation.from_dict(c) for c in customizations]

    def move_customization(self, index: int, offset: int):
        """
        Move the customization at the index by x places.
        :param index: the index to move
        :param offset: number of places to move; may be negative
        :return:
        """
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            settings = {}
        customization_section = settings.setdefault(self.customization_name, {})
        customizations = customization_section.setdefault(customization_const.SETTING_CUSTOMIZATIONS, [])
        if 0 <= index < len(customizations):
            customization = customizations.pop(index)
            customizations.insert(index + offset, customization)
            self._action.set_settings(settings)

    def remove_customization(self, index: int) -> None:
        """
        Remove the customization at the index.
        :param index: the index to remove
        :return:
        """
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            settings = {}
        customization_section = settings.setdefault(self.customization_name, {})
        customizations = customization_section.setdefault(customization_const.SETTING_CUSTOMIZATIONS, [])
        if 0 <= index < len(customizations):
            customizations.pop(index)
            self._action.set_settings(settings)

    def replace_customization(self, index: int, customization: Customization) -> None:
        """
        Replace the customization at the index.
        :param index: the index to replace
        :param customization: the new customization
        :return:
        """
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            settings = {}
        customization_section = settings.setdefault(self.customization_name, {})
        customizations = customization_section.setdefault(customization_const.SETTING_CUSTOMIZATIONS, [])
        if 0 <= index < len(customizations):
            customizations[index] = customization.export()
            self._action.set_settings(settings)

    def add_customization(self, customization: Customization) -> None:
        """
        Add a new customization.
        :param customization: the new customization
        """
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            settings = {}
        customization_section = settings.setdefault(self.customization_name, {})
        customizations = customization_section.setdefault(customization_const.SETTING_CUSTOMIZATIONS, [])
        customizations.append(customization.export())
        self._action.set_settings(settings)
