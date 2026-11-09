import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.show_icon import icon_helper, icon_const
from HomeAssistantPlugin.actions.show_icon.icon_settings import ShowIconSettings
from HomeAssistantPlugin.actions.show_icon.icon_customization import IconCustomization
from HomeAssistantPlugin.actions.cores.customization_core.condition import Condition, evaluate


def _mock_customization():
    """A mocked customization whose conditions are evaluated based on the mocked getters."""
    customization = MagicMock(spec=IconCustomization)
    customization.get_entity.return_value = None
    customization.get_all_conditions.side_effect = lambda: [
        Condition(customization.get_attribute(), customization.get_operator(), customization.get_value(),
                  customization.get_entity())]
    customization.matches.side_effect = lambda get_value: evaluate(customization.get_all_conditions(), get_value)
    return customization


class TestIconHelper(unittest.TestCase):
    def setUp(self):
        # Patch MDI_ICONS with keys used for tests
        patcher = patch.object(icon_helper, "MDI_ICONS", {
            "thermometer": "M0,0h24v24H0V0z",
            icon_const.ICON_NETWORK_OFF: "M1,1h22v22H1V1z"
        })
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_get_icon_disconnected(self):
        state = {}
        settings = MagicMock(spec=ShowIconSettings)
        icon, scale = icon_helper.get_icon(state, settings, is_connected=False)
        self.assertIn('<svg', icon)
        self.assertEqual(scale, round(icon_const.DEFAULT_ICON_SCALE / 100, 2))

    def test_get_icon_connected_defaults(self):
        settings = MagicMock(spec=ShowIconSettings)
        settings.get_color.return_value = (255, 0, 0, 255)
        settings.get_scale.return_value = 100
        settings.get_opacity.return_value = 100
        settings.get_icon.return_value = "thermometer"
        settings.get_customizations.return_value = []
        state = {"attributes": {icon_const.ATTRIBUTE_ICON: "thermometer"}}
        with patch("HomeAssistantPlugin.actions.cores.customization_core.customization_helper.convert_color_list_to_hex", return_value="#FF0000FF"):
            icon, scale = icon_helper.get_icon(state, settings, is_connected=True)
            self.assertIn('<svg', icon)
            self.assertEqual(scale, round(settings.get_scale.return_value / 100, 100))
            self.assertIn("#FF0000FF", icon)
            self.assertIn('opacity="1.0"', icon)

    def test_get_icon_settings_with_customization_operator_eq(self):
        customization = _mock_customization()
        customization.get_operator.return_value = "=="
        customization.get_value.return_value = "21"
        customization.get_attribute.return_value = "temperature"
        customization.get_icon.return_value = "thermometer"
        customization.get_color.return_value = (1, 2, 3, 4)
        customization.get_scale.return_value = 2
        customization.get_opacity.return_value = 90

        settings = MagicMock(spec=ShowIconSettings)
        settings.get_color.return_value = (255, 0, 0, 255)
        settings.get_scale.return_value = 100
        settings.get_opacity.return_value = 100
        settings.get_icon.return_value = "thermometer"
        settings.get_customizations.return_value = [customization]
        state = {"attributes": {icon_const.ATTRIBUTE_ICON: "thermometer", "temperature": "21"}}

        name, color, scale, opacity = icon_helper._get_icon_settings(state, settings)
        self.assertEqual(name, "thermometer")
        self.assertEqual(color, (1, 2, 3, 4))
        self.assertEqual(scale, round(customization.get_scale.return_value / 100, 2))
        self.assertEqual(opacity, round(customization.get_opacity.return_value / 100, 90))

    def test_operator_with_non_float_value_triggers_continue(self):
        customization = _mock_customization()
        customization.get_operator.return_value = ">"
        customization.get_value.return_value = "abc"  # not a number
        customization.get_attribute.return_value = "temperature"
        customization.get_icon.return_value = "custom"
        customization.get_color.return_value = (99, 88, 77, 66)
        customization.get_scale.return_value = 9.9
        customization.get_opacity.return_value = 42
        state = {"attributes": {icon_const.ATTRIBUTE_ICON: "thermometer", "temperature": "abc"}}
        settings = MagicMock(spec=ShowIconSettings)
        settings.get_color.return_value = (255, 0, 0, 255)
        settings.get_scale.return_value = 100
        settings.get_opacity.return_value = 100
        settings.get_icon.return_value = "thermometer"
        settings.get_customizations.return_value = [customization]
        # Should not replace values, as value is not a float and triggers continue
        name, color, scale, opacity = icon_helper._get_icon_settings(state, settings)
        assert name != "custom"
        assert color != (99, 88, 77, 66)
        assert scale != 9.9
        assert opacity != 42

    def test_get_value_for_state(self):
        customization = _mock_customization()
        customization.get_attribute.return_value = icon_const.STATE
        state = {icon_const.STATE: "on", "attributes": {}}
        self.assertEqual(icon_helper.get_value(state, customization), "on")

        customization.get_attribute.return_value = "temperature"
        state = {icon_const.STATE: "on", "attributes": {"temperature": "22"}}
        self.assertEqual(icon_helper.get_value(state, customization), "22")

    def test_get_value_for_other_entity(self):
        customization = _mock_customization()
        customization.get_attribute.return_value = icon_const.STATE
        customization.get_entity.return_value = "light.a"
        state = {icon_const.STATE: "on", "attributes": {}}
        get_entity = MagicMock(return_value={icon_const.STATE: "off", "attributes": {}})

        self.assertEqual(icon_helper.get_value(state, customization, get_entity), "off")
        get_entity.assert_called_once_with("light.a")

    def test_customization_on_other_entity(self):
        customization = IconCustomization("state", "==", "on", "custom", None, None, None, entity="light.a")
        settings = MagicMock(spec=ShowIconSettings)
        settings.get_color.return_value = (255, 0, 0, 255)
        settings.get_scale.return_value = 100
        settings.get_opacity.return_value = 100
        settings.get_icon.return_value = "thermometer"
        settings.get_customizations.return_value = [customization]
        state = {icon_const.STATE: "off", "attributes": {}}

        name, _, _, _ = icon_helper._get_icon_settings(
            state, settings, lambda _: {icon_const.STATE: "on", "attributes": {}})
        self.assertEqual("custom", name)

        name, _, _, _ = icon_helper._get_icon_settings(
            state, settings, lambda _: {icon_const.STATE: "off", "attributes": {}})
        self.assertEqual("thermometer", name)

    def test_customization_with_and_or_conditions(self):
        customization = IconCustomization(
            "state", "==", "on", "custom", None, None, None,
            conditions=[Condition("temperature", ">", "20", logic="and"),
                        Condition("state", "==", "unavailable", "light.a", logic="or")])
        settings = MagicMock(spec=ShowIconSettings)
        settings.get_color.return_value = (255, 0, 0, 255)
        settings.get_scale.return_value = 100
        settings.get_opacity.return_value = 100
        settings.get_icon.return_value = "thermometer"
        settings.get_customizations.return_value = [customization]

        def get_icon_name(state, other_state):
            return icon_helper._get_icon_settings(
                state, settings, lambda _: {icon_const.STATE: other_state, "attributes": {}})[0]

        self.assertEqual("custom", get_icon_name({"state": "on", "attributes": {"temperature": "21"}}, "off"))
        self.assertEqual("thermometer", get_icon_name({"state": "on", "attributes": {"temperature": "19"}}, "off"))
        self.assertEqual("custom", get_icon_name({"state": "off", "attributes": {}}, "unavailable"))
        self.assertEqual("thermometer", get_icon_name({"state": "off", "attributes": {}}, "on"))

    def test_replace_values(self):
        customization = _mock_customization()
        customization.get_icon.return_value = "custom"
        customization.get_color.return_value = (10, 20, 30, 40)
        customization.get_scale.return_value = 15
        customization.get_opacity.return_value = 80
        name, color, scale, opacity = icon_helper._replace_values("mdi:icon", (0,0,0,0), 1.0, 100, customization)
        self.assertEqual(name, "custom")
        self.assertEqual(color, (10, 20, 30, 40))
        self.assertEqual(scale, 15)
        self.assertEqual(opacity, 80)

    def test_get_icon_path(self):
        # icon name with mdi: prefix removed
        self.assertEqual(icon_helper._get_icon_path("mdi:thermometer"), "M0,0h24v24H0V0z")
        # icon name not found
        self.assertEqual(icon_helper._get_icon_path("notfound"), "")

    def test_get_icon_svg(self):
        svg = icon_helper._get_icon_svg("thermometer")
        self.assertIn('<svg', svg)
        self.assertIn('d="M0,0h24v24H0V0z"', svg)
        self.assertIn('<color>', svg)
        self.assertIn('<opacity>', svg)

        svg_empty = icon_helper._get_icon_svg("notfound")
        self.assertEqual(svg_empty, "")

