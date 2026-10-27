import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.cores.customization_core import condition
from HomeAssistantPlugin.actions.cores.customization_core.condition import Condition


class TestCondition(unittest.TestCase):
    def test_export_and_from_dict_minimal(self):
        cond = Condition("state", "==", "on")

        exported = cond.export()

        self.assertEqual({"attribute": "state", "operator": "==", "value": "on"}, exported)
        self.assertEqual(cond, Condition.from_dict(exported))
        self.assertIsNone(cond.entity)
        self.assertEqual("and", cond.logic)

    def test_export_and_from_dict_full(self):
        cond = Condition("brightness", ">", "5", "light.a", "or")

        exported = cond.export()

        self.assertEqual({"attribute": "brightness", "operator": ">", "value": "5", "entity": "light.a",
                          "logic": "or"}, exported)
        self.assertEqual(cond, Condition.from_dict(exported))

    def test_unknown_logic_is_and(self):
        self.assertEqual("and", Condition("state", "==", "on", logic="xor").logic)

    def test_empty_entity_is_none(self):
        self.assertIsNone(Condition("state", "==", "on", "").entity)

    def test_get_state_value(self):
        state = {"state": "on", "attributes": {"brightness": 5}}
        self.assertEqual("on", condition.get_state_value(state, "state"))
        self.assertEqual(5, condition.get_state_value(state, "brightness"))
        self.assertIsNone(condition.get_state_value(state, "missing"))
        self.assertIsNone(condition.get_state_value(None, "state"))
        self.assertIsNone(condition.get_state_value({"state": "on"}, "brightness"))

    def test_resolve_state(self):
        own = {"state": "own"}
        other = {"state": "other"}
        get_entity = Mock(return_value=other)

        self.assertEqual(own, condition.resolve_state(own, None, get_entity))
        get_entity.assert_not_called()
        self.assertEqual(other, condition.resolve_state(own, "light.a", get_entity))
        get_entity.assert_called_once_with("light.a")
        self.assertEqual({}, condition.resolve_state(own, "light.a", None))
        self.assertEqual({}, condition.resolve_state(own, "light.a", Mock(return_value=None)))

    def test_compare_equality(self):
        self.assertTrue(condition.compare("on", "==", "on"))
        self.assertFalse(condition.compare("on", "==", "off"))
        self.assertTrue(condition.compare("on", "!=", "off"))
        self.assertFalse(condition.compare("on", "!=", "on"))
        self.assertTrue(condition.compare(21, "==", "21.0"))
        self.assertTrue(condition.compare("21", "==", 21.0))

    def test_compare_numbers(self):
        self.assertTrue(condition.compare("21", "<", "22"))
        self.assertFalse(condition.compare("22", "<", "22"))
        self.assertTrue(condition.compare("22", "<=", "22"))
        self.assertTrue(condition.compare("23", ">", "22"))
        self.assertFalse(condition.compare("22", ">", "22"))
        self.assertTrue(condition.compare("22", ">=", "22"))

    def test_compare_non_numbers_with_numeric_operator(self):
        self.assertFalse(condition.compare("abc", ">", "1"))
        self.assertFalse(condition.compare(None, "<", "1"))

    def test_compare_invalid_expected_value(self):
        with patch("HomeAssistantPlugin.actions.cores.customization_core.condition.logging.error") as log_mock:
            self.assertFalse(condition.compare("21", ">", "abc"))
            log_mock.assert_called_once_with("Could not convert custom value to float: %s", "abc")

    def test_evaluate_empty(self):
        self.assertFalse(condition.evaluate([], Mock()))

    def test_evaluate_single(self):
        self.assertTrue(condition.evaluate([Condition("state", "==", "on")], lambda c: "on"))
        self.assertFalse(condition.evaluate([Condition("state", "==", "on")], lambda c: "off"))

    def test_evaluate_and_or_precedence(self):
        # a or b and c  ==  a or (b and c)
        a = Condition("a", "==", "1")
        b = Condition("b", "==", "1", logic="or")
        c = Condition("c", "==", "1", logic="and")

        def evaluate(values):
            return condition.evaluate([a, b, c], lambda cond: values[cond.attribute])

        self.assertTrue(evaluate({"a": "1", "b": "0", "c": "0"}))
        self.assertTrue(evaluate({"a": "0", "b": "1", "c": "1"}))
        self.assertFalse(evaluate({"a": "0", "b": "1", "c": "0"}))
        self.assertFalse(evaluate({"a": "0", "b": "0", "c": "1"}))

    def test_evaluate_and_chain(self):
        conditions = [Condition("a", "==", "1"), Condition("b", "==", "1"), Condition("c", "==", "1")]
        self.assertTrue(condition.evaluate(conditions, lambda cond: "1"))
        self.assertFalse(condition.evaluate(conditions, lambda cond: "0" if cond.attribute == "c" else "1"))

    def test_evaluate_or_chain(self):
        conditions = [Condition("a", "==", "1"), Condition("b", "==", "1", logic="or"),
                      Condition("c", "==", "1", logic="or")]
        self.assertTrue(condition.evaluate(conditions, lambda cond: "1" if cond.attribute == "c" else "0"))
        self.assertFalse(condition.evaluate(conditions, lambda cond: "0"))
