"""Dial action for controlling Home Assistant entities via Stream Deck Plus dials."""

import json
import os
import threading
from io import BytesIO

# Available in the StreamController flatpak runtime; graceful fallback for unit tests
try:
    import cairosvg
    from PIL import Image
    from loguru import logger as log
except ImportError:
    cairosvg = None
    Image = None
    import logging

    log = logging.getLogger(__name__)

from GtkHelper.GenerativeUI.EntryRow import EntryRow
from GtkHelper.GenerativeUI.ScaleRow import ScaleRow
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.EventAssigner import EventAssigner
from HomeAssistantPlugin.actions.cores.customization_core import customization_helper
from HomeAssistantPlugin.actions.cores.customization_core.customization_core import CustomizationCore
from HomeAssistantPlugin.actions.cores.base_core.base_core import requires_initialization
from HomeAssistantPlugin.actions.level_dial import level_const
from HomeAssistantPlugin.actions.level_dial.level_customization import LevelDialCustomization
from HomeAssistantPlugin.actions.level_dial.level_row import LevelDialRow
from HomeAssistantPlugin.actions.level_dial.level_settings import LevelDialSettings
from HomeAssistantPlugin.actions.level_dial.level_window import LevelDialWindow

# Load MDI icons once at import time
_MDI_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "mdi-svg.json")
with open(_MDI_PATH, "r", encoding="utf-8") as _f:
    _MDI_ICONS: dict[str, str] = json.load(_f)

_ICON_CACHE: dict = {}


def _get_icon_image(icon_name: str, color_hex: str, opacity: float = 1.0):
    """Build a PIL Image from an MDI icon name, color, and opacity."""
    cache_key = f"{icon_name}:{color_hex}:{opacity}"
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key].copy()

    path_d = _MDI_ICONS.get(icon_name, "")
    if not path_d:
        return None

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 24 24">'
        f'<path d="{path_d}" fill="{color_hex}" opacity="{opacity}"/></svg>'
    )
    if cairosvg is None or Image is None:
        return None

    try:
        png_data = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=300, output_height=300)
        img = Image.open(BytesIO(png_data)).convert("RGBA")
        _ICON_CACHE[cache_key] = img
        return img.copy()
    except Exception as e:
        log.error("LevelDial icon render failed: {}", e)
        return None


def _get_entity_icon(state: dict, fallback: str) -> str:
    """Extract the MDI icon name from an entity's state attributes."""
    icon = state.get("attributes", {}).get("icon", "")
    if icon.startswith("mdi:"):
        icon = icon[4:]
    return icon if icon else fallback


def _evaluate_customizations(state: dict, customizations: list[LevelDialCustomization],
                             default_icon: str, default_color: str) -> tuple[str, str]:
    """Evaluate customization rules against current state, returning (icon_name, color_hex)."""
    icon_name = default_icon
    color_hex = default_color

    for customization in customizations:
        if customization.get_attribute() == "state":
            value = state.get("state")
        else:
            value = state.get("attributes", {}).get(customization.get_attribute())

        custom_value = customization.get_value()

        try:
            value = float(value)
            custom_value = float(custom_value)
        except (ValueError, TypeError):
            pass

        operator = customization.get_operator()
        matched = False

        if operator == "==" and str(value) == str(custom_value):
            matched = True
        elif operator == "!=" and str(value) != str(custom_value):
            matched = True
        elif isinstance(value, float):
            try:
                custom_value = float(custom_value)
            except (ValueError, TypeError):
                continue

            if ((operator == "<" and value < custom_value)
                    or (operator == "<=" and value <= custom_value)
                    or (operator == ">" and value > custom_value)
                    or (operator == ">=" and value >= custom_value)):
                matched = True

        if matched:
            if customization.get_icon() is not None:
                icon_name = customization.get_icon()
            if customization.get_color() is not None:
                color_hex = customization_helper.convert_color_list_to_hex(customization.get_color())

    return icon_name, color_hex


