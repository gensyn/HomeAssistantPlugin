import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

absolute_mock_path = str(Path(__file__).parent.parent.parent.parent / "stream_controller_mock")
sys.path.insert(0, absolute_mock_path)

absolute_plugin_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.absolute())
sys.path.insert(0, absolute_plugin_path)

from HomeAssistantPlugin.actions.cores.base_core.base_core import BaseCore


class TestBaseCoreLoadDomains(unittest.TestCase):

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_get_domains")
    def test_load_domains_domain_not_in_domains(self, get_domains_mock, _, __):
        domains = ["switch", "sensor"]
        domain = "light"
        domains_sorted = sorted(domains + [domain])

        get_domains_mock.return_value = domains

        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value=domain)

        domain_combo_mock = Mock()
        domain_combo_mock.populate = Mock()

        instance = BaseCore(Mock(), True)
        instance.initialized = True
        instance.settings = settings_mock
        instance.domain_combo = domain_combo_mock
        assert domain not in domains
        instance._load_domains()

        settings_mock.get_domain.assert_called_once()
        get_domains_mock.assert_called_once()
        domain_combo_mock.populate.assert_called_once_with(domains_sorted, domain, trigger_callback=False)

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_get_domains")
    def test_load_domains_success(self, get_domains_mock, _, __):
        domains = ["light", "switch", "sensor"]
        domains_sorted = sorted(domains)
        domain = "light"

        get_domains_mock.return_value = domains

        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value=domain)

        domain_combo_mock = Mock()
        domain_combo_mock.populate = Mock()

        instance = BaseCore(Mock(), True)
        instance.initialized = True
        instance.settings = settings_mock
        instance.domain_combo = domain_combo_mock
        instance._load_domains()

        settings_mock.get_domain.assert_called_once()
        get_domains_mock.assert_called_once()
        domain_combo_mock.populate.assert_called_once_with(domains_sorted, domain, trigger_callback=False)


    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_get_domains")
    def test_load_domains_with_none_in_domains(self, get_domains_mock, _, __):
        domains = ["switch", None, "sensor"]
        domain = "light"
        domains_sorted = sorted(["switch", "sensor", domain])

        get_domains_mock.return_value = domains

        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value=domain)

        domain_combo_mock = Mock()
        domain_combo_mock.populate = Mock()

        instance = BaseCore(Mock(), True)
        instance.initialized = True
        instance.settings = settings_mock
        instance.domain_combo = domain_combo_mock
        instance._load_domains()

        domain_combo_mock.populate.assert_called_once_with(domains_sorted, domain, trigger_callback=False)

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_get_domains")
    def test_load_domains_no_update_needed(self, get_domains_mock, _, __):
        domains = ["light", "sensor", "switch"]
        domain = "light"

        get_domains_mock.return_value = domains

        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value=domain)

        domain_combo_mock = Mock()
        domain_combo_mock.populate = Mock()

        instance = BaseCore(Mock(), True)
        instance.initialized = True
        instance.settings = settings_mock
        instance.domain_combo = domain_combo_mock
        # Simulate that domains were already loaded (Python-level cache)
        instance._last_loaded_domains = sorted(domains)
        instance._load_domains()

        domain_combo_mock.populate.assert_not_called()

    @patch.object(BaseCore, "create_ui_elements")
    @patch.object(BaseCore, "_create_event_assigner")
    @patch.object(BaseCore, "_get_domains")
    def test_load_domains_no_double_populate_on_repeated_call(self, get_domains_mock, _, __):
        """Second call with identical domains must not trigger a second populate()."""
        domains = ["light", "sensor", "switch"]
        domain = "light"

        get_domains_mock.return_value = domains

        settings_mock = Mock()
        settings_mock.get_domain = Mock(return_value=domain)

        domain_combo_mock = Mock()
        domain_combo_mock.populate = Mock()

        instance = BaseCore(Mock(), True)
        instance.initialized = True
        instance.settings = settings_mock
        instance.domain_combo = domain_combo_mock

        # Two rapid successive calls (simulating double page-load)
        instance._load_domains()
        instance._load_domains()

        # populate() must only have been called once
        domain_combo_mock.populate.assert_called_once_with(sorted(domains), domain, trigger_callback=False)
