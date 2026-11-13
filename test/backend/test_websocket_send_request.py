import json
import sys
import unittest
from pathlib import Path
from queue import Queue
from unittest.mock import patch, Mock

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.backend import backend_const
from HomeAssistantPlugin.backend.home_assistant_websocket import HomeAssistantWebsocket


class TestWebsocketSendRequest(unittest.TestCase):

    def _create(self):
        return HomeAssistantWebsocket(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, Mock(), None, Mock())

    def test_send_request_not_connected(self):
        instance = self._create()
        on_response = Mock()

        with patch.object(HomeAssistantWebsocket, 'send') as send_mock:
            self.assertFalse(instance.send_request(backend_const.GET_STATES, on_response))

        send_mock.assert_not_called()
        self.assertEqual({}, instance._pending_requests)

    def test_send_request_response_matched_by_id(self):
        instance = self._create()
        instance.connected = True
        on_response = Mock()

        with patch.object(HomeAssistantWebsocket, 'send') as send_mock:
            self.assertTrue(instance.send_request(backend_const.GET_STATES, on_response))

        message = send_mock.call_args[0][0]
        other_id = message[backend_const.ID] + 1

        instance._on_message(None, json.dumps(
            {backend_const.ID: other_id, backend_const.FIELD_TYPE: backend_const.FIELD_RESULT,
             backend_const.FIELD_SUCCESS: True, backend_const.FIELD_RESULT: []}))
        on_response.assert_not_called()

        instance._on_message(None, json.dumps(
            {backend_const.ID: message[backend_const.ID], backend_const.FIELD_TYPE: backend_const.FIELD_RESULT,
             backend_const.FIELD_SUCCESS: True, backend_const.FIELD_RESULT: [1]}))
        on_response.assert_called_once_with(True, [1], backend_const.EMPTY_STRING)
        self.assertEqual({}, instance._pending_requests)

    def test_on_close_clears_pending_requests(self):
        instance = self._create()
        instance._pending_requests[1] = Mock()

        instance._on_close(None, None, None)

        self.assertEqual({}, instance._pending_requests)

    def test_send_and_recv_callback_runs_before_next_event(self):
        order = []
        instance = self._create()
        instance._on_event_message = lambda _: order.append("event")
        instance._pending[1] = Queue()
        instance._pending_callbacks[1] = lambda *_: order.append("snapshot")

        instance._on_message(None, json.dumps(
            {backend_const.ID: 1, backend_const.FIELD_TYPE: backend_const.FIELD_RESULT,
             backend_const.FIELD_SUCCESS: True, backend_const.FIELD_RESULT: []}))
        instance._on_message(None, json.dumps({backend_const.FIELD_TYPE: backend_const.FIELD_EVENT}))

        self.assertEqual(["snapshot", "event"], order)
