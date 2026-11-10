"""Module to manage the connection to Home Assistant via WebSocket."""

import json
from ssl import CERT_NONE, SSLEOFError
from queue import Empty, Queue
from threading import current_thread, Thread
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

RESPONSE_TIMEOUT = 10


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
        self._ws_thread: Thread | None = None
        self._pending: dict[int, Queue] = {}

    def run_forever(self) -> None:
        """Start the WebSocketApp."""
        ssl_opt = {}
        if not self._verify_certificate:
            ssl_opt[backend_const.CERT_REQS] = CERT_NONE
        self._ws_thread = current_thread()
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
        self._pending_requests.clear()
        self._on_close_callback(self)

    def _on_message(self, _, message: str) -> None:
        """Handle a message that was received from Home Assistant."""
        if not message:
            # received an empty message - happens when Home Assistants shuts down; ignore
            return

        message_dict = json.loads(message)
        message_type = message_dict.get(backend_const.FIELD_TYPE)

        pending = self._pending.get(message_dict.get(backend_const.ID))
        if pending is not None and backend_const.FIELD_RESULT == message_type:
            pending.put(message)
            return

        if backend_const.FIELD_EVENT == message_type:
            self._on_event_message(message_dict)
            return

        if backend_const.FIELD_RESULT == message_type:
            on_response = self._pending_requests.pop(message_dict.get(backend_const.ID), None)
            if on_response is not None:
                on_response(
                    message_dict.get(backend_const.FIELD_SUCCESS, False),
                    message_dict.get(backend_const.FIELD_RESULT, backend_const.EMPTY_STRING),
                    message_dict.get(backend_const.FIELD_ERROR, backend_const.EMPTY_STRING),
                )
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

        message_dict = self.create_message(message)
        if self._ws_thread is None or current_thread() is self._ws_thread:
            self.send(message_dict, check_connected)
            response = self.sock.recv()
        else:
            # another thread is reading from the socket; wait for it to hand over the response
            message_id = message_dict[backend_const.ID]
            queue: Queue = Queue()
            self._pending[message_id] = queue
            try:
                self.send(message_dict, check_connected)
                response = queue.get(timeout=RESPONSE_TIMEOUT)
            except Empty:
                return False, backend_const.EMPTY_STRING, backend_const.EMPTY_STRING
            finally:
                self._pending.pop(message_id, None)
        success = _get_field_from_message(response, backend_const.FIELD_SUCCESS)
        result = _get_field_from_message(response, backend_const.FIELD_RESULT)
        error = _get_field_from_message(response, backend_const.FIELD_ERROR)
        return success, result, error

    def send_request(self, message_type: str, on_response: Callable) -> bool:
        """Send a request while connected and call on_response(success, result, error) from the receive loop.

        The response is matched by its message ID, so the receive loop remains the only reader of the socket."""
        if not self.connected:
            return False

        message = self.create_message(message_type)
        self._pending_requests[message[backend_const.ID]] = on_response
        self.send(message)
        return True

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
