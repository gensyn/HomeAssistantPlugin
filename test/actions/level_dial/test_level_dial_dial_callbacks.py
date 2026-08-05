import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.level_dial.level_dial import LevelDial


class TestLevelDialDialCallbacks(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    @patch.object(LevelDial, '_adjust_level')
    def test_on_dial_turn_cw_calls_adjust_positive(self, adjust_mock, _):
        instance = LevelDial()
        instance.initialized = True
        instance._on_dial_turn_cw()

        adjust_mock.assert_called_once_with(1)

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    @patch.object(LevelDial, '_adjust_level')
    def test_on_dial_turn_ccw_calls_adjust_negative(self, adjust_mock, _):
        instance = LevelDial()
        instance.initialized = True
        instance._on_dial_turn_ccw()

        adjust_mock.assert_called_once_with(-1)

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    @patch.object(LevelDial, '_adjust_level')
    def test_on_dial_turn_cw_not_initialized(self, adjust_mock, _):
        instance = LevelDial()
        instance.initialized = False
        instance._on_dial_turn_cw()

        adjust_mock.assert_not_called()

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    @patch.object(LevelDial, '_adjust_level')
    def test_on_dial_turn_ccw_not_initialized(self, adjust_mock, _):
        instance = LevelDial()
        instance.initialized = False
        instance._on_dial_turn_ccw()

        adjust_mock.assert_not_called()
