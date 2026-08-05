from HomeAssistantPlugin.actions import const
from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.show_icon import icon_const
from HomeAssistantPlugin.actions.show_icon.icon_settings import ShowIconSettings


def migrate_settings(action) -> None:
    settings = action.get_settings()

    if settings.get(const.SETTING_VERSION) is not None:
        return

    migrate_v0_v1(action)

def migrate_v0_v1(action) -> None:
    """
    Migrate from no version to v1.
    There is actually nothing to do yet - this just introduces the version field.
    """
    settings = action.get_settings()

    if not settings:
        # settings are empty - this is a brand-new action
        return

    settings[const.SETTING_VERSION] = const.SETTING_VERSION_NUMBER
    action.set_settings(settings)