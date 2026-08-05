import sys
import unittest
from pathlib import Path
from ssl import CERT_NONE
from unittest.mock import patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.backend import backend_const
from HomeAssistantPlugin.backend.home_assistant_websocket import HomeAssistantWebsocket


class TestWebsocketRunForever(unittest.TestCase):

    @patch("HomeAssistantPlugin.backend.home_assistant_websocket.WebSocketApp.run_forever")
    def test_run_forever_verify_certificate(self, websocket_app_mock):
        instance = HomeAssistantWebsocket(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, True, None, None, None)
        instance.run_forever()

        websocket_app_mock.assert_called_once_with(sslopt={})

    @patch("HomeAssistantPlugin.backend.home_assistant_websocket.WebSocketApp.run_forever")
    def test_run_forever_dont_verify_certificate(self, websocket_app_mock):
        instance = HomeAssistantWebsocket(backend_const.EMPTY_STRING, backend_const.EMPTY_STRING, False, None, None, None)
        instance.run_forever()

        websocket_app_mock.assert_called_once_with(sslopt={backend_const.CERT_REQS: CERT_NONE})

