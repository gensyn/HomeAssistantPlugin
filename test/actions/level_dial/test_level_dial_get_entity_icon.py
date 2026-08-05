import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.level_dial.level_dial import _get_entity_icon


class TestGetEntityIcon(unittest.TestCase):

    def test_mdi_icon_stripped(self):
        state = {"attributes": {"icon": "mdi:lightbulb"}}
        self.assertEqual(_get_entity_icon(state, "fallback"), "lightbulb")

    def test_mdi_prefix_only(self):
        state = {"attributes": {"icon": "mdi:"}}
        self.assertEqual(_get_entity_icon(state, "fallback"), "fallback")

    def test_no_icon_returns_fallback(self):
        state = {"attributes": {}}
        self.assertEqual(_get_entity_icon(state, "fan"), "fan")

    def test_no_attributes_returns_fallback(self):
        state = {}
        self.assertEqual(_get_entity_icon(state, "speaker"), "speaker")

    def test_empty_icon_string_returns_fallback(self):
        state = {"attributes": {"icon": ""}}
        self.assertEqual(_get_entity_icon(state, "tune"), "tune")

    def test_non_mdi_icon_returned_as_is(self):
        state = {"attributes": {"icon": "custom-icon-name"}}
        self.assertEqual(_get_entity_icon(state, "fallback"), "custom-icon-name")
