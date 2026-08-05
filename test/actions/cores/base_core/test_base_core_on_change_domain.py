import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreOnChangeDomain(unittest.TestCase):

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_load_entities")
    @patch.object(BaseCore, "set_enabled_disabled")
    def test_on_change_domain_old_and_new_equal(self, set_enabled_disabled_mock, load_entities_mock, _, __):
        entity_id = "light.living_room"

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value=entity_id)
        settings_mock.reset = Mock()

        remove_all_items_mock = Mock()

        entity_combo_mock = Mock()
        entity_combo_mock.remove_all_items = remove_all_items_mock

        domain = "light"

        instance = BaseCore(Mock(), True)
        instance.initialized = True
        instance.settings = settings_mock
        instance.entity_combo = entity_combo_mock
        instance.on_change_domain(None, domain, domain)

        settings_mock.get_entity.assert_not_called()
        instance.plugin_base.backend.remove_tracked_entity.assert_not_called()
        settings_mock.reset.assert_not_called()
        instance.entity_combo.remove_all_items.assert_not_called()
        load_entities_mock.assert_called_once()
        set_enabled_disabled_mock.assert_called_once()

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_load_entities")
    @patch.object(BaseCore, "set_enabled_disabled")
    def test_on_change_domain_no_entity(self, set_enabled_disabled_mock, load_entities_mock, _, __):
        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value=None)
        settings_mock.reset = Mock()

        remove_all_items_mock = Mock()

        entity_combo_mock = Mock()
        entity_combo_mock.remove_all_items = remove_all_items_mock
        entity_combo_mock.get_item_amount = Mock(return_value=0)

        domain = "light"

        instance = BaseCore(Mock(), True)
        instance.initialized = True
        instance.settings = settings_mock
        instance.entity_combo = entity_combo_mock
        instance.on_change_domain(None, domain, None)

        settings_mock.get_entity.assert_called_once()
        instance.plugin_base.backend.remove_tracked_entity.assert_not_called()
        settings_mock.reset.assert_called_once_with(domain)
        instance.entity_combo.remove_all_items.assert_called_once()
        load_entities_mock.assert_called_once()
        set_enabled_disabled_mock.assert_called_once()

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_load_entities")
    @patch.object(BaseCore, "set_enabled_disabled")
    def test_on_change_domain_enity_not_tracked(self, set_enabled_disabled_mock, load_entities_mock, _, __):
        entity_id = "light.living_room"

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value=entity_id)
        settings_mock.reset = Mock()

        remove_all_items_mock = Mock()

        entity_combo_mock = Mock()
        entity_combo_mock.remove_all_items = remove_all_items_mock
        entity_combo_mock.get_item_amount = Mock(return_value=0)

        domain = "light"

        instance = BaseCore(Mock(), False)
        instance.initialized = True
        instance.settings = settings_mock
        instance.entity_combo = entity_combo_mock
        instance.on_change_domain(None, domain, None)

        settings_mock.get_entity.assert_called_once()
        instance.plugin_base.backend.remove_tracked_entity.assert_not_called()
        settings_mock.reset.assert_called_once_with(domain)
        instance.entity_combo.remove_all_items.assert_called_once()
        load_entities_mock.assert_called_once()
        set_enabled_disabled_mock.assert_called_once()

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_load_entities")
    @patch.object(BaseCore, "set_enabled_disabled")
    def test_on_change_domain_no_new_domain(self, set_enabled_disabled_mock, load_entities_mock, _, __):
        entity_id = "light.living_room"

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value=entity_id)
        settings_mock.reset = Mock()

        remove_all_items_mock = Mock()

        entity_combo_mock = Mock()
        entity_combo_mock.remove_all_items = remove_all_items_mock
        entity_combo_mock.get_item_amount = Mock(return_value=0)

        domain = None

        instance = BaseCore(Mock(), True)
        instance.initialized = True
        instance.settings = settings_mock
        instance.entity_combo = entity_combo_mock
        instance.on_change_domain(None, domain, "light")

        settings_mock.get_entity.assert_called_once()
        instance.plugin_base.backend.remove_tracked_entity.assert_called_once_with(entity_id, instance.refresh)
        settings_mock.reset.assert_called_once_with(domain)
        instance.entity_combo.remove_all_items.assert_called_once()
        load_entities_mock.assert_not_called()
        set_enabled_disabled_mock.assert_called_once()

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_load_entities")
    @patch.object(BaseCore, "set_enabled_disabled")
    def test_on_change_domain_success(self, set_enabled_disabled_mock, load_entities_mock, _, __):
        entity_id = "light.living_room"

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value=entity_id)
        settings_mock.reset = Mock()

        remove_all_items_mock = Mock()

        entity_combo_mock = Mock()
        entity_combo_mock.remove_all_items = remove_all_items_mock
        entity_combo_mock.get_item_amount = Mock(return_value=0)

        domain = "light"

        instance = BaseCore(Mock(), True)
        instance.initialized = True
        instance.settings = settings_mock
        instance.entity_combo = entity_combo_mock
        instance.on_change_domain(None, domain, None)

        settings_mock.get_entity.assert_called_once()
        instance.plugin_base.backend.remove_tracked_entity.assert_called_once_with(entity_id, instance.refresh)
        settings_mock.reset.assert_called_once_with(domain)
        instance.entity_combo.remove_all_items.assert_called_once()
        load_entities_mock.assert_called_once()
        set_enabled_disabled_mock.assert_called_once()

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_load_entities")
    @patch.object(BaseCore, "set_enabled_disabled")
    def test_on_change_domain_resets_entity_cache(self, set_enabled_disabled_mock, load_entities_mock, _, __):
        """Changing domain must reset _last_loaded_entities so entities are re-populated."""
        entity_id = "light.living_room"

        settings_mock = Mock()
        settings_mock.get_entity = Mock(return_value=entity_id)
        settings_mock.reset = Mock()

        entity_combo_mock = Mock()
        entity_combo_mock.get_item_amount = Mock(return_value=0)

        instance = BaseCore(Mock(), True)
        instance.initialized = True
        instance.settings = settings_mock
        instance.entity_combo = entity_combo_mock
        # Pre-populate the entity cache
        instance._last_loaded_entities = ["light.living_room", "light.kitchen"]

        instance.on_change_domain(None, "switch", "light")

        self.assertIsNone(instance._last_loaded_entities)

