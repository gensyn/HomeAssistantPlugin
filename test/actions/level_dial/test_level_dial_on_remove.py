import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.level_dial.level_dial import LevelDial


class TestLevelDialOnRemove(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.on_remove')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_on_remove_cancels_batch_timer_and_clears_pending_state(self, init_mock, super_on_remove_mock):
        instance = LevelDial()
        timer_mock = Mock()
        instance._batch_timer = timer_mock
        instance._pending_command = ("light", "turn_on", "light.desk", {"brightness": 154})
        instance._pending_pct = 60

        instance.on_remove()

        timer_mock.cancel.assert_called_once()
        self.assertIsNone(instance._batch_timer)
        self.assertIsNone(instance._pending_command)
        self.assertIsNone(instance._pending_pct)
        super_on_remove_mock.assert_called_once()

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_send_pending_command_skips_when_disposed(self, _):
        instance = LevelDial()
        instance._disposed = True
        instance._batch_timer = Mock()
        instance._pending_command = ("light", "turn_on", "light.desk", {"brightness": 154})
        instance.plugin_base = Mock()

        instance._send_pending_command()

        instance.plugin_base.backend.perform_action.assert_not_called()
        self.assertIsNone(instance._batch_timer)
        self.assertIsNone(instance._pending_command)
