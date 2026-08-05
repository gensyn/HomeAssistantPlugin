import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.level_dial.level_dial import LevelDial


def _make_instance(init_mock, control_indices=None, action_count=1, image_control=0):
    """Create a LevelDial with mocked SC internals."""
    instance = LevelDial()

    indices = control_indices or [0, 0, 0]
    permission_manager = Mock()
    permission_manager.get_label_control_index = Mock(side_effect=lambda i: indices[i])
    permission_manager.get_image_control_index = Mock(return_value=image_control)

    state_mock = Mock()
    state_mock.action_permission_manager = permission_manager

    actions = [Mock() for _ in range(action_count)]

    page_mock = Mock()
    page_mock.get_all_actions_for_input = Mock(return_value=actions)

    instance.get_state = Mock(return_value=state_mock)
    instance.get_own_action_index = Mock(return_value=0)
    instance.page = page_mock
    instance.input_ident = Mock()
    instance.state = 0

    return instance


class TestLevelDialIsControlOrphaned(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_valid_index(self, init_mock):
        instance = _make_instance(init_mock, action_count=3)
        self.assertFalse(instance._is_control_orphaned(2))

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_orphaned_index(self, init_mock):
        instance = _make_instance(init_mock, action_count=1)
        self.assertTrue(instance._is_control_orphaned(2))

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_none_index(self, init_mock):
        instance = _make_instance(init_mock, action_count=1)
        self.assertTrue(instance._is_control_orphaned(None))

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_zero_index_single_action(self, init_mock):
        instance = _make_instance(init_mock, action_count=1)
        self.assertFalse(instance._is_control_orphaned(0))

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_attribute_error_returns_true(self, init_mock):
        instance = LevelDial()
        instance.page = None
        instance.input_ident = Mock()
        instance.state = 0
        self.assertTrue(instance._is_control_orphaned(0))


class TestLevelDialShouldForceLabel(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_top_always_forced(self, init_mock):
        instance = _make_instance(init_mock, control_indices=[1, 0, 0], action_count=2)
        self.assertTrue(instance._should_force_label("top"))

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_center_not_forced_when_valid_owner(self, init_mock):
        instance = _make_instance(init_mock, control_indices=[0, 1, 0], action_count=2)
        self.assertFalse(instance._should_force_label("center"))

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_center_forced_when_orphaned(self, init_mock):
        instance = _make_instance(init_mock, control_indices=[0, 2, 0], action_count=1)
        self.assertTrue(instance._should_force_label("center"))

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_center_forced_when_none(self, init_mock):
        instance = _make_instance(init_mock, control_indices=[0, None, 0], action_count=1)
        self.assertTrue(instance._should_force_label("center"))

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_bottom_forced_when_orphaned(self, init_mock):
        instance = _make_instance(init_mock, control_indices=[0, 0, 3], action_count=2)
        self.assertTrue(instance._should_force_label("bottom"))

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_bottom_not_forced_when_valid_owner(self, init_mock):
        instance = _make_instance(init_mock, control_indices=[0, 0, 1], action_count=2)
        self.assertFalse(instance._should_force_label("bottom"))

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_center_not_forced_when_self_owns(self, init_mock):
        instance = _make_instance(init_mock, control_indices=[0, 0, 0], action_count=1)
        self.assertFalse(instance._should_force_label("center"))
