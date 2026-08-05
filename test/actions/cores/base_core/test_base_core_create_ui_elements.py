import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions import const
from HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore, set_substring_search


class TestBaseCoreCreateUiElements(unittest.TestCase):

    @patch.object(BaseCore, "_create_event_assigner")
    def test_create_ui_elements_success(self, _):
        with patch.object(BaseCore, "create_ui_elements"):
            # create_ui_elements is called in the constructor
            instance = BaseCore(Mock(), False)

        instance.create_ui_elements()

        self.assertEqual((instance, const.SETTING_ENTITY_DOMAIN, const.EMPTY_STRING, [],
                          const.LABEL_ENTITY_DOMAIN), instance.domain_combo.args)
        self.assertEqual({"enable_search": True,
                          "on_change": instance.on_change_domain, "can_reset": False,
                          "complex_var_name": True}, instance.domain_combo.kwargs)

        self.assertEqual((instance, const.SETTING_ENTITY_ENTITY, const.EMPTY_STRING, [],
                          const.LABEL_ENTITY_ENTITY), instance.entity_combo.args)
        self.assertEqual({"enable_search": True,
                          "on_change": instance.on_change_entity, "can_reset": False,
                          "complex_var_name": True}, instance.entity_combo.kwargs)

    def test_set_substring_search_calls_set_search_match_mode_when_available(self):
        """set_search_match_mode is called on the widget when the method is present."""
        widget_mock = Mock(spec=["set_search_match_mode"])
        combo_mock = Mock()
        combo_mock.widget = widget_mock

        with patch("HomeAssistantPlugin.actions.cores.base_core.base_core.Gtk") as gtk_mock:
            set_substring_search(combo_mock)

        widget_mock.set_search_match_mode.assert_called_once_with(
            gtk_mock.StringFilterMatchMode.SUBSTRING
        )

    def test_set_substring_search_is_noop_when_method_not_available(self):
        """No error is raised when set_search_match_mode is absent (older libadwaita)."""
        widget_mock = Mock(spec=[])  # no set_search_match_mode
        combo_mock = Mock()
        combo_mock.widget = widget_mock

        set_substring_search(combo_mock)  # must not raise

        self.assertFalse(hasattr(widget_mock, "set_search_match_mode"))

    def test_set_substring_search_is_noop_when_widget_raises(self):
        """No error is raised when accessing the widget attribute fails."""
        from unittest.mock import PropertyMock
        combo_mock = Mock()
        type(combo_mock).widget = PropertyMock(side_effect=AttributeError())
        set_substring_search(combo_mock)  # must not raise

