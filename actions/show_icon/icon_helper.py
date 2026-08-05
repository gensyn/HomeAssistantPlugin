"""
Module for icon related operations.
"""

import json
import logging
import os

from HomeAssistantPlugin.actions.cores.customization_core import customization_helper
from HomeAssistantPlugin.actions.show_icon import icon_const
from HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization
from HomeAssistantPlugin.actions.show_icon.icon_settings import ShowIconSettings

MDI_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..",
                            icon_const.MDI_SVG_JSON)

with open(MDI_FILENAME, "r", encoding="utf-8") as f:
    MDI_ICONS: dict[str, str] = json.loads(f.read())


def get_icon(state: dict, settings: ShowIconSettings, is_connected: bool) -> tuple[str, float]:
    """
    Get the item corresponding to the given state.
    """
    if not is_connected:
        return (_get_icon_svg(icon_const.ICON_NETWORK_OFF).replace("<color>",
                                                                   icon_const.ICON_COLOR_RED).replace(
            "<opacity>", "1.0")), round(icon_const.DEFAULT_ICON_SCALE / 100, 2)

    name, color, scale, opacity = _get_icon_settings(state, settings)

    if name not in MDI_ICONS:
        # color and opacity only have an effect on icons
        return name, scale

    # convert RGB color to hex
    color = customization_helper.convert_color_list_to_hex(color)

    icon = _get_icon_svg(name)

    return (icon.replace("<color>", color).replace("<opacity>", str(opacity))), scale


def _get_icon_settings(state: dict, settings: ShowIconSettings) -> tuple[str, str, float, float]:
    # default value for the icon is the icon set in HA
    name = settings.get_icon() or state.get(icon_const.ATTRIBUTES, {}).get(icon_const.ATTRIBUTE_ICON, icon_const.EMPTY_STRING).replace("mdi:", icon_const.EMPTY_STRING)
    color = settings.get_color()
    scale = settings.get_scale()
    opacity = settings.get_opacity()

    #
    # Begin custom icon
    #

    customizations: list[IconCustomization] = settings.get_customizations()

    for customization in customizations:
        value = get_value(state, customization)

        custom_icon_value = customization.get_value()

        try:
            # if both values are numbers, convert them both to float
            # if one is int and one float, testing for equality might fail (21 vs 21.0 eg)
            value = float(value)
            custom_icon_value = float(custom_icon_value)
        except (ValueError, TypeError):
            pass

        operator = customization.get_operator()

        if ((operator == "==" and str(value) == str(custom_icon_value))
                or (operator == "!=" and str(value) != str(custom_icon_value))):
            name, color, scale, opacity = _replace_values(name, color, scale, opacity,
                                                          customization)

        if not isinstance(value, float):
            # other operators are only applicable to numbers
            continue

        try:
            custom_icon_value = float(custom_icon_value)
        except ValueError:
            logging.error("Could not convert custom value to float: %s",
                          custom_icon_value)
            continue

        if ((operator == "<" and value < custom_icon_value)
                or (operator == "<=" and value <= custom_icon_value)
                or (operator == ">" and value > custom_icon_value)
                or (operator == ">=" and value >= custom_icon_value)):
            name, color, scale, opacity = _replace_values(name, color, scale, opacity, customization)

    #
    # End custom icon
    #
    scale = round(scale / 100, 2)
    opacity = round(opacity / 100, 2)

    return name, color, scale, opacity


def get_value(state: dict, customization: IconCustomization):
    """
    Gets the current value that the customization references.
    """
    if customization.get_attribute() == icon_const.STATE:
        value = state[icon_const.STATE]
    else:
        value = state[icon_const.ATTRIBUTES].get(customization.get_attribute())

    return value


def _replace_values(name: str, color: str, scale: float, opacity: str, customization: IconCustomization):
    ret_name = name
    ret_color = color
    ret_scale = scale
    ret_opacity = opacity

    if customization.get_icon() is not None:
        ret_name = customization.get_icon()

    if customization.get_color() is not None:
        ret_color = customization.get_color()

    if customization.get_scale() is not None:
        ret_scale = customization.get_scale()

    if customization.get_opacity() is not None:
        ret_opacity = customization.get_opacity()

    return ret_name, ret_color, ret_scale, ret_opacity


def _get_icon_path(name: str) -> str:
    """
    Get the SVG path for the icon's MDI name.
    """
    if "mdi:" in name:
        name = name.replace("mdi:", icon_const.EMPTY_STRING)

    return MDI_ICONS.get(name, icon_const.EMPTY_STRING)


def _get_icon_svg(name: str) -> str:
    """
    Build a complete SVG string from an icons' name and path.
    """
    path = _get_icon_path(name)

    if not path:
        return icon_const.EMPTY_STRING

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 24 '
            f'24"><title>{name}</title><path d="{path}" fill="<color>" opacity="<opacity>" '
            f'/></svg>')