class LevelDial(CustomizationCore):
    """Dial action that controls Home Assistant entity levels (brightness, fan speed, etc.)."""

    def __init__(self, *args, **kwargs):
        # Must be set before create_ui_elements in BaseCore is called
        self.label_entry = None
        self.step_scale = None
        self.batch_delay_scale = None
        super().__init__(
            *args,
            window_implementation=LevelDialWindow,
            customization_implementation=LevelDialCustomization,
            row_implementation=LevelDialRow,
            settings_implementation=LevelDialSettings,
            track_entity=True,
            **kwargs
        )

    def _should_force_label(self, position: str) -> bool:
        """Check if we should bypass has_label_control for a position.

        LevelDial always owns the top label (display name).  For other
        positions it respects normal permission checks unless the control
        index is orphaned.
        """
        if position == "top":
            return True

        label_index = 0 if position == "top" else 1 if position == "center" else 2
        try:
            control_index = self.get_state().action_permission_manager.get_label_control_index(label_index)
            return self._is_control_orphaned(control_index)
        except (AttributeError, TypeError):
            return True

    def _is_control_orphaned(self, control_index) -> bool:
        """Check if a control index points to a non-existent action.

        SC does not clean up image-control-action or label-control-actions
        when an action is removed from a slot.
        """
        try:
            actions = self.page.get_all_actions_for_input(self.input_ident, self.state)
            return control_index is None or control_index >= len(actions)
        except (AttributeError, TypeError):
            return True

    def set_media(self, image=None, media_path=None, size: float = None,
                  valign: float = None, halign: float = None, fps: int = 30,
                  loop: bool = True, update: bool = True):
        """Override to reclaim image control when the index is orphaned."""
        original = self.has_image_control
        try:
            image_index = self.get_state().action_permission_manager.get_image_control_index()
            if self._is_control_orphaned(image_index):
                self.has_image_control = lambda: True
        except (AttributeError, TypeError):
            self.has_image_control = lambda: True
        try:
            super().set_media(image=image, media_path=media_path, size=size,
                              valign=valign, halign=halign, fps=fps, loop=loop, update=update)
        finally:
            self.has_image_control = original

    def set_label(self, text: str, position: str = "bottom", color: list = None,
                  font_family: str = None, font_size=None, outline_width: int = None,
                  outline_color: list = None, font_weight: int = None,
                  font_style: str = None, update: bool = True):
        """Override to handle orphaned label permissions.

        SC does not clean up label-control-actions when an action is removed.
        LevelDial always writes the top label and reclaims other positions
        when the control index points to a non-existent action.
        """
        if self._should_force_label(position):
            original = self.has_label_control
            self.has_label_control = lambda _: True
            try:
                super().set_label(text, position, color, font_family, font_size,
                                  outline_width, outline_color, font_weight, font_style, update)
            finally:
                self.has_label_control = original
        else:
            super().set_label(text, position, color, font_family, font_size,
                              outline_width, outline_color, font_weight, font_style, update)

    def on_ready(self) -> None:
        super().on_ready()
        self._reload()

    def get_config_rows(self) -> list:
        return [
            self.domain_combo.widget,
            self.entity_combo.widget,
            self.label_entry.widget,
            self.step_scale.widget,
            self.batch_delay_scale.widget,
            self.customization_expander.widget,
        ]

    def create_ui_elements(self) -> None:
        super().create_ui_elements()

        self.label_entry: EntryRow = EntryRow(
            self, level_const.SETTING_LEVEL_LABEL, level_const.DEFAULT_LABEL,
            title=level_const.LABEL_LEVEL_LABEL,
            on_change=self._reload, can_reset=False,
            complex_var_name=True
        )

        self.step_scale: ScaleRow = ScaleRow(
            self, level_const.SETTING_LEVEL_STEP, level_const.DEFAULT_STEP,
            level_const.MIN_STEP, level_const.MAX_STEP,
            title=level_const.LABEL_LEVEL_STEP,
            step=1, digits=0, on_change=self._reload, can_reset=False,
            complex_var_name=True
        )

        self.batch_delay_scale: ScaleRow = ScaleRow(
            self, level_const.SETTING_LEVEL_BATCH_DELAY, level_const.DEFAULT_BATCH_DELAY,
            level_const.MIN_BATCH_DELAY, level_const.MAX_BATCH_DELAY,
            title=level_const.LABEL_LEVEL_BATCH_DELAY,
            step=10, digits=0, on_change=self._reload, can_reset=False,
            complex_var_name=True
        )

    def _create_event_assigner(self) -> None:
        self.add_event_assigner(EventAssigner(
            id="Dial Turn CW",
            ui_label="Dial Turn CW",
            default_events=[Input.Dial.Events.TURN_CW],
            callback=self._on_dial_turn_cw
        ))
        self.add_event_assigner(EventAssigner(
            id="Dial Turn CCW",
            ui_label="Dial Turn CCW",
            default_events=[Input.Dial.Events.TURN_CCW],
            callback=self._on_dial_turn_ccw
        ))
        self.add_event_assigner(EventAssigner(
            id="Dial Short Up",
            ui_label="Dial Short Up",
            default_events=[Input.Dial.Events.SHORT_UP],
            callback=self._on_dial_short_up
        ))

    @requires_initialization
    def _on_dial_turn_cw(self, _=None) -> None:
        self._adjust_level(1)

    @requires_initialization
    def _on_dial_turn_ccw(self, _=None) -> None:
        self._adjust_level(-1)

    @requires_initialization
    def _on_dial_short_up(self, _=None) -> None:
        entity = self.settings.get_entity()
        if not entity:
            return
        domain = entity.split(".")[0]
        config = level_const.DOMAIN_CONFIGS.get(domain)
        if not config:
            return
        self.plugin_base.backend.perform_action(domain, config["toggle_service"], entity, {})

    def _adjust_level(self, direction: int) -> None:
        entity = self.settings.get_entity()
        if not entity:
            return

        domain = entity.split(".")[0]
        config = level_const.DOMAIN_CONFIGS.get(domain)
        if not config:
            return

        state = self.plugin_base.backend.get_entity(entity)
        if state is None:
            return

        step = self.settings.get_step()
        level_range = config["level_max"] - config["level_min"]

        # Work in percentage space to avoid rounding accumulation.
        # Use pending percentage if we have one, otherwise convert from HA state.
        pending_pct = getattr(self, "_pending_pct", None)
        if pending_pct is None:
            reported = state.get("attributes", {}).get(config["level_attr"], 0) or 0
            pending_pct = (reported - config["level_min"]) / level_range * 100

        # Fine-grained 1% steps in the bottom 10%, or when a full step
        # down would cross into the bottom 10%
        pct_after = pending_pct + (step * direction)
        effective_step = 1 if pending_pct <= 10 or (direction < 0 and pct_after < 10) else step

        # Clamp to 1% floor (dial can't turn off — that's what toggle is for)
        new_pct = max(1, min(100, pending_pct + (effective_step * direction)))
        self._pending_pct = new_pct

        # Convert to native value for the HA command
        new_value = config["level_min"] + (new_pct / 100) * level_range
        if isinstance(config["level_max"], int):
            new_value = round(new_value)

        # Update the display immediately so the user sees feedback
        self.set_center_label(
            f"{round(new_pct)}%", color=[255, 255, 255], font_size=28,
            outline_width=3, outline_color=[0, 0, 0]
        )

        # Debounce the HA command — cancel any pending timer, start a new one
        batch_delay = self.settings.get_batch_delay()
        self._pending_command = (domain, config["set_service"], entity, {config["set_param"]: new_value})

        timer = getattr(self, "_batch_timer", None)
        if timer is not None:
            timer.cancel()

        if batch_delay <= 0:
            self._send_pending_command()
        else:
            self._batch_timer = threading.Timer(
                batch_delay / 1000.0, self._send_pending_command
            )
            self._batch_timer.start()

    def _send_pending_command(self) -> None:
        """Send the most recent pending command to Home Assistant."""
        cmd = getattr(self, "_pending_command", None)
        if cmd is None:
            return
        self._pending_command = None
        self._batch_timer = None
        domain, service, entity, params = cmd
        self.plugin_base.backend.perform_action(domain, service, entity, params)

    def refresh(self, state: dict = None) -> None:
        if not self.initialized:
            return

        # If we have an unsent command (debounce timer active), don't let
        # intermediate HA state updates override the pending target or display.
        if getattr(self, "_batch_timer", None) is not None:
            return

        # Clear pending target so _adjust_level re-syncs from HA state
        self._pending_pct = None
        entity = self.settings.get_entity()
        if not entity:
            self.set_top_label("")
            self.set_center_label("")
            self.set_media()
            return

        if state is None:
            state = self.plugin_base.backend.get_entity(entity)

        if state is None:
            self.set_top_label("")
            self.set_center_label("N/A")
            self.set_media()
            return

        # Label
        label = self.settings.get_label()
        if not label:
            label = state.get("attributes", {}).get("friendly_name", "")
        self.set_top_label(label, font_size=14)

        # Domain config
        domain = entity.split(".")[0]
        config = level_const.DOMAIN_CONFIGS.get(domain)
        if not config:
            self.set_center_label("?")
            self.set_media()
            return

        # Default icon from entity state, with domain-appropriate fallback
        default_icon = _get_entity_icon(state, config["fallback_icon"])

        # State & level
        entity_state = state.get("state", "off")
        level = state.get("attributes", {}).get(config["level_attr"])

        if entity_state in ("off", "unavailable", "unknown") or level is None:
            default_color = level_const.COLOR_OFF
        else:
            default_color = level_const.COLOR_ON

        # Apply customization rules (icon/color overrides based on state conditions)
        customizations = self.settings.get_customizations()
        icon_name, color_hex = _evaluate_customizations(
            state, customizations, default_icon, default_color
        )

        if entity_state in ("off", "unavailable", "unknown") or level is None:
            self.set_center_label(
                "Off", color=[100, 100, 100], font_size=28,
                outline_width=3, outline_color=[0, 0, 0]
            )
            icon_img = _get_icon_image(icon_name, color_hex, opacity=0.85)
        else:
            level_range = config["level_max"] - config["level_min"]
            pct = round((level - config["level_min"]) / level_range * 100)
            self.set_center_label(
                f"{pct}%", color=[255, 255, 255], font_size=28,
                outline_width=3, outline_color=[0, 0, 0]
            )
            icon_img = _get_icon_image(icon_name, color_hex, opacity=0.75)

        if icon_img:
            self.set_media(image=icon_img, size=0.75)

        self._load_customizations()
        self.set_enabled_disabled()

    @requires_initialization
    def set_enabled_disabled(self) -> None:
        super().set_enabled_disabled()
        domain = self.settings.get_domain()
        entity = self.settings.get_entity()
        has_entity = bool(domain) and bool(entity)

        if not has_entity:
            self.label_entry.widget.set_sensitive(False)
            self.step_scale.widget.set_sensitive(False)
            self.step_scale.widget.set_subtitle(
                self.lm.get(level_const.LABEL_LEVEL_NO_ENTITY)
            )
            self.batch_delay_scale.widget.set_sensitive(False)
            self.batch_delay_scale.widget.set_subtitle(
                self.lm.get(level_const.LABEL_LEVEL_NO_ENTITY)
            )
        else:
            self.label_entry.widget.set_sensitive(True)
            self.step_scale.widget.set_sensitive(True)
            self.step_scale.widget.set_subtitle(level_const.EMPTY_STRING)
            self.batch_delay_scale.widget.set_sensitive(True)
            self.batch_delay_scale.widget.set_subtitle(level_const.EMPTY_STRING)

    @requires_initialization
    def _get_domains(self) -> list[str]:
        available = set(self.plugin_base.backend.get_domains_for_entities())
        return [d for d in level_const.DOMAIN_CONFIGS if d in available]
