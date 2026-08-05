"""Module to manage the connection to Home Assistant via WebSocket."""

import json
from ssl import CERT_NONE, SSLEOFError
from time import sleep
from typing import Any, Callable

from HomeAssistantPlugin.backend import backend_const
from loguru import logger as log
from websocket import WebSocketApp, WebSocketException, WebSocketAddressException

ERRORS_TO_EXCEPT = (
    WebSocketException,
    WebSocketAddressException,
    ValueError,
    ConnectionResetError,
    BrokenPipeError,
    SSLEOFError,
)


class HomeAssistantWebsocket(WebSocketApp):
    """"Manages the connection to Home Assistant."""

    def __init__(self, url: str, token: str, verify_certificate: bool, on_event_message: Callable,
                 on_connected: Callable, on_close: Callable, *args, **kwargs):
        super().__init__(url=url, on_message=self._on_message, on_error=_on_error, on_close=self._on_close, *args,
                         **kwargs)
        self._url = url
        self._token = token
        self._verify_certificate = verify_certificate
        self._on_event_message = on_event_message
        self._on_connected_callback = on_connected
        self._on_close_callback = on_close
        self.connected = False
        self._message_id: int = 0

    def run_forever(self) -> None:
        """Start the WebSocketApp."""
        ssl_opt = {}
        if not self._verify_certificate:
            ssl_opt[backend_const.CERT_REQS] = CERT_NONE
        super().run_forever(sslopt=ssl_opt)

    def _auth(self) -> None:
        """Authenticated with Home Assistant."""
        self.send({backend_const.FIELD_TYPE: backend_const.AUTH, backend_const.ACCESS_TOKEN: self._token},
                  check_connected=False)
        auth_ok = json.loads(self.sock.recv()).get(backend_const.FIELD_TYPE)
        if not auth_ok or auth_ok != backend_const.AUTH_OK:
            log.error(backend_const.AUTH_ERROR)
            return

        success, result, _ = self.send_and_recv(backend_const.GET_CONFIG, check_connected=False)
        while not success or result.get(backend_const.STATE, backend_const.EMPTY_STRING) != backend_const.RUNNING:
            # Home Assistant hasn't finished starting yet so not all entities might have been initialized
            # try again later
            log.info(backend_const.ERROR_NOT_STARTED)
            sleep(backend_const.RECONNECT_INTERVAL)
            success, result, _ = self.send_and_recv(backend_const.GET_CONFIG, check_connected=False)

        self.connected = True
        self._on_connected_callback()

    def _on_close(self, _, __, ___) -> None:
        """Execute the respective callback when the connection to Home Assistant was closed."""
        self.connected = False
        self._on_close_callback(self)

    def _on_message(self, _, message: str) -> None:
        """Handle a message that was received from Home Assistant."""
        if not message:
            # received an empty message - happens when Home Assistants shuts down; ignore
            return

        message_dict = json.loads(message)
        message_type = message_dict.get(backend_const.FIELD_TYPE)

        if backend_const.FIELD_EVENT == message_type:
            self._on_event_message(message_dict)
            return

        if backend_const.AUTH_REQUIRED == message_type:
            self._auth()
            return

    def send(self, message: dict, check_connected: bool = True) -> None:
        """Convert the Dict to a string and send it to Home Assistant."""
        if check_connected and not self.connected:
            return

        super().send(json.dumps(message))

    def send_and_recv(
            self, message: str, check_connected: bool = True
    ) -> tuple[bool, Any, Any]:
        """Send a websocket message to Home Assistant and return the response."""
        if check_connected and not self.connected:
            return False, backend_const.EMPTY_STRING, backend_const.EMPTY_STRING

        self.send(self.create_message(message), check_connected)
        response = self.sock.recv()
        success = _get_field_from_message(response, backend_const.FIELD_SUCCESS)
        result = _get_field_from_message(response, backend_const.FIELD_RESULT)
        error = _get_field_from_message(response, backend_const.FIELD_ERROR)
        return success, result, error

    def create_message(self, message_type: str) -> dict[str, Any]:
        """Create a message that can be sent to the Home Assistant websocket."""
        self._message_id += 1
        return {backend_const.ID: self._message_id, backend_const.FIELD_TYPE: message_type}


def _on_error(_, error: Exception) -> None:
    """Log the error."""
    log.error(backend_const.ERROR_GENERIC.format(error))


def _get_field_from_message(message: str, field: str) -> Any:
    """Extracts the specified field from the message."""
    if not message:
        return backend_const.EMPTY_STRING
    try:
        parsed = json.loads(message)
        return parsed.get(field, backend_const.EMPTY_STRING)
    except json.JSONDecodeError:
        log.error(backend_const.ERROR_PARSE.format(message))
        return backend_const.EMPTY_STRING
