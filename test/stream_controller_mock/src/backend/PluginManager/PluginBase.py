from typing import Any

from HomeAssistantPlugin.const import SETTING_HOST, SETTING_PORT, SETTING_SSL, SETTING_TOKEN


class PluginBase:

    def __init__(self):
        # without token - otherwise it tries to connect to HA
        self.settings = {
            SETTING_HOST: "localhost",
            SETTING_PORT: 8123,
            SETTING_SSL: True,
            SETTING_TOKEN: "",
        }

    def add_action_holder(self, _):
        pass

    def register(self, **kwargs):
        pass

    def get_settings(self):
        return self.settings

    def set_settings(self, settings: dict[str, Any]):
        self.settings = settings
