"""
The module for the Home Assistant customization row.
"""
from HomeAssistantPlugin.actions.cores.customization_core import customization_helper
from HomeAssistantPlugin.actions.cores.customization_core.customization_row import CustomizationRow
from HomeAssistantPlugin.actions.show_text import text_helper, text_const
from HomeAssistantPlugin.actions.show_text.text_customization import TextCustomization
from HomeAssistantPlugin.actions.show_text.text_settings import ShowTextSettings


class TextRow(CustomizationRow):
    """
    Base for customization icon rows
    """

    def __init__(self, lm, customization: TextCustomization, customization_count: int, index: int, attributes: list,
                 state: dict, settings: ShowTextSettings):
        super().__init__(lm, customization_count, index, attributes, state, settings)

        current_value = text_helper.get_value(state, settings, customization)

        title = self._init_title(customization, current_value)

        if customization.get_position() is not None:
            title += (f"\n{self.lm.get(text_const.LABEL_POSITION)} "
                      f"{customization.get_position()}")

        if customization.get_text_attribute() is not None:
            title += (f"\n{self.lm.get(text_const.LABEL_ATTRIBUTE)} "
                      f"{customization.get_text_attribute()}")
            if customization.get_custom_text() is not None:
                title += f" = \"{customization.get_custom_text()}\""

        if customization.get_round() is not None:
            title += (f"\n{self.lm.get(text_const.LABEL_ROUND)} "
                      f"{customization.get_round()}")

        if customization.get_round_precision() is not None:
            title += (f"\n{self.lm.get(text_const.LABEL_ROUND_PRECISION)} "
                      f"{customization.get_round_precision()}")

        if customization.get_text_size() is not None:
            title += (f"\n{self.lm.get(text_const.LABEL_TEXT_SIZE)} "
                      f"{customization.get_text_size()}")

        if customization.get_text_color() is not None:
            color = customization_helper.convert_color_list_to_hex(customization.get_text_color())
            title += (f"\n{self.lm.get(text_const.LABEL_TEXT_COLOR)} "
                      f"{color}")

        if customization.get_outline_size() is not None:
            title += (f"\n{self.lm.get(text_const.LABEL_OUTLINE_SIZE)} "
                      f"{customization.get_outline_size()}")

        if customization.get_outline_color() is not None:
            color = customization_helper.convert_color_list_to_hex(customization.get_outline_color())
            title += (f"\n{self.lm.get(text_const.LABEL_OUTLINE_COLOR)} "
                      f"{color}")

        if customization.get_show_unit() is not None:
            title += (f"\n{self.lm.get(text_const.LABEL_SHOW_UNIT_SHORT)} "
                      f"{customization.get_show_unit()}")

        if customization.get_line_break() is not None:
            title += (f"\n{self.lm.get(text_const.LABEL_UNIT_LINE_BREAK_SHORT)} "
                      f"{customization.get_line_break()}")

        self.set_title(title)