class TestGetIconSettingsUncovered(unittest.TestCase):
    def setUp(self):
        # Patch MDI_ICONS with a known value
        patcher = patch.object(icon_helper, "MDI_ICONS", {
            "thermometer": "M0,0h24v24H0V0z"
        })
        self.addCleanup(patcher.stop)
        patcher.start()
        self.state = {"attributes": {icon_const.ATTRIBUTE_ICON: "thermometer", "temperature": "21"}}
        self.settings = MagicMock(spec=ShowIconSettings)
        self.settings.get_color.return_value = (255, 0, 0, 255)
        self.settings.get_scale.return_value = 100
        self.settings.get_opacity.return_value = 100
        self.settings.get_icon.return_value = "thermometer"

    def test_operator_ne(self):
        customization = _mock_customization()
        customization.get_operator.return_value = "!="
        customization.get_value.return_value = "22"
        customization.get_attribute.return_value = "temperature"
        customization.get_icon.return_value = "custom"
        customization.get_color.return_value = (1, 2, 3, 4)
        customization.get_scale.return_value = 2
        customization.get_opacity.return_value = 90
        self.settings.get_customizations.return_value = [customization]
        name, color, scale, opacity = icon_helper._get_icon_settings(self.state, self.settings)
        self.assertEqual(name, "custom")
        self.assertEqual(color, (1, 2, 3, 4))
        self.assertEqual(scale, round(customization.get_scale.return_value / 100, 2))
        self.assertEqual(opacity, round(customization.get_opacity.return_value / 100, 90))

    def test_operator_number_lt(self):
        customization = _mock_customization()
        customization.get_operator.return_value = "<"
        customization.get_value.return_value = "22"
        customization.get_attribute.return_value = "temperature"
        customization.get_icon.return_value = "custom"
        customization.get_color.return_value = (10, 20, 30, 40)
        customization.get_scale.return_value = 15
        customization.get_opacity.return_value = 80
        self.state["attributes"]["temperature"] = "21"
        self.settings.get_customizations.return_value = [customization]
        name, color, scale, opacity = icon_helper._get_icon_settings(self.state, self.settings)
        self.assertEqual(name, "custom")
        self.assertEqual(color, (10, 20, 30, 40))
        self.assertEqual(scale, round(customization.get_scale.return_value / 100, 15))
        self.assertEqual(opacity, round(customization.get_opacity.return_value / 100, 80))

    def test_operator_number_le(self):
        customization = _mock_customization()
        customization.get_operator.return_value = "<="
        customization.get_value.return_value = "21"
        customization.get_attribute.return_value = "temperature"
        customization.get_icon.return_value = "custom"
        customization.get_color.return_value = (11, 22, 33, 44)
        customization.get_scale.return_value = 35
        customization.get_opacity.return_value = 81
        self.state["attributes"]["temperature"] = "21"
        self.settings.get_customizations.return_value = [customization]
        name, color, scale, opacity = icon_helper._get_icon_settings(self.state, self.settings)
        self.assertEqual(name, "custom")
        self.assertEqual(color, (11, 22, 33, 44))
        self.assertEqual(scale, round(customization.get_scale.return_value / 100, 35))
        self.assertEqual(opacity, round(customization.get_opacity.return_value / 100, 81))

    def test_operator_number_gt(self):
        customization = _mock_customization()
        customization.get_operator.return_value = ">"
        customization.get_value.return_value = "20"
        customization.get_attribute.return_value = "temperature"
        customization.get_icon.return_value = "custom"
        customization.get_color.return_value = (12, 23, 34, 45)
        customization.get_scale.return_value = 45
        customization.get_opacity.return_value = 82
        self.state["attributes"]["temperature"] = "21"
        self.settings.get_customizations.return_value = [customization]
        name, color, scale, opacity = icon_helper._get_icon_settings(self.state, self.settings)
        self.assertEqual(name, "custom")
        self.assertEqual(color, (12, 23, 34, 45))
        self.assertEqual(scale, round(customization.get_scale.return_value / 100, 45))
        self.assertEqual(opacity, round(customization.get_opacity.return_value / 100, 82))

    def test_operator_number_ge(self):
        customization = _mock_customization()
        customization.get_operator.return_value = ">="
        customization.get_value.return_value = "21"
        customization.get_attribute.return_value = "temperature"
        customization.get_icon.return_value = "custom"
        customization.get_color.return_value = (13, 24, 35, 46)
        customization.get_scale.return_value = 55
        customization.get_opacity.return_value = 83
        self.state["attributes"]["temperature"] = "21"
        self.settings.get_customizations.return_value = [customization]
        name, color, scale, opacity = icon_helper._get_icon_settings(self.state, self.settings)
        self.assertEqual(name, "custom")
        self.assertEqual(color, (13, 24, 35, 46))
        self.assertEqual(scale, round(customization.get_scale.return_value / 100, 55))
        self.assertEqual(opacity, round(customization.get_opacity.return_value / 100, 83))

    def test_custom_icon_value_not_float(self):
        customization = _mock_customization()
        customization.get_operator.return_value = ">"
        customization.get_value.return_value = "not_a_float"
        customization.get_attribute.return_value = "temperature"
        customization.get_icon.return_value = "custom"
        customization.get_color.return_value = (14, 25, 36, 47)
        customization.get_scale.return_value = 65
        customization.get_opacity.return_value = 84
        self.state["attributes"]["temperature"] = "21"
        self.settings.get_customizations.return_value = [customization]
        # Should not replace values since custom_icon_value conversion fails

        with patch("HomeAssistantPlugin.actions.cores.customization_core.condition.logging.error") as log_mock:
            name, color, scale, opacity = icon_helper._get_icon_settings(self.state, self.settings)
            log_mock.assert_called_once_with("Could not convert custom value to float: %s", "not_a_float")
        self.assertNotEqual(name, "custom")
        self.assertNotEqual(color, (14, 25, 36, 47))
        self.assertNotEqual(scale, round(customization.get_scale.return_value / 100, 65))
        self.assertNotEqual(opacity, round(customization.get_opacity.return_value / 100, 84))