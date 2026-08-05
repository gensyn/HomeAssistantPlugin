import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreSetEnabledDisabled(unittest.TestCase):

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_set_enabled_disabled_not_initialized(self, _, __):
        settings_mock = Mock()
        settings_mock.load = Mock()
        settings_mock.get_domain = Mock(return_value="light")

        entity_combo_mock = Mock()
        entity_combo_mock.get_item_amount = Mock(return_value=2)
        entity_combo_mock.set_sensitive = Mock()

        instance = BaseCore(Mock(), True)
        instance.settings = settings_mock
        instance.entity_combo = entity_combo_mock
        instance.initialized = False
        instance.set_enabled_disabled()

        settings_mock.load.assert_not_called()
        settings_mock.get_domain.assert_not_called()
        entity_combo_mock.set_sensitive.assert_not_called()

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_set_enabled_disabled_no_domain(self, _, __):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value=None)

        entity_combo_mock = Mock()
        entity_combo_mock.get_item_amount = Mock(return_value=2)
        entity_combo_mock.set_sensitive = Mock()

        instance = BaseCore(Mock(), True)
        instance.settings = settings_mock
        instance.entity_combo = entity_combo_mock
        instance.initialized = True
        instance.set_enabled_disabled()

        settings_mock.get_domain.assert_called_once()
        entity_combo_mock.set_sensitive.assert_called_once_with(False)

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_set_enabled_enabled_only_one_entity(self, _, __):
        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value="light")

        entity_combo_mock = Mock()
        entity_combo_mock.get_item_amount = Mock(return_value=1)
        entity_combo_mock.set_sensitive = Mock()

        instance = BaseCore(Mock(), True)
        instance.settings = settings_mock
        instance.entity_combo = entity_combo_mock
        instance.initialized = True
        instance.set_enabled_disabled()

        settings_mock.get_domain.assert_called_once()
        entity_combo_mock.set_sensitive.assert_called_once_with(True)

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    def test_set_enabled_disabled_success(self, _, __):
        settings_mock = Mock()
        settings_mock.get_domain.return_value = "light"

        entity_combo_mock = Mock()
        entity_combo_mock.get_item_amount = Mock(return_value=2)
        entity_combo_mock.set_sensitive = Mock()

        instance = BaseCore(Mock(), True)
        instance.settings = settings_mock
        instance.entity_combo = entity_combo_mock
        instance.initialized = True
        instance.set_enabled_disabled()

        settings_mock.get_domain.assert_called_once()
        entity_combo_mock.set_sensitive.assert_called_once_with(True)

