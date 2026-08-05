import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.level_dial.level_dial import LevelDial


class TestLevelDialGetDomains(unittest.TestCase):

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_get_domains_filters_to_supported(self, _):
        """Only returns domains that are both in DOMAIN_CONFIGS and available from backend."""
        plugin_base_mock = Mock()
        plugin_base_mock.backend = Mock()
        plugin_base_mock.backend.get_domains_for_entities = Mock(
            return_value=['light', 'switch', 'fan', 'sensor']
        )

        instance = LevelDial()
        instance.initialized = True
        instance.plugin_base = plugin_base_mock
        result = instance._get_domains()

        # light and fan are in DOMAIN_CONFIGS; switch and sensor are not
        self.assertEqual(result, ['light', 'fan'])
        plugin_base_mock.backend.get_domains_for_entities.assert_called_once()

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_get_domains_preserves_config_order(self, _):
        """Returned domains follow DOMAIN_CONFIGS key order, not backend order."""
        plugin_base_mock = Mock()
        plugin_base_mock.backend = Mock()
        plugin_base_mock.backend.get_domains_for_entities = Mock(
            return_value=['media_player', 'cover', 'fan', 'light']
        )

        instance = LevelDial()
        instance.initialized = True
        instance.plugin_base = plugin_base_mock
        result = instance._get_domains()

        # DOMAIN_CONFIGS order: light, fan, cover, media_player
        self.assertEqual(result, ['light', 'fan', 'cover', 'media_player'])

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_get_domains_none_available(self, _):
        plugin_base_mock = Mock()
        plugin_base_mock.backend = Mock()
        plugin_base_mock.backend.get_domains_for_entities = Mock(
            return_value=['switch', 'sensor', 'automation']
        )

        instance = LevelDial()
        instance.initialized = True
        instance.plugin_base = plugin_base_mock
        result = instance._get_domains()

        self.assertEqual(result, [])

    @patch('HomeAssistantPlugin.actions.level_dial.level_dial.CustomizationCore.__init__')
    def test_get_domains_not_initialized(self, _):
        settings_mock = Mock()

        instance = LevelDial()
        instance.initialized = False
        instance.settings = settings_mock
        instance._get_domains()

        # Should early return due to @requires_initialization
        settings_mock.get_domain.assert_not_called()
