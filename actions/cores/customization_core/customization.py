"""
Modul to manage customizations.
"""

from typing import Any, Callable

from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.cores.customization_core.condition import Condition, evaluate


class Customization:
    """
    Base class to represent a customization.
    """

    def __init__(self, attribute: str, operator: str, value: str, entity: str = None,
                 conditions: list[Condition] = None):
        self.attribute: str = attribute
        self.operator: str = operator
        self.value: str = value
        self.entity: str = entity or None
        self.conditions: list[Condition] = list(conditions) if conditions else []

    @staticmethod
    def parse_condition(condition: dict) -> dict[str, Any]:
        """
        Convert an exported condition to the keyword arguments of the constructor.
        :param condition: the exported condition
        :return: the keyword arguments
        """
        return {
            "attribute": condition[customization_const.ATTRIBUTE],
            "operator": condition[customization_const.OPERATOR],
            "value": condition[customization_const.VALUE],
            "entity": condition.get(customization_const.ENTITY),
            "conditions": [Condition.from_dict(c) for c in condition.get(customization_const.CONDITIONS, [])],
        }

    def export_condition(self) -> dict[str, Any]:
        """
        Get the condition of this customization as a dict.
        :return: the condition as a dict
        """
        condition = {
            customization_const.ATTRIBUTE: self.attribute,
            customization_const.OPERATOR: self.operator,
            customization_const.VALUE: self.value,
        }
        if self.entity:
            condition[customization_const.ENTITY] = self.entity
        if self.conditions:
            condition[customization_const.CONDITIONS] = [c.export() for c in self.conditions]
        return condition

    def get_entity(self) -> str:
        """
        Get the entity for the condition.
        :return: the entity for the condition or None if it refers to the action's entity
        """
        return self.entity

    def get_conditions(self) -> list[Condition]:
        """
        Get the additional conditions that are combined with the first condition.
        :return: the additional conditions
        """
        return self.conditions

    def get_all_conditions(self) -> list[Condition]:
        """
        Get the first condition and all additional conditions.
        :return: all conditions in order
        """
        return [Condition(self.attribute, self.operator, self.value, self.entity)] + self.conditions

    def get_entities(self) -> set[str]:
        """
        Get all entities that are referenced by the conditions.
        :return: the set of entities
        """
        return {c.entity for c in self.get_all_conditions() if c.entity}

    def matches(self, get_value: Callable[[Condition], Any]) -> bool:
        """
        Check whether the conditions of this customization are fulfilled.
        :param get_value: function to get the current value that a condition refers to
        :return: whether the customization should be applied
        """
        return evaluate(self.get_all_conditions(), get_value)

    def get_attribute(self) -> str:
        """
        Get the attribute for the condition.
        :return: the attribute for the condition
        """
        return self.attribute

    def get_operator(self) -> str:
        """
        Get the operator for the condition.
        :return: the operator for the condition
        """
        return self.operator

    def get_value(self) -> str:
        """
        Get the value for the condition.
        :return: the value for the condition
        """
        return self.value

    def export(self) -> dict[str, Any]:
        """
        Get this customization as a dict. Must be implemented in a subclass.
        :return: this customization as a dict
        """
        raise NotImplementedError
