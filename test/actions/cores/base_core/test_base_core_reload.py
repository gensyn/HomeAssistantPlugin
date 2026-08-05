import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreReload(unittest.TestCase):

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "set_enabled_disabled")
    @patch.object(BaseCore, "refresh")
    def test_reload_success(self, refresh_mock, set_enabled_disabled_mock, _, __):
        settings_mock = Mock()

        instance = BaseCore(Mock(), False)
        instance.initialized = True
        instance.settings = settings_mock
        instance._reload()

        set_enabled_disabled_mock.assert_called_once()
        refresh_mock.assert_called_once()

