import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreOnRemove(unittest.TestCase):

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "refresh")
    def test_on_read_entity_not_tracked(self, refresh_mock, _, __):
        get_entity_mock = Mock(return_value="entity")

        settings_mock = Mock()
        settings_mock.get_entity = get_entity_mock

        track_entity = False

        instance = BaseCore(Mock(), track_entity)
        instance.initialized = True
        instance.settings = settings_mock
        instance.on_remove()

        instance.plugin_base.backend.remove_action_ready_callback.assert_called_once_with(instance.on_ready)
        instance.plugin_base.backend.remove_tracked_entity.assert_not_called()
        refresh_mock.assert_called_once()

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "refresh")
    def test_on_remove_success(self, refresh_mock, _, __):
        get_entity_mock = Mock(return_value="entity")

        settings_mock = Mock()
        settings_mock.get_entity = get_entity_mock

        track_entity = True

        instance = BaseCore(Mock(), track_entity)
        instance.initialized = True
        instance.settings = settings_mock
        instance.on_remove()

        instance.plugin_base.backend.remove_action_ready_callback.assert_called_once_with(instance.on_ready)
        instance.plugin_base.backend.remove_tracked_entity.assert_called_once_with("entity", instance.refresh)
        refresh_mock.assert_called_once()

