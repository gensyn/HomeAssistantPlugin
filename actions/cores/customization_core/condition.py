"""
Module to evaluate customization conditions.
"""
import logging
from typing import Any, Callable

from HomeAssistantPlugin.actions.cores.customization_core import customization_const


class Condition:
    """
    A single condition that compares the state or an attribute of an entity with a value.
    If no entity is set, the condition refers to the entity of the action.
    The logic defines how the condition is combined with the preceding condition.
    """

    def __init__(self, attribute: str, operator: str, value: str, entity: str = None,
                 logic: str = customization_const.AND):
        self.attribute: str = attribute
        self.operator: str = operator
        self.value: str = value
        self.entity: str = entity or None
        self.logic: str = logic if logic == customization_const.OR else customization_const.AND

    @classmethod
    def from_dict(cls, condition: dict):
        return cls(condition[customization_const.ATTRIBUTE], condition[customization_const.OPERATOR],
                   condition[customization_const.VALUE], condition.get(customization_const.ENTITY),
                   condition.get(customization_const.LOGIC, customization_const.AND))

    def export(self) -> dict[str, Any]:
        """
        Get this condition as a dict.
        :return: this condition as a dict
        """
        exported = {
            customization_const.ATTRIBUTE: self.attribute,
            customization_const.OPERATOR: self.operator,
            customization_const.VALUE: self.value,
        }
        if self.entity:
            exported[customization_const.ENTITY] = self.entity
        if self.logic == customization_const.OR:
            exported[customization_const.LOGIC] = self.logic
        return exported

    def __eq__(self, other) -> bool:
        return isinstance(other, Condition) and self.export() == other.export()

    def __hash__(self) -> int:
        return hash((self.attribute, self.operator, self.value, self.entity, self.logic))


def get_state_value(state: dict, attribute: str) -> Any:
    """
    Gets the state or the attribute value from an entity's state dict.
    """
    if state is None:
        return None
    if attribute == customization_const.STATE:
        return state.get(customization_const.STATE)
    return state.get(customization_const.ATTRIBUTES, {}).get(attribute)


def resolve_state(state: dict, entity: str, get_entity: Callable[[str], dict] = None) -> dict:
    """
    Gets the state that a condition refers to.
    :param state: the state of the action's entity
    :param entity: the entity of the condition or None if it refers to the action's entity
    :param get_entity: function to get the state of any entity
    """
    if not entity:
        return state
    if get_entity is None:
        return {}
    return get_entity(entity) or {}


def compare(value: Any, operator: str, expected: Any) -> bool:
    """
    Compares a value with the expected value using the operator.
    """
    try:
        # if both values are numbers, convert them both to float
        # if one is int and one float, testing for equality might fail (21 vs 21.0 eg)
        value = float(value)
        expected = float(expected)
    except (ValueError, TypeError):
        pass

    if operator == "==":
        return str(value) == str(expected)
    if operator == "!=":
        return str(value) != str(expected)

    if not isinstance(value, float):
        # other operators are only applicable to numbers
        return False

    try:
        expected = float(expected)
    except (ValueError, TypeError):
        logging.error("Could not convert custom value to float: %s", expected)
        return False

    return ((operator == "<" and value < expected)
            or (operator == "<=" and value <= expected)
            or (operator == ">" and value > expected)
            or (operator == ">=" and value >= expected))


def evaluate(conditions: list[Condition], get_value: Callable[[Condition], Any]) -> bool:
    """
    Evaluates a chain of conditions. "and" binds stronger than "or".
    :param conditions: the conditions; the logic of the first one is ignored
    :param get_value: function to get the current value that a condition refers to
    """
    if not conditions:
        return False

    result = False
    current = compare(get_value(conditions[0]), conditions[0].operator, conditions[0].value)

    for condition in conditions[1:]:
        if condition.logic == customization_const.OR:
            result = result or current
            current = compare(get_value(condition), condition.operator, condition.value)
        else:
            current = current and compare(get_value(condition), condition.operator, condition.value)

    return result or current
