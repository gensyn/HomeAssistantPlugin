import sys
import unittest
from pathlib import Path
from unittest.mock import patch

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction


class TestPerformActionOnChangeDomain(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.on_change_entity')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.parameters.parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_domain_not_initialized(self, reload_mock, load_parameters_mock, on_change_entity_mock, _):
        new_entity = 'light.kitchen'
        old_entity = 'switch.living_room'

        instance = PerformAction()
        instance.initialized = False
        instance.on_change_entity(None, new_entity, old_entity)

        on_change_entity_mock.assert_not_called()
        load_parameters_mock.assert_not_called()
        reload_mock.assert_not_called()

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.on_change_entity')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.parameters.parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_domain_same_entity(self, reload_mock, load_parameters_mock, on_change_entity_mock, _):
        new_entity = 'light.kitchen'
        old_entity = 'light.kitchen'

        instance = PerformAction()
        instance.initialized = True
        instance.on_change_entity(None, new_entity, old_entity)

        on_change_entity_mock.assert_not_called()
        load_parameters_mock.assert_not_called()
        reload_mock.assert_not_called()

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.on_change_entity')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.parameters.parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_domain_entity_none(self, reload_mock, load_parameters_mock, on_change_entity_mock, _):
        new_entity = None
        old_entity = 'switch.living_room'

        instance = PerformAction()
        instance.initialized = True
        instance.on_change_entity(None, new_entity, old_entity)

        on_change_entity_mock.assert_called_once()
        load_parameters_mock.assert_not_called()
        reload_mock.assert_called_once()

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.on_change_entity')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.parameters.parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_domain_entity_empty(self, reload_mock, load_parameters_mock, on_change_entity_mock, _):
        new_entity = ""
        old_entity = 'switch.living_room'

        instance = PerformAction()
        instance.initialized = True
        instance.on_change_entity(None, new_entity, old_entity)

        on_change_entity_mock.assert_called_once()
        load_parameters_mock.assert_not_called()
        reload_mock.assert_called_once()

    @patch('HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.__init__')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.perform_action.BaseCore.on_change_entity')
    @patch(
        'HomeAssistantPlugin.actions.perform_action.parameters.parameters_helper.load_parameters')
    @patch.object(PerformAction, '_reload')
    def test_on_change_domain_success(self, reload_mock, load_parameters_mock, on_change_entity_mock, _):
        new_entity = 'light.kitchen'
        old_entity = 'switch.living_room'

        instance = PerformAction()
        instance.initialized = True
        instance.on_change_entity(None, new_entity, old_entity)

        on_change_entity_mock.assert_called_once()
        load_parameters_mock.assert_called_once_with(instance)
        reload_mock.assert_called_once()

