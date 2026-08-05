import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.level_dial.level_dial import LevelDial
from HomeAssistantPlugin.actions.level_dial.level_customization import LevelDialCustomization
from HomeAssistantPlugin.actions.level_dial.level_row import LevelDialRow
from HomeAssistantPlugin.actions.level_dial.level_settings import LevelDialSettings
from HomeAssistantPlugin.actions.level_dial.level_window import LevelDialWindow


class TestLevelDialInit(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_init_calls_super_with_correct_args(self, base_core_init_mock):
        test_arg = "test_arg_value"
        test_kwarg = "test_kwarg_value"

        LevelDial(test_arg, test_kwarg=test_kwarg)

        base_core_init_mock.assert_called_once_with(
            test_arg,
            window_implementation=LevelDialWindow,
            customization_implementation=LevelDialCustomization,
            row_implementation=LevelDialRow,
            settings_implementation=LevelDialSettings,
            track_entity=True,
            test_kwarg=test_kwarg
        )
