"""
Constants for actions.
"""

EMPTY_STRING = ""

# HOME_ASSISTANT_ACTION

LABEL_ENTITY_DOMAIN = "actions.home_assistant.entity.domain.label"
LABEL_ENTITY_ENTITY = "actions.home_assistant.entity.entity.label"

LABEL_SETTINGS_ENTITY = "actions.home_assistant.settings.entity.label"

LABEL_CUSTOMIZATION = "actions.home_assistant.customization.label"
LABEL_NO_ENTITY = "actions.home_assistant.customization.no_entity.label"

SETTING_VERSION = "version"
SETTING_VERSION_NUMBER = 1

SETTING_ENTITY = "entity"
SETTING_DOMAIN = "domain"
SETTING_ENTITY_DOMAIN = f"{SETTING_ENTITY}.{SETTING_DOMAIN}"
SETTING_ENTITY_ENTITY = f"{SETTING_ENTITY}.{SETTING_ENTITY}"

CONNECT_ACTIVATE = "activate"
CONNECT_CHANGED = "changed"
CONNECT_CLICKED = "clicked"
CONNECT_NOTIFY_ACTIVE = "notify::active"
CONNECT_NOTIFY_RGBA = "notify::rgba"
CONNECT_NOTIFY_SELECTED_ITEM = "notify::selected-item"
CONNECT_NOTIFY_COLOR_SET = "color-set"
CONNECT_TOGGLED = "toggled"
CONNECT_VALUE_CHANGED = "value-changed"
