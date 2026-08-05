"""
The module for the Home Assistant customization row.
"""
from HomeAssistantPlugin.actions.cores.customization_core import customization_helper
from HomeAssistantPlugin.actions.cores.customization_core.customization_row import CustomizationRow
from HomeAssistantPlugin.actions.cores.customization_core.customization_settings import CustomizationSettings
from HomeAssistantPlugin.actions.show_icon import icon_const, icon_helper
from HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization


class IconRow(CustomizationRow):
    """
    Base for customization icon rows
    """

    def __init__(self, lm, customization: IconCustomization, customization_count: int, index: int, attributes: list,
                 state: dict, settings: CustomizationSettings):
        super().__init__(lm, customization_count, index, attributes, state, settings)

        current_value = icon_helper.get_value(state, customization)

        title = self._init_title(customization, current_value)

        if customization.get_icon() is not None:
            title += (f"\n{self.lm.get(icon_const.LABEL_ICON_ICON)} "
                      f"{customization.get_icon()}")

        if customization.get_color() is not None:
            color = customization_helper.convert_color_list_to_hex(customization.get_color())
            title += (f"\n{self.lm.get(icon_const.LABEL_ICON_COLOR)} "
                      f"{color}")

        if customization.get_scale() is not None:
            title += (f"\n{self.lm.get(icon_const.LABEL_ICON_SCALE)} "
                      f"{int(customization.get_scale())}")

        if customization.get_opacity() is not None:
            title += (f"\n{self.lm.get(icon_const.LABEL_ICON_OPACITY)} "
                      f"{int(customization.get_opacity())}")

        self.set_title(title)
