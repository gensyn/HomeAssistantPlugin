"""
The module for the Home Assistant action that is loaded in StreamController.
"""

import json
from json import JSONDecodeError

from HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore, requires_initialization, \
    set_substring_search
from HomeAssistantPlugin.actions.perform_action import perform_const
from HomeAssistantPlugin.actions.perform_action.parameters import parameters_helper
from HomeAssistantPlugin.actions.perform_action.perform_settings import PerformActionSettings

from GtkHelper.GenerativeUI.ComboRow import ComboRow
from GtkHelper.GenerativeUI.ExpanderRow import ExpanderRow
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.EventAssigner import EventAssigner


class PerformAction(BaseCore):
    """Action to be loaded by StreamController."""

    def __init__(self, *args, **kwargs):
        # Must be set before create_ui_elements in BaseCore is called
        self.action_combo = None
        self.parameters_expander = None
        super().__init__(settings_implementation=PerformActionSettings, track_entity=False, *args, **kwargs)

    def on_ready(self) -> None:
        """Set up action when StreamController has finished loading."""
        super().on_ready()

        if not self.plugin_base.backend.is_connected():
            return

        self._load_actions()
        self._reload()

    @requires_initialization
    def _perform_action(self, _) -> None:
        """Call the action stated in the settings."""
        domain = self.settings.get_domain()
        action = self.settings.get_action()
        if not domain or not action:
            return

        parameters = {}
        for parameter, value in self.settings.get_parameters().items():
            try:
                # try to create a dict or list from the value
                value = json.loads(value)
            except (JSONDecodeError, TypeError):
                # if it doesn't work just keep it as is
                pass
            parameters[parameter] = value

        entity = self.settings.get_entity()

        self.plugin_base.backend.perform_action(domain, action, entity, parameters)

    def _create_event_assigner(self) -> None:
        self.add_event_assigner(EventAssigner(
            id=perform_const.ACTION_ID,
            ui_label=perform_const.ACTION_NAME,
            default_events=[Input.Key.Events.DOWN],
            callback=self._perform_action
        ))

    def get_config_rows(self) -> list:
        """Get the rows to be displayed in the UI."""
        return [self.domain_combo.widget, self.action_combo.widget, self.entity_combo.widget,
                self.parameters_expander.widget]

    def create_ui_elements(self) -> None:
        """Get all action rows."""
        super().create_ui_elements()
        self.action_combo: ComboRow = ComboRow(
            self, perform_const.SETTING_ACTION_ACTION, perform_const.EMPTY_STRING, [],
            perform_const.LABEL_SERVICE_SERVICE, enable_search=True,
            on_change=self._on_change_action, can_reset=False,
            complex_var_name=True
        )
        set_substring_search(self.action_combo)

        self.parameters_expander: ExpanderRow = ExpanderRow(
            self, perform_const.EMPTY_STRING, False,
            title=perform_const.LABEL_SERVICE_PARAMETERS, can_reset=False,
            auto_add=False
        )

    @requires_initialization
    def on_change_domain(self, _, domain, old_domain):
        """Execute when the domain is changed."""
        super().on_change_domain(_, domain, old_domain)

        domain = str(domain) if domain is not None else None
        if domain:
            self._load_actions()

        self.set_enabled_disabled()

    @requires_initialization
    def on_change_entity(self, _, entity, old_entity):
        """Execute when the entity is changed."""
        entity = str(entity) if entity is not None else None
        old_entity = str(old_entity) if old_entity is not None else None

        if old_entity == entity:
            return

        super().on_change_entity(_, entity, old_entity)

        if entity:
            parameters_helper.load_parameters(self)

        self._reload()

    @requires_initialization
    def _on_change_action(self, _, action, old_action) -> None:
        """Execute when the action is changed."""
        action = str(action) if action is not None else None
        old_action = str(old_action) if old_action is not None else None

        if old_action == action:
            return

        self.settings.clear_parameters()
        parameters_helper.load_parameters(self)
        self._reload()

    @requires_initialization
    def _load_actions(self) -> None:
        """
        Load actions from Home Assistant.
        """
        action = self.settings.get_action()
        actions_dict = self.plugin_base.backend.get_actions(
            str(self.domain_combo.get_selected_item())
        )
        actions = list(actions_dict.keys())
        if action is not None and action not in actions:
            actions.append(action)
        actions = [a for a in actions if a is not None]
        self.action_combo.populate(actions, action, update_settings=True, trigger_callback=False)
        parameters_helper.load_parameters(self)

    @requires_initialization
    def set_enabled_disabled(self) -> None:
        """
        Set the active/inactive state for all rows.
        """
        domain = self.settings.get_domain()
        is_domain_set = bool(domain)

        if not is_domain_set:
            self.action_combo.widget.set_sensitive(False)
            self.action_combo.widget.set_subtitle(self.lm.get(perform_const.LABEL_SERVICE_NO_DOMAIN))
            self.parameters_expander.widget.set_sensitive(False)
            self.parameters_expander.widget.set_subtitle(self.lm.get(perform_const.LABEL_SERVICE_NO_DOMAIN))
        elif self.action_combo.get_item_amount() == 0:
            self.action_combo.widget.set_sensitive(False)
            self.action_combo.widget.set_subtitle(self.lm.get(perform_const.LABEL_SERVICE_NO_ACTIONS))
            self.parameters_expander.widget.set_sensitive(False)
            self.parameters_expander.widget.set_subtitle(self.lm.get(perform_const.LABEL_SERVICE_NO_ACTIONS))
        else:
            self.action_combo.widget.set_sensitive(True)
            self.action_combo.widget.set_subtitle(perform_const.EMPTY_STRING)

            if len(self.parameters_expander.widget.get_rows()) == 0:
                self.parameters_expander.widget.set_sensitive(False)
                self.parameters_expander.set_expanded(False)
                self.parameters_expander.widget.set_subtitle(self.lm.get(perform_const.LABEL_SERVICE_NO_PARAMETERS))
            else:
                self.parameters_expander.widget.set_sensitive(True)
                self.parameters_expander.set_expanded(True)
                self.parameters_expander.widget.set_subtitle(perform_const.EMPTY_STRING)

            action = self.settings.get_action()
            actions = self.plugin_base.backend.get_actions(
                str(self.domain_combo.get_selected_item())
            )
            has_target = bool(actions.get(action, {}).get(perform_const.TARGET))
            self.entity_combo.widget.set_sensitive(has_target)

    @requires_initialization
    def _get_domains(self) -> list[str]:
        """This class needs all domains that provide actions in Home Assistant."""
        return self.plugin_base.backend.get_domains_for_actions()
