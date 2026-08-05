"""
Modul to manage customizations.
"""

from typing import Any


class Customization:
    """
    Base class to represent a customization.
    """

    def __init__(self, attribute: str, operator: str, value: str):
        self.attribute: str = attribute
        self.operator: str = operator
        self.value: str = value

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
