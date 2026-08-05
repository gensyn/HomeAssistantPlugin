import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreInit(unittest.TestCase):

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_init_success(self, create_event_assigner_mock, create_ui_elements_mock):
        track_entity = True
        test_arg = "test_arg_value"
        test_kwarg = "test_kwarg_value"

        instance = BaseCore(Mock(), track_entity, test_arg, test_kwarg=test_kwarg)

        self.assertIsNone(instance.settings)
        self.assertFalse(instance.initialized)
        self.assertEqual(instance.plugin_base.locale_manager, instance.lm)
        self.assertTrue(instance.has_configuration)
        self.assertEqual(track_entity, instance.track_entity)
        self.assertEqual((test_arg,), instance.args)
        self.assertEqual({"test_kwarg": test_kwarg}, instance.kwargs)
        create_ui_elements_mock.assert_called_once()
        create_event_assigner_mock.assert_called_once()

