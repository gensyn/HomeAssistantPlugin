import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction


class TestPerformActionOnReady(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.on_ready')
    @patch.object(PerformAction, '_load_actions')
    @patch.object(PerformAction, '_reload')
    def test_on_ready_not_connected(self, reload_mock, load_actions_mock, on_ready_mock, _):
        backend_mock = Mock()
        backend_mock.is_connected = Mock(return_value=False)

        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = PerformAction()
        instance.plugin_base = plugin_base_mock
        instance.on_ready()

        on_ready_mock.assert_called_once()
        load_actions_mock.assert_not_called()
        reload_mock.assert_not_called()

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.on_ready')
    @patch.object(PerformAction, '_load_actions')
    @patch.object(PerformAction, '_reload')
    def test_on_ready_success(self, reload_mock, load_actions_mock, on_ready_mock, _):
        backend_mock = Mock()
        backend_mock.is_connected = Mock(return_value=True)

        plugin_base_mock = Mock()
        plugin_base_mock.backend = backend_mock

        instance = PerformAction()
        instance.plugin_base = plugin_base_mock
        instance.on_ready()

        on_ready_mock.assert_called_once()
        load_actions_mock.assert_called_once()
        reload_mock.assert_called_once()

