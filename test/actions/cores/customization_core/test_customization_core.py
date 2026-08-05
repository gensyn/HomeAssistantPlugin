import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, call

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions import const as base_const
from HomeAssistantPlugin.actions.cores.customization_core.customization_core import CustomizationCore
from HomeAssistantPlugin.actions.cores.customization_core import customization_const


class TestCustomizationCore(unittest.TestCase):

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_core.BaseCore.__init__')
    def test_init(self, super_init_mock):
        window_implementation = "123"
        customization_implementation = "456"
        row_implementation = "789"
        arg = "abc"
        kwarg = {"key": "value"}

        instance = CustomizationCore(window_implementation, customization_implementation, row_implementation, arg,
                                     kwarg)

        super_init_mock.assert_called_once_with(arg, kwarg)
        self.assertEqual(instance.window_implementation, window_implementation)
        self.assertEqual(instance.customization_implementation, customization_implementation)
        self.assertEqual(instance.row_implementation, row_implementation)

    @patch('HomeAssistantPlugin.actions.cores.customization_core.customization_core.BaseCore.on_ready')
    def test_on_ready_not_connected(self, super_on_ready_mock):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.plugin_base = Mock()
        instance.plugin_base.backend.is_connected.return_value = False
        instance.refresh = Mock()
        instance.initialized = False
        instance._reload = Mock()

        instance.on_ready()

        super_on_ready_mock.assert_called_once()
        instance.refresh.assert_called_once()
        self.assertFalse(instance.initialized)
        instance._reload.assert_not_called()

    @patch('HomeAssistantPlugin.actions.cores.customization_core.customization_core.BaseCore.on_ready')
    def test_on_ready_connected(self, super_on_ready_mock):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.plugin_base = Mock()
        instance.plugin_base.backend.is_connected.return_value = True
        instance.refresh = Mock()
        instance.initialized = False
        instance._reload = Mock()

        instance.on_ready()

        super_on_ready_mock.assert_called_once()
        instance.refresh.assert_not_called()
        instance._reload.assert_called_once()

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_core.BaseCore.create_ui_elements')
    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_core.Button')
    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_core.ExpanderRow')
    def testcreate_ui_elements(self, expander_row_mock, button_mock, super_create_ui_elements_mock):
        button_mock.return_value = button_mock
        expander_row_mock.return_value = expander_row_mock

        instance = CustomizationCore.__new__(CustomizationCore)
        instance.create_ui_elements()

        super_create_ui_elements_mock.assert_called_once()
        button_mock.assert_called_once_with(icon_name="list-add", valign=3)
        button_mock.set_size_request.assert_called_once_with(15, 15)
        button_mock.connect.assert_called_once_with(
            base_const.CONNECT_CLICKED,
            instance._on_add_customization,
            instance._add_customization
        )
        expander_row_mock.assert_called_once_with(
            instance, '', False,
            title=base_const.LABEL_CUSTOMIZATION, can_reset=False,
            auto_add=False
        )
        expander_row_mock.widget.add_suffix.assert_called_once_with(button_mock)

    @patch.object(CustomizationCore, '_get_attributes')
    def test_on_add_customization_index_negative(self, get_attributes_mock):
        get_attributes_mock.return_value = ['attr1', 'attr2']
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.window_implementation = Mock()
        instance.window_implementation.return_value = instance.window_implementation
        instance.lm = "456"
        instance.settings = Mock()

        callback = "123"

        instance._on_add_customization(None, callback)

        get_attributes_mock.assert_called_once()
        instance.settings.get_customizations.assert_not_called()
        instance.window_implementation.assert_called_once_with(instance.lm, ['attr1', 'attr2'], callback, current=None,
                                                               index=-1)
        instance.window_implementation.show.assert_called_once()

    @patch.object(CustomizationCore, '_get_attributes')
    def test_on_add_customization_success(self, get_attributes_mock):
        get_attributes_mock.return_value = ['attr1', 'attr2']
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.window_implementation = Mock()
        instance.window_implementation.return_value = instance.window_implementation
        instance.lm = "456"
        instance.settings = Mock()
        instance.settings.get_customizations.return_value = ["custom1", "custom2"]

        callback = "123"

        instance._on_add_customization(None, callback, index=1)

        get_attributes_mock.assert_called_once()
        instance.settings.get_customizations.assert_called_once()
        instance.window_implementation.assert_called_once_with(instance.lm, ['attr1', 'attr2'], callback,
                                                               current="custom2", index=1)
        instance.window_implementation.show.assert_called_once()

    def test_add_customization_already_exists(self):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.settings = Mock()
        instance.settings.get_customizations.return_value = ["custom1", "custom2"]
        instance.refresh = Mock()

        customization = "custom1"
        index = 1

        instance._add_customization(customization, index)

        instance.settings.remove_customization.assert_called_once_with(1)
        instance.refresh.assert_called_once()
        instance.settings.replace_customization.assert_not_called()
        instance.settings.add_customization.assert_not_called()

    def test_add_customization_replace(self):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.settings = Mock()
        instance.settings.get_customizations.return_value = ["custom1", "custom2"]
        instance.refresh = Mock()

        customization = "custom3"
        index = 1

        instance._add_customization(customization, index)

        instance.settings.remove_customization.assert_not_called()
        instance.settings.replace_customization.assert_called_once_with(1, "custom3")
        instance.settings.add_customization.assert_not_called()
        instance.refresh.assert_called_once()

    def test_add_customization_add(self):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.settings = Mock()
        instance.settings.get_customizations.return_value = ["custom1", "custom2"]
        instance.refresh = Mock()

        customization = "custom3"
        index = -1

        instance._add_customization(customization, index)

        instance.settings.remove_customization.assert_not_called()
        instance.settings.replace_customization.assert_not_called()
        instance.settings.add_customization.assert_called_once_with("custom3")
        instance.refresh.assert_called_once()

    def test_on_delete_customization(self):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.settings = Mock()
        instance.refresh = Mock()

        index = 1

        instance._on_delete_customization(None, index)

        instance.settings.remove_customization.assert_called_once_with(1)
        instance.refresh.assert_called_once()

    def test_on_move_up(self):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.settings = Mock()
        instance.refresh = Mock()

        index = 1

        instance._on_move_up(None, index)

        instance.settings.move_customization.assert_called_once_with(1, -1)
        instance.refresh.assert_called_once()

    def test_on_move_down(self):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.settings = Mock()
        instance.refresh = Mock()

        index = 1

        instance._on_move_down(None, index)

        instance.settings.move_customization.assert_called_once_with(1, 1)
        instance.refresh.assert_called_once()

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_core.BaseCore.set_enabled_disabled')
    def test_set_enabled_disabled_no_domain(self, super_set_enabled_disabled_mock):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.initialized = True
        instance.settings = Mock()
        instance.settings.get_domain.return_value = ""
        instance.settings.get_entity.return_value = "entity"
        instance.customization_expander = Mock()
        instance.lm = Mock()
        instance.lm.get.return_value = "label"

        instance.set_enabled_disabled()

        super_set_enabled_disabled_mock.assert_called_once()
        instance.settings.get_domain.assert_called_once()
        instance.settings.get_entity.assert_called_once()
        instance.customization_expander.widget.set_sensitive.assert_called_once_with(False)
        instance.lm.get.assert_called_once_with(base_const.LABEL_NO_ENTITY)
        instance.customization_expander.widget.set_subtitle.assert_called_once_with("label")
        instance.customization_expander.set_expanded.assert_called_once_with(False)

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_core.BaseCore.set_enabled_disabled')
    def test_set_enabled_disabled_no_entity(self, super_set_enabled_disabled_mock):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.initialized = True
        instance.settings = Mock()
        instance.settings.get_domain.return_value = "domain"
        instance.settings.get_entity.return_value = ""
        instance.customization_expander = Mock()
        instance.lm = Mock()
        instance.lm.get.return_value = "label"

        instance.set_enabled_disabled()

        super_set_enabled_disabled_mock.assert_called_once()
        instance.settings.get_domain.assert_called_once()
        instance.settings.get_entity.assert_called_once()
        instance.customization_expander.widget.set_sensitive.assert_called_once_with(False)
        instance.lm.get.assert_called_once_with(base_const.LABEL_NO_ENTITY)
        instance.customization_expander.widget.set_subtitle.assert_called_once_with("label")
        instance.customization_expander.set_expanded.assert_called_once_with(False)

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_core.BaseCore.set_enabled_disabled')
    def test_set_enabled_disabled_no_customizations(self, super_set_enabled_disabled_mock):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.initialized = True
        instance.settings = Mock()
        instance.settings.get_domain.return_value = "domain"
        instance.settings.get_entity.return_value = "entity"
        instance.settings.get_customizations.return_value = []
        instance.customization_expander = Mock()
        instance.lm = Mock()
        instance.lm.get.return_value = "label"

        instance.set_enabled_disabled()

        super_set_enabled_disabled_mock.assert_called_once()
        instance.settings.get_domain.assert_called_once()
        instance.settings.get_entity.assert_called_once()
        instance.customization_expander.widget.set_sensitive.assert_called_once_with(True)
        instance.lm.get.assert_not_called()
        instance.customization_expander.widget.set_subtitle.assert_called_once_with(base_const.EMPTY_STRING)
        instance.customization_expander.set_expanded.assert_called_once_with(False)

    @patch(
        'HomeAssistantPlugin.actions.cores.customization_core.customization_core.BaseCore.set_enabled_disabled')
    def test_set_enabled_disabled_with_customizations(self, super_set_enabled_disabled_mock):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.initialized = True
        instance.settings = Mock()
        instance.settings.get_domain.return_value = "domain"
        instance.settings.get_entity.return_value = "entity"
        instance.settings.get_customizations.return_value = ["custom1"]
        instance.customization_expander = Mock()
        instance.lm = Mock()
        instance.lm.get.return_value = "label"

        instance.set_enabled_disabled()

        super_set_enabled_disabled_mock.assert_called_once()
        instance.settings.get_domain.assert_called_once()
        instance.settings.get_entity.assert_called_once()
        instance.customization_expander.widget.set_sensitive.assert_called_once_with(True)
        instance.lm.get.assert_not_called()
        instance.customization_expander.widget.set_subtitle.assert_called_once_with(base_const.EMPTY_STRING)
        instance.customization_expander.set_expanded.assert_called_once_with(True)

    def test_get_attributes(self):
        ha_entity = {"attributes": {"attr1": "value1", "attr2": "value2"}}
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.settings = Mock()
        instance.settings.get_entity.return_value = "entity"
        instance.plugin_base = Mock()
        instance.plugin_base.backend.get_entity.return_value = ha_entity

        result = instance._get_attributes()

        self.assertEqual([customization_const.STATE, "attr1", "attr2"], result)

    def test_load_customizations(self):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.customization_expander = Mock()
        instance._clearing = False
        instance._get_attributes = Mock()
        instance._get_attributes.return_value = ["attr1", "attr2"]
        instance.plugin_base = Mock()
        instance.plugin_base.backend.get_entity.return_value = "state"
        instance.settings = Mock()
        instance.settings.get_entity.return_value = "entity"
        instance.settings.get_customizations.return_value = ["custom1", "custom2"]
        edit_connect_mock = Mock()
        delete_connect_mock = Mock()
        up_connect_mock = Mock()
        down_connect_mock = Mock()
        row_mock = Mock()
        row_mock.edit_button.connect = edit_connect_mock
        row_mock.delete_button.connect = delete_connect_mock
        row_mock.up_button.connect = up_connect_mock
        row_mock.down_button.connect = down_connect_mock
        instance.row_implementation = Mock()
        instance.row_implementation.side_effect = [row_mock, row_mock]
        instance.lm = "abc"

        instance._load_customizations()

        instance.customization_expander.clear_rows.assert_called_once()
        instance.row_implementation.assert_has_calls([call("abc", "custom1", 2, 0, ["attr1", "attr2"], "state", instance.settings), call("abc", "custom2", 2, 1, ["attr1", "attr2"], "state", instance.settings)])
        edit_connect_mock.assert_has_calls([call(base_const.CONNECT_CLICKED, instance._on_add_customization, instance._add_customization, 0), call(base_const.CONNECT_CLICKED, instance._on_add_customization, instance._add_customization, 1)])
        delete_connect_mock.assert_has_calls([call(base_const.CONNECT_CLICKED, instance._on_delete_customization, 0), call(base_const.CONNECT_CLICKED, instance._on_delete_customization, 1)])
        up_connect_mock.assert_has_calls([call(base_const.CONNECT_CLICKED, instance._on_move_up, 0), call(base_const.CONNECT_CLICKED, instance._on_move_up, 1)])
        down_connect_mock.assert_has_calls([call(base_const.CONNECT_CLICKED, instance._on_move_down, 0), call(base_const.CONNECT_CLICKED, instance._on_move_down, 1)])

    def test_load_customizations_skipped_while_clearing(self):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.customization_expander = Mock()
        instance._clearing = True

        instance._load_customizations()

        instance.customization_expander.clear_rows.assert_not_called()

    @patch('HomeAssistantPlugin.actions.cores.customization_core.customization_core.BaseCore.on_remove')
    def test_on_remove_clears_expander_and_resets_flag(self, super_on_remove_mock):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.initialized = True
        instance._clearing = False
        instance.customization_expander = Mock()

        instance.on_remove()

        super_on_remove_mock.assert_called_once()
        instance.customization_expander.clear_rows.assert_called_once()
        self.assertFalse(instance._clearing)

    @patch('HomeAssistantPlugin.actions.cores.customization_core.customization_core.BaseCore.on_remove')
    def test_on_remove_sets_clearing_flag_during_super_call(self, super_on_remove_mock):
        """_clearing must be True when super().on_remove() runs so that any
        refresh() call triggered by the base class skips _load_customizations()."""
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.initialized = True
        instance._clearing = False
        instance.customization_expander = Mock()

        flag_during_super = []

        def capture_flag():
            flag_during_super.append(instance._clearing)

        super_on_remove_mock.side_effect = capture_flag

        instance.on_remove()

        self.assertTrue(flag_during_super[0])
        self.assertFalse(instance._clearing)

    @patch('HomeAssistantPlugin.actions.cores.customization_core.customization_core.BaseCore.on_remove')
    def test_on_remove_clears_expander_even_when_super_raises(self, super_on_remove_mock):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.initialized = True
        instance._clearing = False
        instance.customization_expander = Mock()
        super_on_remove_mock.side_effect = RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            instance.on_remove()

        instance.customization_expander.clear_rows.assert_called_once()
        self.assertFalse(instance._clearing)

    def test_on_remove_not_initialized(self):
        instance = CustomizationCore.__new__(CustomizationCore)
        instance.initialized = False
        instance._clearing = False
        instance.customization_expander = Mock()

        result = instance.on_remove()

        self.assertIsNone(result)
        instance.customization_expander.clear_rows.assert_not_called()
        self.assertFalse(instance._clearing)
