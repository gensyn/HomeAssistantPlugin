"""Module to manage HomeAssistantPlugin action settings."""

from copy import deepcopy
from HomeAssistantPlugin.actions import const

DEFAULT_SETTINGS = {
    const.SETTING_VERSION: const.SETTING_VERSION_NUMBER,
    const.SETTING_DOMAIN: const.EMPTY_STRING,
    const.SETTING_ENTITY: const.EMPTY_STRING
}


class BaseSettings:
    """
    Class to manage all settings for an HomeAssistantPlugin action.
    :param action: the action whose settings are being managed
    """

    def __init__(self, action):
        self._action = action

        if not self._action.get_settings().get(const.SETTING_ENTITY):
            settings = self._action.get_settings()
            settings[const.SETTING_ENTITY] = deepcopy(DEFAULT_SETTINGS)
            self._action.set_settings(settings)

    def _get_entity_settings(self) -> dict:
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            return deepcopy(DEFAULT_SETTINGS)
        entity_settings = settings.get(const.SETTING_ENTITY)
        if not isinstance(entity_settings, dict):
            entity_settings = deepcopy(DEFAULT_SETTINGS)
            settings[const.SETTING_ENTITY] = entity_settings
            self._action.set_settings(settings)
        return entity_settings

    def get_domain(self) -> str:
        """
        Get the domain.
        :return: the domain
        """
        return self._get_entity_settings().get(const.SETTING_DOMAIN, const.EMPTY_STRING)

    def get_entity(self) -> str:
        """
        Get the entity.
        :return: the entity
        """
        return self._get_entity_settings().get(const.SETTING_ENTITY, const.EMPTY_STRING)

    def reset(self, domain: str) -> None:
        """
        Delete the settings and keeps only the UUID. The given domain is also set.
        :param domain: the new domain
        """
        settings = self._action.get_settings()
        if not isinstance(settings, dict):
            settings = {}
        if not isinstance(settings.get(const.SETTING_ENTITY), dict):
            settings[const.SETTING_ENTITY] = deepcopy(DEFAULT_SETTINGS)
        settings[const.SETTING_ENTITY][const.SETTING_DOMAIN] = domain
        settings[const.SETTING_ENTITY][const.SETTING_ENTITY] = const.EMPTY_STRING
        self._action.set_settings(settings)
