import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, call

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.show_text import text_const
from HomeAssistantPlugin.actions.show_text.text_action import ShowText
from HomeAssistantPlugin.actions.show_text.text_customization import TextCustomization
from HomeAssistantPlugin.actions.show_text.text_row import TextRow
from HomeAssistantPlugin.actions.show_text.text_settings import ShowTextSettings
from HomeAssistantPlugin.actions.show_text.text_window import TextWindow


class TestShowText(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.show_text.text_action.CustomizationCore.__init__')
    def test_init(self, super_init_mock):
        arg = "abc"
        kwargs = {"key": "value"}

        ShowText(*arg, **kwargs)

        super_init_mock.assert_called_once_with(
            window_implementation=TextWindow,
            customization_implementation=TextCustomization,
            row_implementation=TextRow,
            settings_implementation=ShowTextSettings,
            track_entity=True,
            *arg,
            **kwargs
        )

    def test_get_config_rows(self):
        instance = ShowText.__new__(ShowText)
        instance.domain_combo = Mock()
        instance.domain_combo.widget = "domain_combo_widget"
        instance.entity_combo = Mock()
        instance.entity_combo.widget = "entity_combo_widget"
        instance.position = Mock()
        instance.position.widget = "position_widget"
        instance.attribute = Mock()
        instance.attribute.widget = "attribute_widget"
        instance.round = Mock()
        instance.round.widget = "round_widget"
        instance.text_size = Mock()
        instance.text_size.widget = "text_size_widget"
        instance.text_color = Mock()
        instance.text_color.widget = "text_color_widget"
        instance.outline_size = Mock()
        instance.outline_size.widget = "outline_size_widget"
        instance.outline_color = Mock()
        instance.outline_color.widget = "outline_color_widget"
        instance.show_unit = Mock()
        instance.show_unit.widget = "show_unit_widget"
        instance.unit_line_break = Mock()
        instance.unit_line_break.widget = "unit_line_break_widget"
        instance.customization_expander = Mock()
        instance.customization_expander.widget = "customization_expander_widget"

        expected = [
            "domain_combo_widget",
            "entity_combo_widget",
            "position_widget",
            "attribute_widget",
            "round_widget",
            "text_size_widget",
            "text_color_widget",
            "outline_size_widget",
            "outline_color_widget",
            "show_unit_widget",
            "unit_line_break_widget",
            "customization_expander_widget"
        ]

        result = instance.get_config_rows()

        self.assertEqual(result, expected)

    @patch('HomeAssistantPlugin.actions.show_text.text_action.CustomizationCore.create_ui_elements')
    @patch('HomeAssistantPlugin.actions.show_text.text_action.ComboRow')
    @patch('HomeAssistantPlugin.actions.show_text.text_action.ExpanderRow')
    @patch('HomeAssistantPlugin.actions.show_text.text_action.ScaleRow')
    @patch('HomeAssistantPlugin.actions.show_text.text_action.ColorButtonRow')
    @patch('HomeAssistantPlugin.actions.show_text.text_action.SwitchRow')
    def test_create_ui_elements(self, switch_row_mock, color_button_row_mock, scale_row_mock, expander_row_mock,
                                combo_row_mock, super_create_ui_elements_mock):
        instance = ShowText.__new__(ShowText)
        instance._reload = Mock()

        instance.create_ui_elements()

        super_create_ui_elements_mock.assert_called_once()
        self.assertTrue(hasattr(instance, "position"))
        self.assertTrue(hasattr(instance, "attribute"))
        self.assertTrue(hasattr(instance, "round"))
        self.assertTrue(hasattr(instance, "text_size"))
        self.assertTrue(hasattr(instance, "text_color"))
        self.assertTrue(hasattr(instance, "outline_size"))
        self.assertTrue(hasattr(instance, "outline_color"))
        self.assertTrue(hasattr(instance, "show_unit"))
        self.assertTrue(hasattr(instance, "unit_line_break"))
        combo_row_mock.assert_has_calls([
            call(instance, text_const.SETTING_TEXT_POSITION, text_const.POSITION_CENTER, ['top', 'center', 'bottom'],
                 title=text_const.LABEL_POSITION, on_change=instance._reload,
                 can_reset=False, complex_var_name=True),
            call(instance, text_const.SETTING_TEXT_ATTRIBUTE, text_const.DEFAULT_ATTRIBUTE, [],
                 title=text_const.LABEL_ATTRIBUTE, on_change=instance._reload,
                 can_reset=False, complex_var_name=True),
        ])
        expander_row_mock.assert_called_once_with(
            instance, text_const.SETTING_TEXT_ROUND, text_const.DEFAULT_ROUND,
            title=text_const.LABEL_ROUND, show_enable_switch=True,
            on_change=instance._reload, can_reset=False, complex_var_name=True
        )
        scale_row_mock.assert_has_calls([
            call(instance, text_const.SETTING_TEXT_ROUND_PRECISION, text_const.DEFAULT_ROUND_PRECISION,
                 text_const.ROUND_MIN_PRECISION, text_const.ROUND_MAX_PRECISION,
                 title=text_const.LABEL_ROUND, step=1, digits=0,
                 on_change=instance._reload, can_reset=False, complex_var_name=True),
            call(instance, text_const.SETTING_TEXT_TEXT_SIZE, text_const.DEFAULT_TEXT_SIZE,
                 text_const.TEXT_MIN_SIZE, text_const.TEXT_MAX_SIZE,
                 title=text_const.LABEL_TEXT_SIZE, step=1, digits=0,
                 on_change=instance._reload, can_reset=False, complex_var_name=True),
            call(instance, text_const.SETTING_TEXT_OUTLINE_SIZE, text_const.DEFAULT_OUTLINE_SIZE,
                 text_const.OUTLINE_MIN_SIZE, text_const.OUTLINE_MAX_SIZE,
                 title=text_const.LABEL_OUTLINE_SIZE, step=1, digits=0,
                 on_change=instance._reload, can_reset=False, complex_var_name=True)
        ])
        color_button_row_mock.assert_has_calls([
            call(instance, text_const.SETTING_TEXT_TEXT_COLOR, text_const.DEFAULT_TEXT_COLOR,
                 title=text_const.LABEL_TEXT_COLOR, on_change=instance._reload,
                 can_reset=False, complex_var_name=True),
            call(instance, text_const.SETTING_TEXT_OUTLINE_COLOR, text_const.DEFAULT_OUTLINE_COLOR,
                 title=text_const.LABEL_OUTLINE_COLOR, on_change=instance._reload,
                 can_reset=False, complex_var_name=True)
        ])
        switch_row_mock.assert_has_calls([
            call(instance, text_const.SETTING_TEXT_SHOW_UNIT, text_const.DEFAULT_SHOW_UNIT,
                 title=text_const.LABEL_SHOW_UNIT, on_change=instance._reload,
                 can_reset=False, complex_var_name=True),
            call(instance, text_const.SETTING_TEXT_UNIT_LINE_BREAK, text_const.DEFAULT_UNIT_LINE_BREAK,
                 title=text_const.LABEL_UNIT_LINE_BREAK, on_change=instance._reload,
                 can_reset=False, complex_var_name=True)
        ])

    @patch('HomeAssistantPlugin.actions.show_text.text_action.CustomizationCore.set_enabled_disabled')
    def test_set_enabled_disabled_no_domain(self, super_set_enabled_disabled_mock):
        lm = {
            text_const.LABEL_NO_ENTITY: "No entity selected"
        }

        instance = ShowText.__new__(ShowText)
        instance.initialized = True
        instance.lm = lm
        instance.settings = Mock()
        instance.settings.get_domain.return_value = ""
        instance.settings.get_entity.return_value = "entity"
        instance.position = Mock()
        instance.attribute = Mock()
        instance.round = Mock()
        instance.round_precision = Mock()
        instance.text_size = Mock()
        instance.text_color = Mock()
        instance.outline_size = Mock()
        instance.outline_color = Mock()
        instance.show_unit = Mock()
        instance.unit_line_break = Mock()

        instance.set_enabled_disabled()

        super_set_enabled_disabled_mock.assert_called_once()
        instance.position.widget.set_sensitive.assert_called_once_with(False)
        instance.position.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.attribute.widget.set_sensitive.assert_called_once_with(False)
        instance.attribute.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.round.widget.set_sensitive.assert_called_once_with(False)
        instance.round.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.round_precision.widget.set_sensitive.assert_called_once_with(False)
        instance.round_precision.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.text_size.widget.set_sensitive.assert_called_once_with(False)
        instance.text_size.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.text_color.widget.set_sensitive.assert_called_once_with(False)
        instance.text_color.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.outline_size.widget.set_sensitive.assert_called_once_with(False)
        instance.outline_size.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.outline_color.widget.set_sensitive.assert_called_once_with(False)
        instance.outline_color.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.show_unit.widget.set_sensitive.assert_called_once_with(False)
        instance.show_unit.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.unit_line_break.widget.set_sensitive.assert_called_once_with(False)
        instance.unit_line_break.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])

    @patch('HomeAssistantPlugin.actions.show_text.text_action.CustomizationCore.set_enabled_disabled')
    def test_set_enabled_disabled_no_entity(self, super_set_enabled_disabled_mock):
        lm = {
            text_const.LABEL_NO_ENTITY: "No entity selected"
        }

        instance = ShowText.__new__(ShowText)
        instance.initialized = True
        instance.lm = lm
        instance.settings = Mock()
        instance.settings.get_domain.return_value = "domain"
        instance.settings.get_entity.return_value = ""
        instance.position = Mock()
        instance.attribute = Mock()
        instance.round = Mock()
        instance.round_precision = Mock()
        instance.text_size = Mock()
        instance.text_color = Mock()
        instance.outline_size = Mock()
        instance.outline_color = Mock()
        instance.show_unit = Mock()
        instance.unit_line_break = Mock()

        instance.set_enabled_disabled()

        super_set_enabled_disabled_mock.assert_called_once()
        instance.position.widget.set_sensitive.assert_called_once_with(False)
        instance.position.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.attribute.widget.set_sensitive.assert_called_once_with(False)
        instance.attribute.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.round.widget.set_sensitive.assert_called_once_with(False)
        instance.round.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.round_precision.widget.set_sensitive.assert_called_once_with(False)
        instance.round_precision.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.text_size.widget.set_sensitive.assert_called_once_with(False)
        instance.text_size.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.text_color.widget.set_sensitive.assert_called_once_with(False)
        instance.text_color.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.outline_size.widget.set_sensitive.assert_called_once_with(False)
        instance.outline_size.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.outline_color.widget.set_sensitive.assert_called_once_with(False)
        instance.outline_color.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.show_unit.widget.set_sensitive.assert_called_once_with(False)
        instance.show_unit.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])
        instance.unit_line_break.widget.set_sensitive.assert_called_once_with(False)
        instance.unit_line_break.widget.set_subtitle.assert_called_once_with(lm[text_const.LABEL_NO_ENTITY])

    @patch('HomeAssistantPlugin.actions.show_text.text_action.CustomizationCore.set_enabled_disabled')
    def test_set_enabled_disabled_without_unit(self, super_set_enabled_disabled_mock):
        lm = {
            text_const.LABEL_NO_ENTITY: "No entity selected"
        }

        ha_entity = {
            "state": "25",
        }

        instance = ShowText.__new__(ShowText)
        instance.initialized = True
        instance.lm = lm
        instance.plugin_base = Mock()
        instance.plugin_base.backend.get_entity.return_value = ha_entity
        instance.settings = Mock()
        instance.settings.get_domain.return_value = "domain"
        instance.settings.get_entity.return_value = "entity"
        instance.position = Mock()
        instance.attribute = Mock()
        instance.attribute.get_item_amount.return_value = 1
        instance.round = Mock()
        instance.round_precision = Mock()
        instance.text_size = Mock()
        instance.text_color = Mock()
        instance.outline_size = Mock()
        instance.outline_color = Mock()
        instance.show_unit = Mock()
        instance.show_unit.get_active.return_value = False
        instance.unit_line_break = Mock()

        instance.set_enabled_disabled()

        super_set_enabled_disabled_mock.assert_called_once()
        instance.position.widget.set_sensitive.assert_called_once_with(True)
        instance.position.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.attribute.widget.set_sensitive.assert_called_once_with(False)
        instance.attribute.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.round.widget.set_sensitive.assert_called_once_with(True)
        instance.round.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.round_precision.widget.set_sensitive.assert_called_once_with(True)
        instance.round_precision.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.text_size.widget.set_sensitive.assert_called_once_with(True)
        instance.text_size.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.text_color.widget.set_sensitive.assert_called_once_with(True)
        instance.text_color.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.outline_size.widget.set_sensitive.assert_called_once_with(True)
        instance.outline_size.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.outline_color.widget.set_sensitive.assert_called_once_with(True)
        instance.outline_color.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.show_unit.set_active.assert_called_once_with(False)
        instance.show_unit.widget.set_sensitive.assert_called_once_with(False)
        instance.show_unit.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.unit_line_break.set_active.assert_has_calls([call(False), call(False)])
        instance.unit_line_break.widget.set_sensitive.assert_has_calls([call(False), call(False)])
        instance.unit_line_break.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)

    @patch('HomeAssistantPlugin.actions.show_text.text_action.CustomizationCore.set_enabled_disabled')
    def test_set_enabled_disabled_with_unit(self, super_set_enabled_disabled_mock):
        lm = {
            text_const.LABEL_NO_ENTITY: "No entity selected"
        }

        ha_entity = {
            "state": "25",
            customization_const.ATTRIBUTES: {
                customization_const.UNIT_OF_MEASUREMENT: "°C"
            }
        }

        instance = ShowText.__new__(ShowText)
        instance.initialized = True
        instance.lm = lm
        instance.plugin_base = Mock()
        instance.plugin_base.backend.get_entity.return_value = ha_entity
        instance.settings = Mock()
        instance.settings.get_domain.return_value = "domain"
        instance.settings.get_entity.return_value = "entity"
        instance.position = Mock()
        instance.attribute = Mock()
        instance.attribute.get_item_amount.return_value = 1
        instance.round = Mock()
        instance.round_precision = Mock()
        instance.text_size = Mock()
        instance.text_color = Mock()
        instance.outline_size = Mock()
        instance.outline_color = Mock()
        instance.show_unit = Mock()
        instance.show_unit.get_active.return_value = True
        instance.unit_line_break = Mock()

        instance.set_enabled_disabled()

        super_set_enabled_disabled_mock.assert_called_once()
        instance.position.widget.set_sensitive.assert_called_once_with(True)
        instance.position.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.attribute.widget.set_sensitive.assert_called_once_with(False)
        instance.attribute.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.round.widget.set_sensitive.assert_called_once_with(True)
        instance.round.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.round_precision.widget.set_sensitive.assert_called_once_with(True)
        instance.round_precision.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.text_size.widget.set_sensitive.assert_called_once_with(True)
        instance.text_size.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.text_color.widget.set_sensitive.assert_called_once_with(True)
        instance.text_color.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.outline_size.widget.set_sensitive.assert_called_once_with(True)
        instance.outline_size.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.outline_color.widget.set_sensitive.assert_called_once_with(True)
        instance.outline_color.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.show_unit.widget.set_sensitive.assert_called_once_with(True)
        instance.show_unit.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)
        instance.unit_line_break.widget.set_sensitive.assert_called_once_with(True)
        instance.unit_line_break.widget.set_subtitle.assert_called_once_with(text_const.EMPTY_STRING)

    @patch('HomeAssistantPlugin.actions.show_text.text_action.CustomizationCore.on_change_entity')
    def test_on_change_entity(self, super_on_change_entity_mock):
        instance = ShowText.__new__(ShowText)
        instance.initialized = True
        instance._load_attributes = Mock()

        instance.on_change_entity(None, "entity", "old_entity")
        instance._load_attributes.assert_called_once()
        super_on_change_entity_mock.assert_called_once_with(None, "entity", "old_entity")

    def test_load_attributes_lists_identical(self):
        instance = ShowText.__new__(ShowText)
        instance.settings = Mock()
        instance.settings.get_attribute.return_value = "attribute1"
        instance._get_attributes = Mock()
        instance._get_attributes.return_value = ["attribute2", "attribute3"]
        instance._get_current_attributes = Mock()
        instance._get_current_attributes.return_value = ["attribute1", "attribute2", "attribute3"]
        instance.attribute = Mock()

        instance._load_attributes()

        instance.attribute.populate.assert_not_called()

    def test_load_attributes_lists_differ(self):
        instance = ShowText.__new__(ShowText)
        instance.settings = Mock()
        instance.settings.get_attribute.return_value = "attribute1"
        instance._get_attributes = Mock()
        instance._get_attributes.return_value = ["attribute1", "attribute2"]
        instance._get_current_attributes = Mock()
        instance._get_current_attributes.return_value = ["attribute1", "attribute2", "attribute3"]
        instance.attribute = Mock()

        instance._load_attributes()

        instance.attribute.populate.assert_called_once_with(
            ["attribute1", "attribute2"],
            "attribute1",
            trigger_callback=False
        )

    def test_get_current_attributes(self):
        attributes = ["attribute1", "attribute2", "attribute3"]

        instance = ShowText.__new__(ShowText)
        instance.attribute = Mock()
        instance.attribute.get_item_amount.return_value = 3
        instance.attribute.get_item_at.side_effect = attributes

        result = instance._get_current_attributes()

        self.assertEqual(attributes, result)

    @patch('HomeAssistantPlugin.actions.show_text.text_action.text_helper')
    def test_refresh_not_initialized(self, text_helper_mock):
        instance = ShowText.__new__(ShowText)
        instance.initialized = False
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_bottom_label = Mock()
        instance.set_label = Mock()
        instance.settings = Mock()
        instance.plugin_base = Mock()
        instance.plugin_base.backend.is_connected.return_value = False
        instance.plugin_base.backend.get_entity.return_value = {"state": "state"}
        instance._load_attributes = Mock()
        instance._load_customizations = Mock()
        instance.set_enabled_disabled = Mock()
        text_helper_mock.get_text.return_value = ("a", "b", "c", "d", "e", "f")

        instance.refresh()

        instance.set_top_label.assert_called_once_with(text_const.EMPTY_STRING)
        instance.set_center_label.assert_called_once_with(text_const.EMPTY_STRING)
        instance.set_bottom_label.assert_called_once_with(text_const.EMPTY_STRING)
        text_helper_mock.get_text.assert_called_once_with(None, instance.settings, False)
        instance.set_label.assert_called_once_with("a", "b", "d", None, "c", "e", "f", None, None, True)
        instance.settings.get_entity.assert_not_called()
        instance._load_attributes.assert_not_called()
        instance._load_customizations.assert_not_called()
        instance.set_enabled_disabled.assert_not_called()

    @patch('HomeAssistantPlugin.actions.show_text.text_action.text_helper')
    def test_refresh_no_entity(self, text_helper_mock):
        instance = ShowText.__new__(ShowText)
        instance.initialized = True
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_bottom_label = Mock()
        instance.set_label = Mock()
        instance.settings = Mock()
        instance.settings.get_entity.return_value = ""
        instance._load_attributes = Mock()
        instance._load_customizations = Mock()
        instance.set_enabled_disabled = Mock()

        instance.refresh()

        instance.set_top_label.assert_called_once_with(text_const.EMPTY_STRING)
        instance.set_center_label.assert_called_once_with(text_const.EMPTY_STRING)
        instance.set_bottom_label.assert_called_once_with(text_const.EMPTY_STRING)
        instance.settings.get_entity.assert_called_once()
        instance._load_attributes.assert_not_called()
        instance._load_customizations.assert_not_called()
        instance.set_enabled_disabled.assert_not_called()

    @patch('HomeAssistantPlugin.actions.show_text.text_action.text_helper')
    def test_refresh_no_state(self, text_helper_mock):
        instance = ShowText.__new__(ShowText)
        instance.initialized = True
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_bottom_label = Mock()
        instance.set_label = Mock()
        instance.settings = Mock()
        instance.settings.get_entity.return_value = "entity"
        instance.plugin_base = Mock()
        instance.plugin_base.backend.get_entity.return_value = None
        instance._load_attributes = Mock()
        instance._load_customizations = Mock()
        instance.set_enabled_disabled = Mock()

        instance.refresh()

        instance.set_top_label.assert_called_once_with(text_const.EMPTY_STRING)
        instance.set_center_label.assert_called_once_with(text_const.EMPTY_STRING)
        instance.set_bottom_label.assert_called_once_with(text_const.EMPTY_STRING)
        instance.settings.get_entity.assert_called_once()
        instance._load_attributes.assert_called_once()
        instance._load_customizations.assert_not_called()
        instance.set_enabled_disabled.assert_not_called()

    @patch('HomeAssistantPlugin.actions.show_text.text_action.text_helper')
    def test_refresh_success(self, text_helper_mock):
        instance = ShowText.__new__(ShowText)
        instance.initialized = True
        instance.set_top_label = Mock()
        instance.set_center_label = Mock()
        instance.set_bottom_label = Mock()
        instance.set_label = Mock()
        instance.settings = Mock()
        instance.settings.get_entity.return_value = "entity"
        instance.plugin_base = Mock()
        instance.plugin_base.backend.is_connected.return_value = True
        instance.plugin_base.backend.get_entity.return_value = {"state": "state"}
        instance._load_attributes = Mock()
        instance._load_customizations = Mock()
        instance.set_enabled_disabled = Mock()
        text_helper_mock.get_text.return_value = ("a", "b", "c", "d", "e", "f")

        instance.refresh()

        instance.set_top_label.assert_called_once_with(text_const.EMPTY_STRING)
        instance.set_center_label.assert_called_once_with(text_const.EMPTY_STRING)
        instance.set_bottom_label.assert_called_once_with(text_const.EMPTY_STRING)
        instance.settings.get_entity.assert_called_once()
        instance._load_attributes.assert_called_once()
        text_helper_mock.get_text.assert_called_once_with({"state": "state"}, instance.settings, True)
        instance.set_label.assert_called_once_with("a", "b", "d", None, "c", "e", "f", None, None, True)
        instance._load_customizations.assert_called_once()
        instance.set_enabled_disabled.assert_called_once()

    def test_get_domains(self):
        instance = ShowText.__new__(ShowText)
        instance.plugin_base = Mock()
        instance.plugin_base.backend.get_domains_for_entities.return_value = ["domain1", "domain2"]

        result = instance._get_domains()

        instance.plugin_base.backend.get_domains_for_entities.assert_called_once()
        self.assertEqual(result, ["domain1", "domain2"])

    def test_load_attributes_none_attribute(self):
        instance = ShowText.__new__(ShowText)
        instance.settings = Mock()
        instance.settings.get_attribute.return_value = None
        instance._get_attributes = Mock()
        instance._get_attributes.return_value = ["attribute1", "attribute2"]
        instance._get_current_attributes = Mock()
        instance._get_current_attributes.return_value = ["attribute1", "attribute2", "attribute3"]
        instance.attribute = Mock()

        instance._load_attributes()

        instance.attribute.populate.assert_called_once_with(
            ["attribute1", "attribute2"],
            None,
            trigger_callback=False
        )
