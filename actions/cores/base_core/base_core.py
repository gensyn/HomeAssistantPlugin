"""The module for the Home Assistant action that is loaded in StreamController."""

from typing import List

from GtkHelper.GenerativeUI.ComboRow import ComboRow
from HomeAssistantPlugin.actions import const
from src.backend.PluginManager.ActionCore import ActionCore


def requires_initialization(func):
    def wrapper(self, *args, **kwargs):
        if not getattr(self, 'initialized', False):
            return None
        return func(self, *args, **kwargs)
    return wrapper


class BaseCore(ActionCore):
    """Action core for all Home Assistant Actions."""

    def __init__(self, settings_implementation, track_entity: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = None
        self.settings_implementation = settings_implementation
        self.initialized = False
        self.lm = self.plugin_base.locale_manager
        self.has_configuration = True
        self.track_entity = track_entity
        self._create_ui_elements()
        self._create_event_assigner()

    def on_ready(self) -> None:
        """Set up action when StreamController has finished loading."""
        self.settings = self.settings_implementation(self)
        self.initialized = True

        self.plugin_base.backend.add_action_ready_callback(self.on_ready)

        entity = self.settings.get_entity()
        if entity and self.track_entity:
            self.plugin_base.backend.add_tracked_entity(entity, self.refresh)

        self._load_domains()
        self._load_entities()

    @requires_initialization
    def on_remove(self) -> None:
        """Clean up after action was removed."""
        self.plugin_base.backend.remove_action_ready_callback(self.on_ready)

        if self.track_entity:
            self.plugin_base.backend.remove_tracked_entity(
                self.settings.get_entity(),
                self.refresh
            )
        self.refresh()

    def get_config_rows(self) -> List:
        """Get the rows to be displayed in the UI."""
        raise NotImplementedError("Must be implemented by subclasses.")

    def _create_ui_elements(self) -> None:
        """Get all entity rows."""
        self.domain_combo: ComboRow = ComboRow(
            self, const.SETTING_ENTITY_DOMAIN, const.EMPTY_STRING, [],
            const.LABEL_ENTITY_DOMAIN, enable_search=True,
            on_change=self._on_change_domain, can_reset=False,
            complex_var_name=True
        )

        self.entity_combo: ComboRow = ComboRow(
            self, const.SETTING_ENTITY_ENTITY, const.EMPTY_STRING, [],
            const.LABEL_ENTITY_ENTITY, enable_search=True,
            on_change=self._on_change_entity, can_reset=False,
            complex_var_name=True
        )

    @requires_initialization
    def _reload(self, *_):
        """Reload the action."""
        self._set_enabled_disabled()
        self.refresh()

    @requires_initialization
    def _on_change_domain(self, _, domain, old_domain):
        """Execute when the domain is changed."""
        domain = str(domain) if domain is not None else None
        old_domain = str(old_domain) if old_domain is not None else None

        if old_domain != domain:
            entity = self.settings.get_entity()
            if entity and self.track_entity:
                self.plugin_base.backend.remove_tracked_entity(entity, self.refresh)
            self.settings.reset(domain)
            self.entity_combo.remove_all_items()

        if domain:
            self._load_entities()

        self._set_enabled_disabled()

    @requires_initialization
    def _on_change_entity(self, _, entity, old_entity):
        """Execute when the entity is changed."""
        entity = str(entity) if entity is not None else None
        old_entity = str(old_entity) if old_entity is not None else None

        if old_entity and self.track_entity:
            self.plugin_base.backend.remove_tracked_entity(old_entity, self.refresh)

        if entity and self.track_entity:
            self.plugin_base.backend.add_tracked_entity(entity, self.refresh)

        self.refresh()
        self._set_enabled_disabled()

    @requires_initialization
    def refresh(self, state: dict = None) -> None:
        """
        Executed when an entity is updated to reflect the changes on the key.
        This does not need to do anything by default, but can be overridden by subclasses.
        :param state: The state of the entity, if available.
        """
        pass

    def _create_event_assigner(self) -> None:
        """
        Create the events that can be triggered in this action.
        This does not need to do anything by default, but can be overridden by subclasses.
        """
        pass

    @requires_initialization
    def _load_domains(self) -> None:
        """Load domains from Home Assistant."""
        domain = self.settings.get_domain()
        domains = self._get_domains()
        if domain is not None and domain not in domains:
            domains.append(domain)
        domains = [d for d in domains if d is not None]
        domains.sort()
        if domains != self._get_current_domains():
            self.domain_combo.populate(domains, domain, trigger_callback=False)

    @requires_initialization
    def _load_entities(self) -> None:
        """Load entities from Home Assistant."""
        entity = self.settings.get_entity()
        entities = self.plugin_base.backend.get_entities(
            str(self.domain_combo.get_selected_item())
        )
        if entity is not None and entity not in entities:
            entities.append(entity)
        entities = [e for e in entities if e is not None]
        entities.sort()
        if entities != self._get_current_entities():
            self.entity_combo.populate(entities, entity, trigger_callback=False)

    def _get_current_domains(self) -> List[str]:
        """Get the domains currently displayed in the domain combo."""
        return [
            str(self.domain_combo.get_item_at(i))
            for i in range(self.domain_combo.get_item_amount())
        ]

    def _get_current_entities(self) -> List[str]:
        """Get the entities currently displayed in the entity combo."""
        return [
            str(self.entity_combo.get_item_at(i))
            for i in range(self.entity_combo.get_item_amount())
        ]

    @requires_initialization
    def _set_enabled_disabled(self) -> None:
        """Set the active/inactive state for all rows."""
        domain = self.settings.get_domain()
        is_domain_set = bool(domain)
        self.entity_combo.set_sensitive(is_domain_set)

    def _get_domains(self) -> List[str]:
        """Get the domains available in Home Assistant."""
        raise NotImplementedError("Must be implemented by subclasses.")

    def _get_canvas_size(self) -> tuple:
        """
        Get the current canvas size for this input.
        :return: (width, height) of the canvas, or (1, 1) if unavailable.
        """
        try:
            return self.get_input().get_image_size()
        except (AttributeError, TypeError):
            return (1, 1)

    def get_generative_ui(self):
        return []
