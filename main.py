"""
Entry point for StreamController to load the plugin.
"""
import sys
from pathlib import Path
from typing import Optional

import gi


gi.require_version("Adw", "1")
from gi.repository import GLib
from gi.repository.Adw import EntryRow, SwitchRow, PasswordEntryRow, PreferencesGroup

ABSOLUTE_PLUGIN_PATH = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, ABSOLUTE_PLUGIN_PATH)

from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.DeckManagement.InputIdentifier import Input

from HomeAssistantPlugin import const
from HomeAssistantPlugin.actions.show_icon.icon_const import SHOW_ICON
from HomeAssistantPlugin.actions.show_icon.icon_action import ShowIcon
from HomeAssistantPlugin.actions.show_text.text_const import SHOW_TEXT
from HomeAssistantPlugin.actions.show_text.text_action import ShowText
from HomeAssistantPlugin.actions.perform_action.perform_const import PERFORM_ACTION
from HomeAssistantPlugin.actions.perform_action.perform_action import PerformAction
from HomeAssistantPlugin.actions.level_dial.level_const import LEVEL_DIAL
from HomeAssistantPlugin.actions.level_dial.level_dial import LevelDial
from HomeAssistantPlugin.backend import backend_const

from HomeAssistantPlugin.backend.home_assistant_backend import HomeAssistantBackend
from HomeAssistantPlugin.connection_settings.connection_settings import ConnectionSettings


class HomeAssistant(PluginBase):  # pylint: disable=too-few-public-methods
    """The plugin class to be loaded by Stream Controller. Manages the credentials."""

    def __init__(self):
        super().__init__()

        self.host_entry: Optional[EntryRow] = None
        self.port_entry: Optional[EntryRow] = None
        self.ssl_switch: Optional[SwitchRow] = None
        self.verify_certificate_switch: Optional[SwitchRow] = None
        self.token_entry: Optional[PasswordEntryRow] = None
        self.connection_status: Optional[EntryRow] = None

        self.perform_action_action_holder = ActionHolder(
            plugin_base=self,
            action_base=PerformAction,
            action_id="HomeAssistantPlugin::PerformAction",
            action_name=PERFORM_ACTION,
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED
            }
        )

        self.show_icon_action_holder = ActionHolder(
            plugin_base=self,
            action_base=ShowIcon,
            action_id="HomeAssistantPlugin::ShowIcon",
            action_name=SHOW_ICON,
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED
            }
        )

        self.show_text_action_holder = ActionHolder(
            plugin_base=self,
            action_base=ShowText,
            action_id="HomeAssistantPlugin::ShowText",
            action_name=SHOW_TEXT,
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED
            }
        )

        self.level_dial_action_holder = ActionHolder(
            plugin_base=self,
            action_base=LevelDial,
            action_id="HomeAssistantPlugin::LevelDial",
            action_name=LEVEL_DIAL,
            action_support={
                Input.Key: ActionInputSupport.UNSUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED
            }
        )

        self.add_action_holder(self.perform_action_action_holder)
        self.add_action_holder(self.show_icon_action_holder)
        self.add_action_holder(self.show_text_action_holder)
        self.add_action_holder(self.level_dial_action_holder)

        self.register(
            plugin_name=const.HOME_ASSISTANT,
            github_repo="https://github.com/gensyn/HomeAssistantPlugin",
            plugin_version="1.1.1",
            app_version="1.5.0-beta"
        )

        self.connection: ConnectionSettings = ConnectionSettings(self)
        host: str = self.connection.get_host()
        port: str = self.connection.get_port()
        ssl: bool = self.connection.get_ssl()
        verify_certificate: bool = self.connection.get_verify_certificate()
        token: str = self.connection.get_token()

        self.backend = HomeAssistantBackend(host, port, ssl, verify_certificate, token)

    def reload_settings(self):
        """Reconnects to Home Assistant with the new connection."""
        self.backend.set_host(self.connection.get_host())
        self.backend.set_port(self.connection.get_port())
        self.backend.set_ssl(self.connection.get_ssl())
        self.backend.set_verify_certificate(self.connection.get_verify_certificate())
        self.backend.set_token(self.connection.get_token())
        self.backend.connect()

    def get_settings_area(self):
        """Gets the rows for configuring Home Assistant credentials and base connection."""
        self.host_entry = EntryRow(title=self.locale_manager.get(const.LABEL_HOST))
        self.host_entry.set_text(self.connection.get_host())

        self.port_entry = EntryRow(title=self.locale_manager.get(const.LABEL_PORT))
        self.port_entry.set_text(self.connection.get_port())

        self.ssl_switch = SwitchRow(title=self.locale_manager.get(const.LABEL_SSL))
        self.ssl_switch.set_active(self.connection.get_ssl())

        self.verify_certificate_switch = SwitchRow(
            title=self.locale_manager.get(const.LABEL_VERIFY_CERTIFICATE))
        self.verify_certificate_switch.set_active(self.connection.get_verify_certificate())

        self.token_entry = PasswordEntryRow(title=self.locale_manager.get(const.LABEL_TOKEN))
        self.token_entry.set_text(self.connection.get_token())

        self.connection_status = EntryRow(title="Connection status:")
        self.connection_status.set_editable(False)
        self.connection_status.set_text(
            backend_const.CONNECTED if self.backend.is_connected() else backend_const.NOT_CONNECTED)

        self.backend.set_connection_status_callback(self.set_status)

        self.host_entry.connect(const.CONNECT_NOTIFY_TEXT, self._on_change_base_entry,
                                const.SETTING_HOST)
        self.port_entry.connect(const.CONNECT_NOTIFY_TEXT, self._on_change_base_entry,
                                const.SETTING_PORT)
        self.ssl_switch.connect(const.CONNECT_NOTIFY_ACTIVE, self._on_change_base_switch,
                                const.SETTING_SSL)
        self.verify_certificate_switch.connect(const.CONNECT_NOTIFY_ACTIVE,
                                               self._on_change_base_switch,
                                               const.SETTING_VERIFY_CERTIFICATE)
        self.token_entry.connect(const.CONNECT_NOTIFY_TEXT, self._on_change_base_entry,
                                 const.SETTING_TOKEN)

        group = PreferencesGroup()
        group.add(self.host_entry)
        group.add(self.port_entry)
        group.add(self.ssl_switch)
        group.add(self.verify_certificate_switch)
        group.add(self.token_entry)
        group.add(self.connection_status)

        return group

    def _on_change_base_entry(self, entry, *args) -> None:
        """Executed when an entry row is changed."""
        self.connection.set_setting(args[1], entry.get_text())

    def _on_change_base_switch(self, switch, *args) -> None:
        """Executed when a switch row is changed."""
        self.connection.set_setting(args[1], switch.get_active())

        if args[1] == const.SETTING_SSL and switch.get_active():
            self.verify_certificate_switch.set_sensitive(True)
            self.verify_certificate_switch.set_active(self.connection.get_verify_certificate())
        elif args[1] == const.SETTING_SSL:
            self.verify_certificate_switch.set_sensitive(False)
            self.verify_certificate_switch.set_active(False)

    def set_status(self, status) -> None:
        """Callback function to be executed when the Home Assistant connection status changes."""
        GLib.idle_add(self.connection_status.set_text, status)
