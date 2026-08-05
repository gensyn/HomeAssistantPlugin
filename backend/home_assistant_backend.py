"""
Module for the Home Assistant backend.
"""

from threading import Thread
from time import sleep
from typing import Callable, Any, Optional

from HomeAssistantPlugin.backend import backend_const
from HomeAssistantPlugin.backend.home_assistant_websocket import HomeAssistantWebsocket
from gi.repository import GLib
from loguru import logger as log


class HomeAssistantBackend:
    """
    Defines the Home Assistant backend.
    """

    def __init__(self, host: str, port: str, ssl: bool, verify_certificate: bool, token: str):
        self._websocket: Optional[HomeAssistantWebsocket] = None
        self._entities: dict[str, dict[str, Any]] = {}
        self._actions: dict[str, dict[str, Any]] = {}
        self._connection_status_callback: Callable = lambda _1, _2=None: None
        self._keep_alive_thread: Optional[Thread] = None
        self._retry_connect_thread: Optional[Thread] = None
        self._action_ready_callbacks: set[Callable] = set()

        self._host: str = backend_const.EMPTY_STRING
        self.set_host(host)
        self._port: str = backend_const.EMPTY_STRING
        self.set_port(port)
        self._ssl: bool = True
        self.set_ssl(ssl)
        self._verify_certificate: bool = True
        self.set_verify_certificate(verify_certificate)
        self._token: str = backend_const.EMPTY_STRING
        self.set_token(token)

        self.connect()

    def set_host(self, host: str) -> None:
        """Set the Home Assistant host."""
        self._host = host.split(backend_const.DOUBLE_SLASH, 1)[-1]

    def set_port(self, port: str) -> None:
        """Set the Home Assistant port."""
        self._port = port

    def set_ssl(self, ssl: bool) -> None:
        """Set whether Home Assistant uses SSL."""
        self._ssl = ssl

    def set_verify_certificate(self, verify_certificate: bool) -> None:
        """Set whether the certificate should be verified."""
        self._verify_certificate = verify_certificate

    def set_token(self, token: str) -> None:
        """Set the Home Assistant token."""
        self._token = token

    def set_connection_status_callback(self, callback: Callable) -> None:
        """Set a callback to be called when the connection state changes."""
        self._connection_status_callback = callback

    def connect(self) -> None:
        """Connect to Home Assistant."""
        self.disconnect()

        if not self._host or not self._token or not self._port:
            return

        self._connection_status_callback(backend_const.CONNECTING)

        websocket_host = (
            f'{backend_const.PROTO_SSL if self._ssl else backend_const.PROTO}{self._host}:{self._port}{backend_const.HASS_WEBSOCKET_API}'
        )

        self._websocket = HomeAssistantWebsocket(
            url=websocket_host, token=self._token,
            verify_certificate=self._verify_certificate, on_event_message=self._on_event_message,
            on_connected=self._on_connect, on_close=self._on_disconnect
        )
        Thread(target=self._websocket.run_forever, daemon=True).start()

    def disconnect(self) -> None:
        """Disconnect from Home Assistant."""
        if self._websocket is not None:
            self._websocket.connected = False
            self._websocket.close()
        self._websocket = None
        self._connection_status_callback(backend_const.NOT_CONNECTED)

    def _readd_tracked_entities(self, _=None) -> None:
        if not self._entities:
            return

        # if the connection was lost we might need to resubscribe to entity events
        for domain_entry in self._entities.values():
            for entity, entity_settings in domain_entry.items():
                if entity_settings.get(backend_const.ACTIONS):
                    # the order here is important
                    # first save the existing actions
                    actions = entity_settings[backend_const.ACTIONS]
                    # then reset the entity settings
                    entity_settings[backend_const.SUBSCRIPTION_ID] = -1
                    entity_settings[backend_const.ACTIONS] = set()
                    # then re-add the actions
                    for action in actions:
                        self.add_tracked_entity(entity, action)

    def _on_connect(self) -> None:
        self._connection_status_callback(backend_const.CONNECTED)
        log.info(backend_const.INFO_CONNECTED)
        self._load_entities()
        self._load_actions()
        self._readd_tracked_entities()

        for ready in self._action_ready_callbacks:
            GLib.idle_add(ready)

    def _on_event_message(self, message: dict) -> None:
        new_state = (
            message
            .get(backend_const.FIELD_EVENT, {})
            .get(backend_const.VARIABLES, {})
            .get(backend_const.TRIGGER, {})
            .get(backend_const.TO_STATE, {})
        )
        if not new_state:
            entity_id = (
                message
                .get(backend_const.FIELD_EVENT, {})
                .get(backend_const.VARIABLES, {})
                .get(backend_const.TRIGGER, {})
                .get(backend_const.FROM_STATE, {})
                .get(backend_const.ENTITY_ID)
            )
            entity_settings = self._entities.get(entity_id.split(backend_const.DOT)[0], {}).get(entity_id)
            if entity_settings is None:
                return
            actions = entity_settings.get(backend_const.ACTIONS, set())
            for action_entity_updated in actions:
                GLib.idle_add(action_entity_updated)
            return

        entity_id = new_state.get(backend_const.ENTITY_ID)
        domain = entity_id.split(backend_const.DOT)[0]
        entity_settings = self._entities.get(domain, {}).get(entity_id)
        if entity_settings is None:
            return
        actions = entity_settings.get(backend_const.ACTIONS, set())
        state = new_state.get(backend_const.STATE)
        attributes = new_state.get(backend_const.ATTRIBUTES, {})

        self._entities[domain][entity_id][backend_const.STATE] = state
        self._entities[domain][entity_id][backend_const.ATTRIBUTES] = attributes

        update_state = {
            backend_const.STATE: state,
            backend_const.ATTRIBUTES: attributes,
            backend_const.HA_CONNECTED: self.is_connected(),
        }

        if not actions:
            log.warning(backend_const.WARNING_NOT_SUBSCRIBED.format(entity_id))

        for action_entity_updated in actions:
            GLib.idle_add(action_entity_updated, update_state)

    def _on_disconnect(self, websocket: HomeAssistantWebsocket) -> None:
        if websocket != self._websocket:
            # the call comes from an obsolete websocket instance
            return
        log.info(backend_const.INFO_DISCONNECTED)
        for ready in self._action_ready_callbacks:
            GLib.idle_add(ready)
        sleep(backend_const.RECONNECT_INTERVAL)
        if websocket == self._websocket:
            # the websocket instance is still the same, so we can try to reconnect
            self.connect()

    def get_domains_for_entities(self) -> list[str]:
        """Get a list of all domains known to Home Assistant."""
        if self._entities:
            return list(self._entities.keys())
        if not self.is_connected():
            return []
        self._load_entities()
        return list(self._entities.keys())

    def get_domains_for_actions(self) -> list[str]:
        """Get a list of all domains known to Home Assistant."""
        if self._actions:
            return list(self._actions.keys())
        if not self.is_connected():
            return []
        self._load_actions()
        return list(self._actions.keys())

    def get_entity(self, entity_id: str) -> dict[str, Any]:
        """Return the entity state with the requested name."""
        entity_fallback_dict = {
            backend_const.STATE: backend_const.NA,
            backend_const.ATTRIBUTES: {},
            backend_const.HA_CONNECTED: self.is_connected(),
        }
        if not entity_id or backend_const.DOT not in entity_id:
            return entity_fallback_dict

        domain = entity_id.split(backend_const.DOT)[0]
        entity_dict = self._entities.get(domain, {}).get(entity_id, entity_fallback_dict)
        entity_dict[backend_const.HA_CONNECTED] = self.is_connected()
        return entity_dict

    def _load_entities(self) -> None:
        """Loads the domains and entities from Home Assistant."""
        success, result, error = self._websocket.send_and_recv(backend_const.GET_STATES)

        if not success:
            log.error(backend_const.ERROR_STATES.format(error))
            self._entities = {}
            return

        states: list[dict] = result

        entities: dict[str, dict[str, Any]] = {}

        for entity in states:
            entity_id = entity.get(backend_const.ENTITY_ID)
            domain = entity_id.split(backend_const.DOT)[0]
            if domain not in entities:
                entities[domain] = {}
            entities[domain][entity_id] = {
                backend_const.STATE: entity.get(backend_const.STATE, backend_const.OFF),
                backend_const.ATTRIBUTES: entity.get(backend_const.ATTRIBUTES, {}),
                backend_const.ACTIONS: set(),
                backend_const.SUBSCRIPTION_ID: -1,
            }

        if self._entities:
            for domain, domain_entry in self._entities.items():
                for entity_id in domain_entry.keys():
                    if entities.get(domain, {}).get(entity_id):
                        entities[domain][entity_id][backend_const.ACTIONS] = domain_entry[entity_id].get(
                            backend_const.ACTIONS, set())
                        entities[domain][entity_id][backend_const.SUBSCRIPTION_ID] = domain_entry[
                            entity_id
                        ].get(backend_const.SUBSCRIPTION_ID, -1)

        self._entities = entities

    def get_entities(self, domain: str) -> list[str]:
        """Return a list of all entities known to Home Assistant."""
        if not domain:
            return []
        if self._entities:
            return list(self._entities.get(domain, {}).keys())
        self._load_entities()
        return list(self._entities.get(domain, {}).keys())

    def _load_actions(self) -> None:
        success, result, error = self._websocket.send_and_recv(backend_const.GET_SERVICES)

        if not success:
            log.error(backend_const.ERROR_SERVICES.format(error))
            self._actions = {}
            return

        self._actions = result

    def get_actions(self, domain: str) -> dict[str, dict[str, Any]]:
        """Return all actions known to Home Assistant for the domain."""
        if not self._actions:
            self._load_actions()
        if not self._actions:
            return {}
        return self._actions.get(domain, {})

    def perform_action(
            self, domain: str, service: str, entity_id: Optional[str], data: Optional[dict[str, Any]] = None
    ) -> None:
        """Calls a Home Assistant service."""
        if not self.is_connected():
            return

        message = self._websocket.create_message(backend_const.CALL_SERVICE)
        message[backend_const.DOMAIN] = domain
        message[backend_const.SERVICE] = service
        message[backend_const.TARGET] = {backend_const.ENTITY_ID: entity_id} if entity_id else {}
        message[backend_const.SERVICE_DATA] = data if data else {}

        self._websocket.send(message)

    def add_action_ready_callback(self, on_ready: Callable) -> None:
        """Register a callback to be called when the action is ready."""
        self._action_ready_callbacks.add(on_ready)

    def remove_action_ready_callback(self, on_ready: Callable) -> None:
        """Deregister a callback that was registered to be called when the action is ready."""
        self._action_ready_callbacks.discard(on_ready)

    def add_tracked_entity(
            self, entity_id: str, action_entity_updated: Callable
    ) -> None:
        """Register an entity with the Home Assistant websocket to be notified when the entity is updated."""
        if not entity_id:
            return

        if not self.is_connected():
            return

        if not self._entities:
            self._load_entities()

        domain = entity_id.split(backend_const.DOT)[0]
        entity_settings = self._entities.get(domain, {}).get(entity_id, {})
        if not entity_settings:
            # entity doesn't exist (anymore)
            return

        if action_entity_updated in entity_settings.get(backend_const.ACTIONS, set()):
            # action already registered
            return

        entity_settings.get(backend_const.ACTIONS).add(action_entity_updated)

        if entity_settings.get(backend_const.SUBSCRIPTION_ID) > -1:
            # already subscribed to entity events
            return

        message = self._websocket.create_message(backend_const.SUBSCRIBE_TRIGGER)
        message[backend_const.TRIGGER] = {backend_const.PLATFORM: backend_const.STATE,
                                          backend_const.ENTITY_ID: entity_id}
        self._websocket.send(message)
        entity_settings[backend_const.SUBSCRIPTION_ID] = message[backend_const.ID]

    def remove_tracked_entity(self, entity_id: str, action_entity_updated: Callable) -> None:
        """Deregister a previously registered entity."""
        if not entity_id:
            return

        if not self.is_connected():
            return

        domain = entity_id.split(backend_const.DOT)[0]
        entity_settings = self._entities.get(domain, {}).get(entity_id)
        if entity_settings is None:
            return
        entity_settings.get(backend_const.ACTIONS, set()).discard(action_entity_updated)

        if len(entity_settings.get(backend_const.ACTIONS, set())) > 0:
            # the entity is still attached to another key, so keep the trigger subscription
            return

        message = self._websocket.create_message(backend_const.UNSUBSCRIBE_EVENTS)
        message[backend_const.SUBSCRIPTION_ID] = entity_settings[backend_const.SUBSCRIPTION_ID]
        self._websocket.send(message)
        entity_settings[backend_const.SUBSCRIPTION_ID] = -1

    def is_connected(self) -> bool:
        """Check if the backend is connected to Home Assistant."""
        return self._websocket and self._websocket.connected
