"""Module for action parameter operations."""
from HomeAssistantPlugin.actions.perform_action import perform_const
from HomeAssistantPlugin.actions.perform_action.parameters.parameter_combo_row import \
    ParameterComboRow
from HomeAssistantPlugin.actions.perform_action.parameters.parameter_entry_row import \
    ParameterEntryRow
from HomeAssistantPlugin.actions.perform_action.parameters.parameter_scale_row import \
    ParameterScaleRow
from HomeAssistantPlugin.actions.perform_action.parameters.parameter_switch_row import \
    ParameterSwitchRow


def load_parameters(action):
    """Load action parameters from Home Assistant."""
    action.parameters_expander.clear_rows()

    ha_entity = action.plugin_base.backend.get_entity(action.settings.get_entity())

    ha_action = action.settings.get_action()

    if not ha_entity or not ha_action:
        return

    fields = action.plugin_base.backend.get_actions(
        str(action.domain_combo.get_selected_item()), load_if_empty=False).get(
        ha_action, {}).get(perform_const.ATTRIBUTE_FIELDS, {})

    fields.update(fields.get(perform_const.ADVANCED_FIELDS, {}).get(perform_const.ATTRIBUTE_FIELDS, {}))
    fields.pop(perform_const.ADVANCED_FIELDS, None)

    for field_name, field_settings in fields.items():
        setting_value = action.settings.get_parameters().get(field_name)

        if not perform_const.SELECTOR in field_settings:
            continue

        selector = list(field_settings[perform_const.SELECTOR].keys())[0]

        name = field_settings.get(perform_const.NAME, field_name)
        var_name = f"{perform_const.SETTING_SERVICE}.{perform_const.ACTION_PARAMETERS}.{field_name}"
        required = field_settings.get(perform_const.REQUIRED, False)
        if selector == perform_const.SELECT or f"{field_name}{perform_const.LIST}" in ha_entity.get(perform_const.ATTRIBUTES,
                                                                               {}).keys():
            if selector == perform_const.SELECT:
                options = field_settings[perform_const.SELECTOR][perform_const.SELECT][perform_const.OPTIONS]
            else:
                options = ha_entity.get(perform_const.ATTRIBUTES, {})[f"{field_name}{perform_const.LIST}"]

            if not options:
                # If there are no options, skip this parameter as it cannot be selected.
                continue

            if not isinstance(options[0], str):
                options = [opt[perform_const.VALUE] for opt in options]

            if setting_value is None:
                setting_value = perform_const.EMPTY_STRING

            row = ParameterComboRow(action, var_name, name, setting_value, options, required)
        elif selector == perform_const.BOOLEAN:
            value = False

            if setting_value is not None:
                value = setting_value
            else:
                default_value = field_settings.get(perform_const.DEFAULT)
                if default_value is not None:
                    value = bool(default_value)

            row = ParameterSwitchRow(action, var_name, name, value, required)
        elif selector == perform_const.NUMBER:
            number_min = field_settings[perform_const.SELECTOR][perform_const.NUMBER][perform_const.MIN]
            number_max = field_settings[perform_const.SELECTOR][perform_const.NUMBER][perform_const.MAX]
            number_step = field_settings[perform_const.SELECTOR][perform_const.NUMBER].get(perform_const.STEP, 1)

            value = number_min

            if setting_value is not None:
                value = setting_value
            else:
                default_value = field_settings.get(perform_const.DEFAULT)
                if default_value is not None:
                    value = default_value

            row = ParameterScaleRow(action, var_name, name, value, number_min, number_max, number_step, required)
        else:
            value = str(setting_value) if setting_value is not None else perform_const.EMPTY_STRING
            row = ParameterEntryRow(action, var_name, name, value, required)

        action.parameters_expander.add_row(row.widget)
