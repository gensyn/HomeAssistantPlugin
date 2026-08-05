"""
Module for text related operations.
"""
import logging as log
from typing import Any

from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.show_text import text_const
from HomeAssistantPlugin.actions.show_text.text_customization import TextCustomization
from HomeAssistantPlugin.actions.show_text.text_settings import ShowTextSettings


def get_text(state: dict, settings: ShowTextSettings, is_connected: bool) -> tuple[str, str, int, str, int, str]:
    """
    Determine text, position and font size to show on StreamDeck.
    """
    position = settings.get_position()
    text_size = settings.get_text_size()
    text_color = settings.get_text_color()
    outline_size = settings.get_outline_size()
    outline_color = settings.get_outline_color()

    if not is_connected:
        return "N/A", position, text_size, text_color, outline_size, outline_color

    attribute = settings.get_attribute()
    text_round = settings.get_round()
    round_precision = settings.get_round_precision()
    show_unit = settings.get_show_unit()
    line_break = settings.get_unit_line_break()

    text = _get_text(state, attribute, text_round, round_precision, show_unit, line_break)

    #
    # Begin custom text
    #

    customizations: list[TextCustomization] = settings.get_customizations()

    for customization in customizations:
        value = get_value(state, settings, customization)

        custom_text_value = customization.get_value()

        try:
            # if both values are numbers, convert them both to float
            # if one is int and one float, testing for equality might fail (21 vs 21.0 eg)
            value = float(value)
            custom_text_value = float(custom_text_value)
        except (ValueError, TypeError):
            pass

        operator = customization.get_operator()

        if ((operator == "==" and str(value) == str(custom_text_value))
                or (operator == "!=" and str(value) != str(custom_text_value))):
            (text, position, attribute, text_round, round_precision, text_size, text_color,
             outline_size, outline_color, show_unit, line_break) = _replace_values(
                text, position, attribute, text_round, round_precision, text_size, text_color,
                outline_size, outline_color, show_unit, line_break, customization)

        if not isinstance(value, float):
            # other operators are only applicable to numbers
            continue

        try:
            custom_text_value = float(custom_text_value)
        except ValueError:
            log.error("Could not convert custom value to float: %s",
                      custom_text_value)
            continue

        if ((operator == "<" and value < custom_text_value)
                or (operator == "<=" and value <= custom_text_value)
                or (operator == ">" and value > custom_text_value)
                or (operator == ">=" and value >= custom_text_value)):
            (text, position, attribute, text_round, round_precision, text_size, text_color,
             outline_size, outline_color, show_unit, line_break) = _replace_values(
                text, position, attribute, text_round, round_precision, text_size, text_color,
                outline_size, outline_color, show_unit, line_break, customization)

    #
    # End custom text
    #

    if attribute != text_const.CUSTOM_CUSTOM_TEXT:
        # get text a second time based on the customizations but only if no custom text is defined
        text = _get_text(state, attribute, text_round, round_precision, show_unit, line_break)

    return text, position, text_size, text_color, outline_size, outline_color


def get_value(state: dict, settings: ShowTextSettings, customization: TextCustomization) -> Any:
    """
    Gets the current value that the customization references.
    """
    attribute = settings.get_attribute()
    text_round = settings.get_round()
    round_precision = settings.get_round_precision()
    show_unit = settings.get_show_unit()

    customization_attribute = customization.get_attribute()

    if customization_attribute == text_const.STATE:
        value = state[text_const.STATE]
    elif customization_attribute == text_const.CUSTOM_TEXT_LENGTH:
        # get text without line break to calculate the correct length
        text = _get_text(state, attribute, text_round, round_precision, show_unit, False)
        value = len(text)
    else:
        value = state[customization_const.ATTRIBUTES].get(customization_attribute)

    return value


def _get_text(state: dict, attribute: str, text_round: bool, round_precision: int, show_unit: bool,
              line_break: bool) -> str:
    if attribute == text_const.STATE:
        text = _round_value(str(state.get(text_const.STATE)), text_round, round_precision)

        if show_unit:
            unit = state.get(customization_const.ATTRIBUTES, {}).get(customization_const.UNIT_OF_MEASUREMENT,
                                                                     text_const.EMPTY_STRING)

            if line_break:
                text = f"{text}\n{unit}"
            else:
                text = f"{text} {unit}"
    else:
        text = str(state.get(customization_const.ATTRIBUTES, {}).get(attribute, text_const.EMPTY_STRING))
        text = _round_value(text, text_round, round_precision)

    return text


def _replace_values(text: str, position: str, attribute: str, text_round: bool,
                    round_precision: int,
                    text_size: int, text_color: list[int], outline_size: int,
                    outline_color: list[int], show_unit: bool, line_break: bool,
                    customization: TextCustomization):
    ret_text = text
    ret_position = position
    ret_attribute = attribute
    ret_text_round = text_round
    ret_round_precision = round_precision
    ret_text_size = text_size
    ret_text_color = text_color
    ret_outline_size = outline_size
    ret_outline_color = outline_color
    ret_show_unit = show_unit
    ret_line_break = line_break

    if customization.get_custom_text() is not None:
        ret_text = customization.get_custom_text().replace("%s", text)
        ret_text = "\n".join(ret_text.split("\\n"))

    if customization.get_position() is not None:
        ret_position = customization.get_position()

    if customization.get_text_attribute() is not None:
        ret_attribute = customization.get_text_attribute()

    if customization.get_round() is not None:
        ret_text_round = customization.get_round()

    if customization.get_round_precision() is not None:
        ret_round_precision = customization.get_round_precision()

    if customization.get_text_size() is not None:
        ret_text_size = customization.get_text_size()

    if customization.get_text_color() is not None:
        ret_text_color = customization.get_text_color()

    if customization.get_outline_size() is not None:
        ret_outline_size = customization.get_outline_size()

    if customization.get_outline_color() is not None:
        ret_outline_color = customization.get_outline_color()

    if customization.get_show_unit() is not None:
        ret_show_unit = customization.get_show_unit()

    if customization.get_line_break() is not None:
        ret_line_break = customization.get_line_break()

    return (ret_text, ret_position, ret_attribute, ret_text_round, ret_round_precision,
            ret_text_size, ret_text_color, ret_outline_size, ret_outline_color, ret_show_unit,
            ret_line_break)


def _round_value(text: str, is_round: bool, precision: int) -> str:
    if not is_round or not _is_float(text):
        return text

    as_number = round(float(text), precision)

    if precision == 0:
        as_number = int(as_number)

    return str(as_number)


def _is_float(value: str) -> bool:
    if not "." in value:
        return False

    try:
        float(value)
        return True
    except ValueError:
        return False
