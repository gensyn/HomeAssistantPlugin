import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, call

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.show_icon import icon_const
from HomeAssistantPlugin.actions.show_icon import icon_helper
from HomeAssistantPlugin.actions.show_icon.icon_action import ShowIcon
from HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization
from HomeAssistantPlugin.actions.show_icon.icon_row import IconRow
from HomeAssistantPlugin.actions.show_icon.icon_settings import ShowIconSettings
from HomeAssistantPlugin.actions.show_icon.icon_window import IconWindow

class TestShowIcon(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.show_icon.icon_action.CustomizationCore.__init__')
    def test_init(self, super_init_mock):
        arg = "abc"
        kwargs = {"key": "value"}

        ShowIcon(*arg, **kwargs)

        super_init_mock.assert_called_once_with(
            window_implementation=IconWindow,
            customization_implementation=IconCustomization,
            row_implementation=IconRow,
            settings_implementation=ShowIconSettings,
            track_entity=True,
            *arg,
            **kwargs
        )

    def test_get_config_rows(self):
        instance = ShowIcon.__new__(ShowIcon)
        instance.domain_combo = Mock()
        instance.domain_combo.widget = "domain_combo_widget"
        instance.entity_combo = Mock()
        instance.entity_combo.widget = "entity_combo_widget"
        instance.icon = Mock()
        instance.icon.widget = "icon_widget"
        instance.color = Mock()
        instance.color.widget = "color_widget"
        instance.scale = Mock()
        instance.scale.widget = "scale_widget"
        instance.opacity = Mock()
        instance.opacity.widget = "opacity_widget"
        instance.customization_expander = Mock()
        instance.customization_expander.widget = "customization_expander_widget"

        expected_rows = [
            "domain_combo_widget",
            "entity_combo_widget",
            "icon_widget",
            "color_widget",
            "scale_widget",
            "opacity_widget",
            "customization_expander_widget"
        ]

        self.assertEqual(instance.get_config_rows(), expected_rows)

    @patch('HomeAssistantPlugin.actions.show_icon.icon_action.CustomizationCore.create_ui_elements')
    @patch('HomeAssistantPlugin.actions.show_icon.icon_action.EntryRow')
    @patch('HomeAssistantPlugin.actions.show_icon.icon_action.ColorButtonRow')
    @patch('HomeAssistantPlugin.actions.show_icon.icon_action.ScaleRow')
    @patch('HomeAssistantPlugin.actions.show_icon.icon_action.Button')
    def testcreate_ui_elements(self, button_mock, scale_row_mock, color_button_row_mock, entry_row_mock, super_create_ui_elements_mock):
        instance = ShowIcon.__new__(ShowIcon)
        instance._reload = Mock()
        instance.lm = Mock()
        instance.lm.get.return_value = "Browse"

        instance.create_ui_elements()

        super_create_ui_elements_mock.assert_called_once()
        self.assertTrue(hasattr(instance, 'icon'))
        self.assertTrue(hasattr(instance, 'color'))
        self.assertTrue(hasattr(instance, 'scale'))
        self.assertTrue(hasattr(instance, 'opacity'))
        entry_row_mock.assert_called_once_with(
            instance, icon_const.SETTING_ICON_ICON, icon_const.EMPTY_STRING, title=icon_const.LABEL_ICON_ICON, on_change=instance._reload, can_reset=False, complex_var_name=True
        )
        color_button_row_mock.assert_called_once_with(
            instance, icon_const.SETTING_ICON_COLOR, icon_const.DEFAULT_ICON_COLOR, title=icon_const.LABEL_ICON_COLOR, on_change=instance._reload, can_reset=False, complex_var_name=True
        )
        scale_row_mock.assert_has_calls([
            call(
                instance, icon_const.SETTING_ICON_SCALE, icon_const.DEFAULT_ICON_SCALE,
                icon_const.ICON_MIN_SCALE, icon_const.ICON_MAX_SCALE, title=icon_const.LABEL_ICON_SCALE,
                step=1, digits=0, on_change=instance._reload, can_reset=False, complex_var_name=True
            ),
            call(
                instance, icon_const.SETTING_ICON_OPACITY, icon_const.DEFAULT_ICON_OPACITY,
                icon_const.ICON_MIN_OPACITY, icon_const.ICON_MAX_OPACITY,
                title=icon_const.LABEL_ICON_OPACITY, step=1, digits=0, on_change=instance._reload,
                can_reset=False, complex_var_name=True
            )
        ])

    @patch('HomeAssistantPlugin.actions.show_icon.icon_action.CustomizationCore.set_enabled_disabled')
    def test_set_enabled_disabled_no_domain(self, super_set_enabled_disabled_mock):
        lm = {
            icon_const.LABEL_ICON_NO_ENTITY: "No entity selected"
        }

        instance = ShowIcon.__new__(ShowIcon)
        instance.initialized = True
        instance.settings = Mock()
        instance.settings.get_domain.return_value = ""
        instance.settings.get_entity.return_value = "entity"
        instance.icon = Mock()
        instance.color = Mock()
        instance.scale = Mock()
        instance.opacity = Mock()
        instance.lm = lm

        instance.set_enabled_disabled()

        super_set_enabled_disabled_mock.assert_called_once()
        instance.icon.widget.set_sensitive.assert_called_once_with(False)
        instance.color.widget.set_sensitive.assert_called_once_with(False)
        instance.color.widget.set_subtitle.assert_called_once_with(lm[icon_const.LABEL_ICON_NO_ENTITY])
        instance.scale.widget.set_sensitive.assert_called_once_with(False)
        instance.scale.widget.set_subtitle.assert_called_once_with(lm[icon_const.LABEL_ICON_NO_ENTITY])
        instance.opacity.widget.set_sensitive.assert_called_once_with(False)
        instance.opacity.widget.set_subtitle.assert_called_once_with(lm[icon_const.LABEL_ICON_NO_ENTITY])

    @patch('HomeAssistantPlugin.actions.show_icon.icon_action.CustomizationCore.set_enabled_disabled')
    def test_set_enabled_disabled_no_entity(self, super_set_enabled_disabled_mock):
        lm = {
            icon_const.LABEL_ICON_NO_ENTITY: "No entity selected"
        }

        instance = ShowIcon.__new__(ShowIcon)
        instance.initialized = True
        instance.settings = Mock()
        instance.settings.get_domain.return_value = "domain"
        instance.settings.get_entity.return_value = ""
        instance.icon = Mock()
        instance.color = Mock()
        instance.scale = Mock()
        instance.opacity = Mock()
        instance.lm = lm

        instance.set_enabled_disabled()

        super_set_enabled_disabled_mock.assert_called_once()
        instance.icon.widget.set_sensitive.assert_called_once_with(False)
        instance.color.widget.set_sensitive.assert_called_once_with(False)
        instance.color.widget.set_subtitle.assert_called_once_with(lm[icon_const.LABEL_ICON_NO_ENTITY])
        instance.scale.widget.set_sensitive.assert_called_once_with(False)
        instance.scale.widget.set_subtitle.assert_called_once_with(lm[icon_const.LABEL_ICON_NO_ENTITY])
        instance.opacity.widget.set_sensitive.assert_called_once_with(False)
        instance.opacity.widget.set_subtitle.assert_called_once_with(lm[icon_const.LABEL_ICON_NO_ENTITY])

    @patch('HomeAssistantPlugin.actions.show_icon.icon_action.CustomizationCore.set_enabled_disabled')
    def test_set_enabled_disabled_success(self, super_set_enabled_disabled_mock):
        instance = ShowIcon.__new__(ShowIcon)
        instance.initialized = True
        instance.settings = Mock()
        instance.settings.get_domain.return_value = "domain"
        instance.settings.get_entity.return_value = "entity"
        instance.settings.get_icon.return_value = next(iter(icon_helper.MDI_ICONS))
        instance.icon = Mock()
        instance.color = Mock()
        instance.scale = Mock()
        instance.opacity = Mock()
        instance.lm = Mock()

        instance.set_enabled_disabled()

        super_set_enabled_disabled_mock.assert_called_once()
        instance.icon.widget.set_sensitive.assert_called_once_with(True)
        instance.color.widget.set_sensitive.assert_called_once_with(True)
        instance.color.widget.set_subtitle.assert_called_once_with(icon_const.EMPTY_STRING)
        instance.scale.widget.set_sensitive.assert_called_once_with(True)
        instance.scale.widget.set_subtitle.assert_called_once_with(icon_const.EMPTY_STRING)
        instance.opacity.widget.set_sensitive.assert_called_once_with(True)
        instance.opacity.widget.set_subtitle.assert_called_once_with(icon_const.EMPTY_STRING)

    @patch('HomeAssistantPlugin.actions.show_icon.icon_action.icon_helper')
    def test_refresh_not_initialized_not_connected(self, icon_helper_mock):
        instance = ShowIcon.__new__(ShowIcon)
        instance.initialized = False
        instance.plugin_base = Mock()
        instance.plugin_base.backend.is_connected.return_value = False
        instance.settings = Mock()
        instance.set_media = Mock()
        instance._load_customizations = Mock()
        instance.set_enabled_disabled = Mock()
        icon_helper_mock.get_icon.return_value = ("icon_path", 3)

        state = {"state_key": "state_value"}

        instance.refresh(state)

        icon_helper_mock.get_icon.assert_called_once_with(state, instance.settings, False)
        instance.set_media.assert_called_once_with(media_path="icon_path", size=3)
        instance.settings.get_entity.assert_not_called()
        instance._load_customizations.assert_not_called()
        instance.set_enabled_disabled.assert_not_called()

    def test_refresh_no_state(self):
        instance = ShowIcon.__new__(ShowIcon)
        instance.initialized = True
        instance.plugin_base = Mock()
        instance.plugin_base.backend.get_entity.return_value = None
        instance.settings = Mock()
        instance.settings.get_entity.return_value = "entity_id"
        instance.set_media = Mock()
        instance._load_customizations = Mock()
        instance.set_enabled_disabled = Mock()

        instance.refresh()

        instance.set_media.assert_called_once_with()
        instance.plugin_base.backend.get_entity.assert_called_once_with("entity_id")
        instance._load_customizations.assert_not_called()
        instance.set_enabled_disabled.assert_not_called()

    @patch('HomeAssistantPlugin.actions.show_icon.icon_action.icon_helper')
    def test_refresh_state_from_backend(self, icon_helper_mock):
        state = {"state_key": "state_value"}

        instance = ShowIcon.__new__(ShowIcon)
        instance.initialized = True
        instance.plugin_base = Mock()
        instance.plugin_base.backend.is_connected.return_value = True
        instance.plugin_base.backend.get_entity.return_value = state
        instance.settings = Mock()
        instance.settings.get_entity.return_value = "entity_id"
        instance.set_media = Mock()
        instance._load_customizations = Mock()
        instance.set_enabled_disabled = Mock()
        icon_helper_mock.get_icon.return_value = ("icon_path", 3)

        instance.refresh()

        instance.plugin_base.backend.get_entity.assert_called_once_with("entity_id")
        icon_helper_mock.get_icon.assert_called_once_with(state, instance.settings, True)
        instance.set_media.assert_called_once_with(media_path="icon_path", size=3)
        instance._load_customizations.assert_called_once()
        instance.set_enabled_disabled.assert_called_once()

    @patch('HomeAssistantPlugin.actions.show_icon.icon_action.icon_helper')
    def test_refresh_state_as_parameter(self, icon_helper_mock):
        state = {"state_key": "state_value"}

        instance = ShowIcon.__new__(ShowIcon)
        instance.initialized = True
        instance.plugin_base = Mock()
        instance.plugin_base.backend.is_connected.return_value = True
        instance.settings = Mock()
        instance.settings.get_entity.return_value = "entity_id"
        instance.set_media = Mock()
        instance._load_customizations = Mock()
        instance.set_enabled_disabled = Mock()
        icon_helper_mock.get_icon.return_value = ("icon_path", 3)

        instance.refresh(state)

        instance.plugin_base.backend.get_entity.assert_not_called()
        icon_helper_mock.get_icon.assert_called_once_with(state, instance.settings, True)
        instance.set_media.assert_called_once_with(media_path="icon_path", size=3)
        instance._load_customizations.assert_called_once()
        instance.set_enabled_disabled.assert_called_once()

    def test_get_domains(self):
        instance = ShowIcon.__new__(ShowIcon)
        instance.plugin_base = Mock()
        instance.plugin_base.backend.get_domains_for_entities.return_value = ["domain1", "domain2"]

        result = instance._get_domains()

        instance.plugin_base.backend.get_domains_for_entities.assert_called_once()
        self.assertEqual(result, ["domain1", "domain2"])
