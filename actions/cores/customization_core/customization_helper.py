"""
Module for helper functions.
"""
import gi

gi.require_version("Gdk", "4.0")
from gi.repository.Gdk import RGBA


def convert_color_list_to_rgba(color: tuple[int, int, int, int]) -> RGBA:
    """
    Converts a list with RGB values to an RGBA object.
    The alpha value is always set to 1.
    :param color: the color list to convert
    :return: the RGBA color
    """
    rgba = RGBA()
    rgba.red = color[0] / 255
    rgba.green = color[1] / 255
    rgba.blue = color[2] / 255
    rgba.alpha = 1
    return rgba


def convert_rgba_to_color_list(rgba: RGBA) -> tuple[int, int, int, int]:
    """
    Converts an RGBA object to a list with RGB values.
    The alpha value is always set to 255.
    :param rgba: the RGBA value to convert
    :return: the color list
    """
    return int(rgba.red * 255), int(rgba.green * 255), int(rgba.blue * 255), 255


def convert_color_list_to_hex(color: tuple[int, int, int, int]) -> str:
    """
    Converts a tuple with RGBA values to a hex string representation.
    :param color: the color to convert
    :return: the color as a hex string
    """
    return f'#{int(color[0]):02X}{int(color[1]):02X}{int(color[2]):02X}'
