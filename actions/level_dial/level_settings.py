"""Module to manage Level Dial settings."""

import copy

from HomeAssistantPlugin.actions.level_dial import level_const
from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.cores.customization_core.customization_settings import CustomizationSettings
from HomeAssistantPlugin.actions.level_dial.level_customization import LevelDialCustomization

DEFAULT_SETTINGS = {
    level_const.SETTING_STEP: level_const.DEFAULT_STEP,
    level_const.SETTING_LABEL: level_const.DEFAULT_LABEL,
    level_const.SETTING_BATCH_DELAY: level_const.DEFAULT_BATCH_DELAY,
    customization_const.SETTING_CUSTOMIZATIONS: []
}


class LevelDialSettings(CustomizationSettings):
    """Settings manager for the Level Dial action."""

    def __init__(self, action):
        super().__init__(action, level_const.SETTING_LEVEL, LevelDialCustomization)

        if not self._action.get_settings().get(level_const.SETTING_LEVEL):
            settings = self._action.get_settings()
            settings[level_const.SETTING_LEVEL] = copy.deepcopy(DEFAULT_SETTINGS)
            self._action.set_settings(settings)

    def get_step(self) -> int:
        return self._action.get_settings()[level_const.SETTING_LEVEL][level_const.SETTING_STEP]

    def get_label(self) -> str:
        return self._action.get_settings()[level_const.SETTING_LEVEL].get(
            level_const.SETTING_LABEL, level_const.DEFAULT_LABEL
        )

    def get_batch_delay(self) -> int:
        return self._action.get_settings()[level_const.SETTING_LEVEL].get(
            level_const.SETTING_BATCH_DELAY, level_const.DEFAULT_BATCH_DELAY
        )

    def reset(self, domain: str) -> None:
        super().reset(domain)
        settings = self._action.get_settings()
        settings[level_const.SETTING_LEVEL][level_const.SETTING_STEP] = level_const.DEFAULT_STEP
        settings[level_const.SETTING_LEVEL][level_const.SETTING_LABEL] = level_const.DEFAULT_LABEL
        settings[level_const.SETTING_LEVEL][level_const.SETTING_BATCH_DELAY] = level_const.DEFAULT_BATCH_DELAY
        self._action.set_settings(settings)
