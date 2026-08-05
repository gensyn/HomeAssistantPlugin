"""Module to manage action settings."""

from typing import Dict

from HomeAssistantPlugin.actions.perform_action import perform_const
from HomeAssistantPlugin.actions.cores.base_core.base_settings import BaseSettings

DEFAULT_SETTINGS = {
    perform_const.SETTING_ACTION: perform_const.EMPTY_STRING,
    perform_const.ACTION_PARAMETERS: {}
}


class PerformActionSettings(BaseSettings):
    """
    Class to manage all settings for a "Perform Action" action.
    :param action: the action whose settings are being managed
    """

    def __init__(self, action):
        super().__init__(action)

        if not self._action.get_settings().get(perform_const.SETTING_ACTION):
            settings = self._action.get_settings()
            settings[perform_const.SETTING_ACTION] = DEFAULT_SETTINGS.copy()
            self._action.set_settings(settings)

    def _get_perform_settings(self) -> dict:
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            return DEFAULT_SETTINGS.copy()
        perform_settings = settings.get(perform_const.SETTING_ACTION)
        if not isinstance(perform_settings, dict):
            perform_settings = DEFAULT_SETTINGS.copy()
            settings[perform_const.SETTING_ACTION] = perform_settings
            self._action.set_settings(settings)
        return perform_settings

    def get_action(self) -> str:
        """
        Get the action.
        :return: the action
        """
        return self._get_perform_settings().get(perform_const.SETTING_ACTION, perform_const.EMPTY_STRING)

    def get_parameters(self) -> Dict:
        """
        Retrieve all action parameters.
        :return: all action parameters
        """
        return self._get_perform_settings().get(perform_const.ACTION_PARAMETERS, {})

    def set_parameter(self, field, value) -> None:
        """
        Set the action parameter for the field.
        :param field: the field to set
        :param value: the value for the field
        """
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            settings = {}
        perform_settings = settings.setdefault(perform_const.SETTING_ACTION, DEFAULT_SETTINGS.copy())
        parameters = perform_settings.setdefault(perform_const.ACTION_PARAMETERS, {})
        parameters[field] = value
        self._action.set_settings(settings)

    def remove_parameter(self, field) -> None:
        """
        Remove the action parameter for the field.
        :param field: the field to remove
        """
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            settings = {}
        perform_settings = settings.setdefault(perform_const.SETTING_ACTION, DEFAULT_SETTINGS.copy())
        parameters = perform_settings.setdefault(perform_const.ACTION_PARAMETERS, {})
        parameters.pop(field, None)
        self._action.set_settings(settings)

    def clear_parameters(self) -> None:
        """Clear all action parameters."""
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            settings = {}
        perform_settings = settings.setdefault(perform_const.SETTING_ACTION, DEFAULT_SETTINGS.copy())
        perform_settings[perform_const.ACTION_PARAMETERS] = {}
        self._action.set_settings(settings)

    def reset(self, domain: str) -> None:
        """
        Empty the settings and keep only the UUID and the given domain.
        :param domain: the new domain
        """
        super().reset(domain)
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            settings = {}
        perform_settings = settings.setdefault(perform_const.SETTING_ACTION, DEFAULT_SETTINGS.copy())
        perform_settings[perform_const.SETTING_ACTION] = perform_const.EMPTY_STRING
        perform_settings[perform_const.ACTION_PARAMETERS] = {}
        self._action.set_settings(settings)
