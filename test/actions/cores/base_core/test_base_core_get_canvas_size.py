import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreGetCanvasSize(unittest.TestCase):

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_get_canvas_size_returns_from_input(self, _, __):
        instance = BaseCore(Mock(), True)
        instance.get_input = Mock(return_value=Mock(get_image_size=Mock(return_value=(200, 100))))

        result = instance._get_canvas_size()

        self.assertEqual((200, 100), result)

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_get_canvas_size_returns_default_on_exception(self, _, __):
        instance = BaseCore(Mock(), True)
        instance.get_input = Mock(side_effect=AttributeError("not available"))

        result = instance._get_canvas_size()

        self.assertEqual((1, 1), result)

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_get_canvas_size_returns_default_on_type_error(self, _, __):
        instance = BaseCore(Mock(), True)
        instance.get_input = Mock(side_effect=TypeError("type error"))

        result = instance._get_canvas_size()

        self.assertEqual((1, 1), result)

    @patch.object(BaseCore, "_create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_get_canvas_size_returns_default_when_get_input_missing(self, _, __):
        instance = BaseCore(Mock(), True)
        # Simulate the mock ActionCore's get_input that raises AttributeError
        result = instance._get_canvas_size()

        self.assertEqual((1, 1), result)
