import sys
import unittest
from pathlib import Path


absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.show_text.text_customization import TextCustomization
from HomeAssistantPlugin.actions.cores.customization_core import customization_const
from HomeAssistantPlugin.actions.show_text import text_const

from HomeAssistantPlugin.actions.cores.customization_core.condition import Condition


class TestTextCustomization(unittest.TestCase):
    
    def test_all(self):
        attribute = "temperature"
        operator = ">"
        value = "20"
        position = "top"
        text_attribute = "state"
        custom_text = "Current Temp"
        do_round = True
        round_precision = 1
        text_size = 12
        text_color = (255, 255, 255, 255)
        outline_size = 2
        outline_color = (0, 0, 0, 255)
        show_unit = True
        line_break = False

        instance = TextCustomization(
            attribute, operator, value, position, text_attribute, custom_text,
            do_round, round_precision, text_size, text_color,
            outline_size, outline_color, show_unit, line_break
        )

        self.assertEqual(attribute, instance.get_attribute())
        self.assertEqual(operator, instance.get_operator())
        self.assertEqual(value, instance.get_value())
        self.assertEqual(position, instance.get_position())
        self.assertEqual(text_attribute, instance.get_text_attribute())
        self.assertEqual(custom_text, instance.get_custom_text())
        self.assertEqual(do_round, instance.get_round())
        self.assertEqual(round_precision, instance.get_round_precision())
        self.assertEqual(text_size, instance.get_text_size())
        self.assertEqual(text_color, instance.get_text_color())
        self.assertEqual(outline_size, instance.get_outline_size())
        self.assertEqual(outline_color, instance.get_outline_color())
        self.assertEqual(show_unit, instance.get_show_unit())
        self.assertEqual(line_break, instance.get_line_break())

        export = instance.export()
        self.assertEqual(attribute, export[customization_const.CONDITION][customization_const.ATTRIBUTE])
        self.assertEqual(operator, export[customization_const.CONDITION][customization_const.OPERATOR])
        self.assertEqual(value, export[customization_const.CONDITION][customization_const.VALUE])
        self.assertEqual(position, export[text_const.CUSTOM_POSITION])
        self.assertEqual(text_attribute, export[text_const.CUSTOM_ATTRIBUTE])
        self.assertEqual(custom_text, export[text_const.CUSTOM_CUSTOM_TEXT])
        self.assertEqual(do_round, export[text_const.CUSTOM_ROUND])
        self.assertEqual(round_precision, export[text_const.CUSTOM_ROUND_PRECISION])
        self.assertEqual(text_size, export[text_const.CUSTOM_TEXT_SIZE])
        self.assertEqual(text_color, export[text_const.CUSTOM_TEXT_COLOR])
        self.assertEqual(outline_size, export[text_const.CUSTOM_OUTLINE_SIZE])
        self.assertEqual(outline_color, export[text_const.CUSTOM_OUTLINE_COLOR])
        self.assertEqual(show_unit, export[text_const.CUSTOM_SHOW_UNIT])
        self.assertEqual(line_break, export[text_const.CUSTOM_LINE_BREAK])

        instance = TextCustomization.from_dict(export)

        self.assertEqual(attribute, instance.get_attribute())
        self.assertEqual(operator, instance.get_operator())
        self.assertEqual(value, instance.get_value())
        self.assertEqual(position, instance.get_position())
        self.assertEqual(text_attribute, instance.get_text_attribute())
        self.assertEqual(custom_text, instance.get_custom_text())
        self.assertEqual(do_round, instance.round)
        self.assertEqual(round_precision, instance.round_precision)
        self.assertEqual(text_size, instance.text_size)
        self.assertEqual(text_color, instance.text_color)
        self.assertEqual(outline_size, instance.outline_size)
        self.assertEqual(outline_color, instance.outline_color)
        self.assertEqual(show_unit, instance.show_unit)
        self.assertEqual(line_break, instance.line_break)

    def test_entity_and_conditions(self):
        instance = TextCustomization(
            "state", "==", "on", "top", "state", None, True, 1, 12, [1, 2, 3, 4], 2, [5, 6, 7, 8], False, True,
            entity="light.a",
            conditions=[Condition("brightness", ">", "5", "light.b", "or")])

        export = instance.export()

        self.assertEqual("light.a", export[customization_const.CONDITION][customization_const.ENTITY])
        self.assertEqual(1, len(export[customization_const.CONDITION][customization_const.CONDITIONS]))

        restored = TextCustomization.from_dict(export)

        self.assertEqual("light.a", restored.get_entity())
        self.assertEqual(instance.get_conditions(), restored.get_conditions())
        self.assertEqual(export, restored.export())
