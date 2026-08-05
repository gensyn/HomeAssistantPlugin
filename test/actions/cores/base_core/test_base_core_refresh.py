import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreRefresh(unittest.TestCase):

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_refresh_success(self, _, __):
        # This test checks if the _entity_updated method can be called without errors
        instance = BaseCore(Mock(), True)
        instance.initialized = True
        instance.refresh()

