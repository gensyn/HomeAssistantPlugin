"""Module to manage action settings."""

from copy import deepcopy

from HomeAssistantPlugin.actions.cores.base_core.base_settings import BaseSettings
from HomeAssistantPlugin.actions.perform_action import perform_const

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
            settings[perform_const.SETTING_ACTION] = deepcopy(DEFAULT_SETTINGS)
            self._action.set_settings(settings)

    def _get_perform_settings(self) -> dict:
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            return deepcopy(DEFAULT_SETTINGS)
        perform_settings = settings.get(perform_const.SETTING_ACTION)
        if not isinstance(perform_settings, dict):
            perform_settings = deepcopy(DEFAULT_SETTINGS)
            settings[perform_const.SETTING_ACTION] = perform_settings
            self._action.set_settings(settings)
        return perform_settings

    def get_action(self) -> str:
        """
        Get the action.
        :return: the action
        """
        return self._get_perform_settings().get(perform_const.SETTING_ACTION, perform_const.EMPTY_STRING)

    def get_parameters(self) -> dict:
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
        settings[perform_const.SETTING_ACTION][perform_const.ACTION_PARAMETERS][field] = value
        self._action.set_settings(settings)

    def remove_parameter(self, field) -> None:
        """
        Remove the action parameter for the field.
        :param field: the field to remove
        """
        settings = self._action.get_settings()
        settings[perform_const.SETTING_ACTION][perform_const.ACTION_PARAMETERS].pop(field)
        self._action.set_settings(settings)

    def clear_parameters(self) -> None:
        """Clear all action parameters."""
        settings = self._action.get_settings()
        settings[perform_const.SETTING_ACTION][perform_const.ACTION_PARAMETERS] = {}
        self._action.set_settings(settings)

    def reset(self, domain: str) -> None:
        """
        Empty the settings and keep only the UUID and the given domain.
        :param domain: the new domain
        """
        super().reset(domain)
        settings = self._action.get_settings()
        settings[perform_const.SETTING_ACTION][perform_const.SETTING_ACTION] = perform_const.EMPTY_STRING
        settings[perform_const.SETTING_ACTION][perform_const.ACTION_PARAMETERS] = {}
        self._action.set_settings(settings)
