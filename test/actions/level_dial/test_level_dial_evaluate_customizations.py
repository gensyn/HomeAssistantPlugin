import sys
import unittest
from pathlib import Path

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.level_dial.level_dial import _evaluate_customizations
from HomeAssistantPlugin.actions.level_dial.level_customization import LevelDialCustomization


class TestEvaluateCustomizations(unittest.TestCase):

    def _make_customization(self, attribute="state", operator="==", value="on",
                            icon=None, color=None):
        return LevelDialCustomization(
            attribute=attribute, operator=operator, value=value,
            icon=icon, color=color
        )

    def test_no_customizations_returns_defaults(self):
        state = {"state": "on", "attributes": {}}
        icon, color = _evaluate_customizations(state, [], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "lightbulb")
        self.assertEqual(color, "#ffdd00")

    def test_equals_match_overrides_icon(self):
        cust = self._make_customization(operator="==", value="on", icon="sun")
        state = {"state": "on", "attributes": {}}
        icon, color = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "sun")
        self.assertEqual(color, "#ffdd00")

    def test_equals_no_match_keeps_defaults(self):
        cust = self._make_customization(operator="==", value="off", icon="sun")
        state = {"state": "on", "attributes": {}}
        icon, color = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "lightbulb")

    def test_not_equals_match(self):
        cust = self._make_customization(operator="!=", value="off", icon="sun")
        state = {"state": "on", "attributes": {}}
        icon, color = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "sun")

    def test_not_equals_no_match(self):
        cust = self._make_customization(operator="!=", value="on", icon="sun")
        state = {"state": "on", "attributes": {}}
        icon, color = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "lightbulb")

    def test_greater_than_match(self):
        cust = self._make_customization(
            attribute="brightness", operator=">", value="100", icon="sun"
        )
        state = {"state": "on", "attributes": {"brightness": 200}}
        icon, _ = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "sun")

    def test_greater_than_no_match(self):
        cust = self._make_customization(
            attribute="brightness", operator=">", value="100", icon="sun"
        )
        state = {"state": "on", "attributes": {"brightness": 50}}
        icon, _ = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "lightbulb")

    def test_less_than_match(self):
        cust = self._make_customization(
            attribute="brightness", operator="<", value="100", icon="moon"
        )
        state = {"state": "on", "attributes": {"brightness": 50}}
        icon, _ = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "moon")

    def test_greater_than_equals_match(self):
        cust = self._make_customization(
            attribute="brightness", operator=">=", value="100", icon="sun"
        )
        state = {"state": "on", "attributes": {"brightness": 100}}
        icon, _ = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "sun")

    def test_less_than_equals_match(self):
        cust = self._make_customization(
            attribute="brightness", operator="<=", value="100", icon="moon"
        )
        state = {"state": "on", "attributes": {"brightness": 100}}
        icon, _ = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "moon")

    def test_color_override(self):
        cust = self._make_customization(operator="==", value="on", color=[255, 0, 0, 255])
        state = {"state": "on", "attributes": {}}
        _, color = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(color, "#FF0000")

    def test_icon_and_color_override(self):
        cust = self._make_customization(
            operator="==", value="on", icon="alert", color=[255, 0, 0, 255]
        )
        state = {"state": "on", "attributes": {}}
        icon, color = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "alert")
        self.assertEqual(color, "#FF0000")

    def test_only_icon_no_color_keeps_default_color(self):
        cust = self._make_customization(operator="==", value="on", icon="sun")
        state = {"state": "on", "attributes": {}}
        _, color = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(color, "#ffdd00")

    def test_only_color_no_icon_keeps_default_icon(self):
        cust = self._make_customization(operator="==", value="on", color=[0, 255, 0, 255])
        state = {"state": "on", "attributes": {}}
        icon, _ = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "lightbulb")

    def test_last_match_wins(self):
        cust1 = self._make_customization(operator="==", value="on", icon="sun")
        cust2 = self._make_customization(operator="==", value="on", icon="lamp")
        state = {"state": "on", "attributes": {}}
        icon, _ = _evaluate_customizations(state, [cust1, cust2], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "lamp")

    def test_numeric_equality_int_vs_float(self):
        cust = self._make_customization(
            attribute="brightness", operator="==", value="21", icon="sun"
        )
        state = {"state": "on", "attributes": {"brightness": 21.0}}
        icon, _ = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "sun")

    def test_non_numeric_comparison_skipped(self):
        cust = self._make_customization(
            attribute="state", operator=">", value="on", icon="sun"
        )
        state = {"state": "off", "attributes": {}}
        icon, _ = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "lightbulb")

    def test_attribute_value_none(self):
        cust = self._make_customization(
            attribute="brightness", operator=">", value="100", icon="sun"
        )
        state = {"state": "on", "attributes": {}}
        icon, _ = _evaluate_customizations(state, [cust], "lightbulb", "#ffdd00")

        self.assertEqual(icon, "lightbulb")
