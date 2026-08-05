import sys
import unittest
from pathlib import Path
from unittest.mock import patch, call

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from src.backend.DeckManagement.InputIdentifier import Input
from HomeAssistantPlugin.actions.level_dial.level_dial import LevelDial


class TestLevelDialCreateEventAssigner(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.EventAssigner')
    @patch.object(LevelDial, 'add_event_assigner')
    def test_create_event_assigner_registers_three_dial_events(self, add_event_assigner_mock, event_assigner_mock, _):
        instance = LevelDial()
        instance._create_event_assigner()

        self.assertEqual(add_event_assigner_mock.call_count, 3)
        self.assertEqual(event_assigner_mock.call_count, 3)

        event_assigner_mock.assert_any_call(
            id="Dial Turn CW",
            ui_label="Dial Turn CW",
            default_events=[Input.Dial.Events.TURN_CW],
            callback=instance._on_dial_turn_cw
        )
        event_assigner_mock.assert_any_call(
            id="Dial Turn CCW",
            ui_label="Dial Turn CCW",
            default_events=[Input.Dial.Events.TURN_CCW],
            callback=instance._on_dial_turn_ccw
        )
        event_assigner_mock.assert_any_call(
            id="Dial Short Up",
            ui_label="Dial Short Up",
            default_events=[Input.Dial.Events.SHORT_UP],
            callback=instance._on_dial_short_up
        )
