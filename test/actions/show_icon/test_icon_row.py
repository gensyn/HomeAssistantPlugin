import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.show_icon import icon_const
from HomeAssistantPlugin.actions.show_icon.icon_row import IconRow
from HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization

class TestIconRow(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.show_icon.icon_row.CustomizationRow.__init__', autospec=True)
    @patch('HomeAssistantPlugin.actions.show_icon.icon_row.icon_helper')
    @patch('HomeAssistantPlugin.actions.show_icon.icon_row.customization_helper')
    @patch.object(IconRow, '_init_title')
    @patch.object(IconRow, 'set_title')
    def test_init(self, set_title_mock, init_title_mock, customization_helper_mock, icon_helper_mock, super_init_mock):
        lm = {
            icon_const.LABEL_ICON_ICON: "Icon",
            icon_const.LABEL_ICON_COLOR: "Color",
            icon_const.LABEL_ICON_SCALE: "Scale",
            icon_const.LABEL_ICON_OPACITY: "Opacity"
        }

        def super_init(instance, lm, *args, **kwargs):
            instance.lm = lm

        super_init_mock.side_effect = super_init
        init_title_mock.return_value = "Title"
        customization_helper_mock.convert_color_list_to_hex.return_value = "#FF0000"

        customization_mock = Mock()
        customization_mock.get_icon.return_value = "icon_name"
        customization_mock.get_color.return_value = [255, 0, 0]
        customization_mock.get_scale.return_value = 150
        customization_mock.get_opacity.return_value = 80
        customization_count = 5
        index = 3
        attributes = ['attr1', 'attr2']
        state = {'state_key': 'state_value'}
        settings = "settings"

        instance = IconRow(lm, customization_mock, customization_count, index, attributes, state, settings)

        super_init_mock.assert_called_once_with(instance, lm, customization_count, index, attributes, state, settings, None) # with instance because of autospec
        init_title_mock.assert_called_once()
        self.assertEqual(customization_mock, init_title_mock.call_args.args[0])
        condition = Mock()
        init_title_mock.call_args.args[1](condition)
        icon_helper_mock.get_condition_value.assert_called_once_with(state, condition, None)
        set_title_mock.assert_called_once_with(
            "Title\nIcon icon_name\nColor #FF0000\nScale 150\nOpacity 80"
        )