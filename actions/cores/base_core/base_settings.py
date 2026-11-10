"""Module to manage HomeAssistantPlugin action settings."""

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
            settings[const.SETTING_ENTITY] = DEFAULT_SETTINGS.copy()
            self._action.set_settings(settings)

    def get_domain(self) -> str:
        """
        Get the domain.
        :return: the domain
        """
        return self._action.get_settings().get(const.SETTING_ENTITY, {}).get(const.SETTING_DOMAIN)

    def get_entity(self) -> str:
        """
        Get the entity.
        :return: the entity
        """
        return self._action.get_settings().get(const.SETTING_ENTITY, {}).get(const.SETTING_ENTITY)

    def reset(self, domain: str) -> None:
        """
        Delete the settings and keeps only the UUID. The given domain is also set.
        A stored domain is never replaced by an empty one - that would only ever happen when the
        backend is not connected and the combo has nothing to offer.
        :param domain: the new domain
        """
        if not domain and self.get_domain():
            return

        settings = self._action.get_settings()
        settings[const.SETTING_ENTITY][const.SETTING_DOMAIN] = domain
        settings[const.SETTING_ENTITY][const.SETTING_ENTITY] = const.EMPTY_STRING
        self._action.set_settings(settings)