"""The module for the Level Dial customization window."""

from functools import partial
from typing import Callable

from HomeAssistantPlugin.actions import const as base_const
from HomeAssistantPlugin.actions.cores.customization_core import customization_helper
from HomeAssistantPlugin.actions.cores.customization_core.customization_window import CustomizationWindow
from HomeAssistantPlugin.actions.level_dial import level_const
from HomeAssistantPlugin.actions.level_dial.level_customization import LevelDialCustomization
# Reuse the MDI icon list from the shared asset
from HomeAssistantPlugin.actions.show_icon import icon_helper


class LevelDialWindow(CustomizationWindow):
    """Window to customize level dial icon and color."""

    def __init__(self, lm, attributes: list, callback: Callable,
                 current: LevelDialCustomization = None, index: int = None):
        super().__init__(lm, attributes, callback, current, index)

        self.icons: list[str] = list(icon_helper.MDI_ICONS)

        self.set_title(lm.get(level_const.CUSTOMIZATION_WINDOW_TITLE))

        self.check_icon = self._create_check_button()
        self.check_color = self._create_check_button()

        label_icon = self._create_label(self.lm.get(level_const.LABEL_LEVEL_ICON))
        label_color = self._create_label(self.lm.get(level_const.LABEL_LEVEL_COLOR))

        self.icon = self._create_entry(self.check_icon)
        self.icon.set_margin_end(self.default_margin)
        self.connect_rows.append(
            partial(self.icon.connect, base_const.CONNECT_ACTIVATE, self.on_widget_changed))

        self.color = self._create_color_button(self.check_color)

        self.grid_fields.attach(self.check_icon, 2, 2, 1, 1)
        self.grid_fields.attach(label_icon, 3, 2, 1, 1)
        self.grid_fields.attach(self.icon, 4, 2, 1, 1)

        self.grid_fields.attach(self.check_color, 2, 3, 1, 1)
        self.grid_fields.attach(label_color, 3, 3, 1, 1)
        self.grid_fields.attach(self.color, 4, 3, 1, 1)

        self._after_init()

    def set_default_values(self) -> None:
        super().set_default_values()

        rgba = customization_helper.convert_color_list_to_rgba(level_const.DEFAULT_ICON_COLOR)
        self.color.set_rgba(rgba)

    def set_current_values(self) -> None:
        if not self.current:
            return

        super().set_current_values()

        self.icon.set_text(self.current.get_icon() or level_const.EMPTY_STRING)
        self.check_icon.set_active(self.current.get_icon() is not None)

        if self.current.get_color():
            rgba = customization_helper.convert_color_list_to_rgba(self.current.get_color())
            self.color.set_rgba(rgba)
        self.check_color.set_active(self.current.get_color() is not None)

    def on_add_button(self, *_, **__) -> None:
        if not super().on_add_button():
            return

        if self.check_icon.get_active():
            raw_icon = self.icon.get_text()

            if raw_icon.startswith("mdi:"):
                icon = raw_icon[4:]
            else:
                icon = raw_icon

            if icon not in self.icons:
                self.icon.add_css_class(level_const.ERROR)
                return
        else:
            icon = None

        if not self.check_icon.get_active() and not self.check_color.get_active():
            self.check_icon.add_css_class(level_const.ERROR)
            self.check_color.add_css_class(level_const.ERROR)
            return
        color = self.color.get_rgba() if self.check_color.get_active() else None
        color_list = customization_helper.convert_rgba_to_color_list(color) if color else None

        self.callback(customization=LevelDialCustomization(
            attribute=self.condition_attribute.get_selected_item().get_string(),
            operator=self.operator.get_selected_item().value,
            value=self.entry_value.get_text(), icon=icon, color=color_list), index=self.index)

        self.destroy()

    def on_widget_changed(self, *_, **__) -> None:
        super().on_widget_changed()

        self.icon.remove_css_class(level_const.ERROR)
        self.check_icon.remove_css_class(level_const.ERROR)
        self.check_color.remove_css_class(level_const.ERROR)
