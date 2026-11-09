import sys
import unittest
from pathlib import Path

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.cores.customization_core import customization
from HomeAssistantPlugin.actions.cores.customization_core.condition import Condition


class TestCustomization(unittest.TestCase):
    def test_getters(self):
        cust = customization.Customization("temperature", ">", "20")
        self.assertEqual(cust.get_attribute(), "temperature")
        self.assertEqual(cust.get_operator(), ">")
        self.assertEqual(cust.get_value(), "20")

    def test_export_not_implemented(self):
        cust = customization.Customization("humidity", "<", "50")
        with self.assertRaises(NotImplementedError):
            cust.export()

    def test_entity_and_conditions_default(self):
        cust = customization.Customization("temperature", ">", "20")
        self.assertIsNone(cust.get_entity())
        self.assertEqual([], cust.get_conditions())
        self.assertEqual(set(), cust.get_entities())
        self.assertEqual({"attribute": "temperature", "operator": ">", "value": "20"}, cust.export_condition())

    def test_all_conditions_and_entities(self):
        additional = [Condition("state", "==", "on", "light.b", "or"), Condition("state", "==", "x", "light.a")]
        cust = customization.Customization("temperature", ">", "20", "light.a", additional)

        self.assertEqual("light.a", cust.get_entity())
        self.assertEqual(additional, cust.get_conditions())
        self.assertEqual([Condition("temperature", ">", "20", "light.a")] + additional, cust.get_all_conditions())
        self.assertEqual({"light.a", "light.b"}, cust.get_entities())

    def test_export_and_parse_condition(self):
        additional = [Condition("state", "==", "on", "light.b", "or")]
        cust = customization.Customization("temperature", ">", "20", "light.a", additional)

        exported = cust.export_condition()

        self.assertEqual({
            "attribute": "temperature", "operator": ">", "value": "20", "entity": "light.a",
            "conditions": [{"attribute": "state", "operator": "==", "value": "on", "entity": "light.b",
                            "logic": "or"}]
        }, exported)

        parsed = customization.Customization(**customization.Customization.parse_condition(exported))
        self.assertEqual(exported, parsed.export_condition())

    def test_parse_condition_without_new_fields(self):
        parsed = customization.Customization.parse_condition(
            {"attribute": "temperature", "operator": ">", "value": "20"})
        self.assertEqual({"attribute": "temperature", "operator": ">", "value": "20", "entity": None,
                          "conditions": []}, parsed)

    def test_matches(self):
        cust = customization.Customization("a", "==", "1", None, [Condition("b", "==", "1", logic="or")])
        self.assertTrue(cust.matches(lambda c: "1" if c.attribute == "b" else "0"))
        self.assertFalse(cust.matches(lambda c: "0"))
