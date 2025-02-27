import signal
import threading

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3
from gi.repository import Notify as notify
from gi.repository import GLib
from connect_vpn.ui.settings_ui import SettingsWindow
from connect_vpn.common import resources
from connect_vpn.common.resources import ApplicationStatus
from connect_vpn.establish_connection import ConnectorBackend
from connect_vpn.configuration_handler import read_credentials
from connect_vpn.ip_info import IPInformationQuery, IPInfoData, fallback_ip_info_data
from connect_vpn.icon_status_handler import IconStatusHandler
from connect_vpn.connection_heartbeat import ConnectionHeartbeat


class VPNConnectorApp:
    def __init__(self, on_disconnect_vpn, on_connect_vpn):
        self.on_disconnect_vpn = on_disconnect_vpn
        self.on_connect_vpn = on_connect_vpn
        self.application_status = ApplicationStatus.DISCONNECTED
        self.ip_info = IPInformationQuery()

        self.APPINDICATOR_ID = 'connect_vpn_indicator'
        self.app = AppIndicator3.Indicator.new(self.APPINDICATOR_ID, str(resources.PATH_VPN_ICON_DISCONNECTED),
                                               AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
        self.app.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.app.set_menu(self.build_app())
        self.settings_window = SettingsWindow(self.app, self.unlock)
        self.icon_status_handler = IconStatusHandler(self.app)
        self.change_ui_availability_state_lock = threading.Lock()
        # Initialize with empty VPN IP - will be set when connection backend is configured
        self.heartbeat = None
        self.vpn_ip = None
        notify.init(self.APPINDICATOR_ID)

    def configure_heartbeat(self, vpn_ip):

        self.vpn_ip = vpn_ip
        self.heartbeat = ConnectionHeartbeat(
            self.ip_info,
            self.vpn_ip,
            self.on_connection_lost,
            check_interval=resources.CONNECTION_HEARTBEAT_INTERVAL_SEC
        )

    def on_connection_lost(self):
        if self.application_status != ApplicationStatus.DISCONNECTED:
            print("Connection lost detected by heartbeat")
            self.notify_user("VPN connection lost")
            self.stop_heartbeat()
            self.on_disconnected(False)

    def start_heartbeat(self):
        if self.heartbeat and self.vpn_ip:
            self.heartbeat.start_monitoring()

    def stop_heartbeat(self):
        if self.heartbeat:
            self.heartbeat.stop_monitoring()

    def request_connection(self):
        self.lock()
        self.notify_user("Connecting ... ")
        self.icon_status_handler.on_establishing_connection()
        self.on_connect_vpn(self.ip_info.ip_address)

    def on_connected(self):
        self.unlock()
        self.update_ip_information()
        self.notify_user(resources.ESTABLISHED_CONNECTION_FORMAT.format(self.ip_info.ip_address))
        self.perform_connection_change_btn_item.set_label(resources.STOP_CONNECTION)
        self.application_status = ApplicationStatus.CONNECTED
        self.change_connect_status_info()
        self.icon_status_handler.on_connected()
        # Start the heartbeat to monitor the connection
        self.start_heartbeat()

    def on_disconnected(self, notify_user=True):
        try:
            self.unlock()
            self.update_ip_information()
        except Exception as e:
            print(e)

        if notify_user:
            self.notify_user(resources.STOPPED_CONNECTION)
        self.perform_connection_change_btn_item.set_label(resources.ESTABLISH_CONNECTION)
        self.application_status = ApplicationStatus.DISCONNECTED
        self.change_connect_status_info()
        self.icon_status_handler.on_disconnected()
        # Stop the heartbeat when disconnected
        self.stop_heartbeat()

    def on_other_process_holds_connection(self, ip):
        msg = resources.OTHER_PROCESS_HOLDS_CONNECTION_FORMAT.format(ip)
        self.notify_user(msg)
        print("Other process holds connection. Exiting")
        exit(-1)

    def on_other_connection_failure(self, failure_reason: str):
        self.notify_user(resources.OTHER_CONNECTION_FAILURE_MSG, failure_reason)
        print(resources.OTHER_CONNECTION_FAILURE_MSG + " " + failure_reason)

    @staticmethod
    def on_read_credentials_failed():
        print(resources.READING_CREDENTIALS_FAILED)
        exit(-1)

    def notify_user(self, msg, additional_info=None):
        if not self.settings_window.user_settings.suppress_notifications:
            if additional_info:
                notify.Notification.new(msg, additional_info).show()
            else:
                notify.Notification.new(msg, None).show()

    def request_disconnection(self):
        self.stop_heartbeat()  # Stop heartbeat before disconnecting
        self.on_disconnect_vpn()

    def change_connect_status_info(self):
        self.connection_status_label = self.application_status.name
        self.connection_status_menu_item.set_label(self.connection_status_label)

    def toggle_vpn_connection(self, btn):
        if self.application_status == ApplicationStatus.DISCONNECTED:
            self.request_connection()
        elif self.application_status == ApplicationStatus.CONNECTED:
            self.request_disconnection()
        else:
            print("Other process holds connection. Aborting program")
            exit(-1)

    def _set_ip_ui_info(self, info_data: IPInfoData):
        self.ip_addr_item.set_label(info_data.get_ip_address())
        self.ip_details_item.set_label(info_data.get_ip_details())

    def update_ip_information(self):
        self.ip_info.update()
        self._set_ip_ui_info(self.ip_info.data)

    def open_settings(self, btn):
        self.lock()
        self.settings_window.show()

    def quit_application(self, btn):
        self.request_disconnection()
        gtk.main_quit()

    def lock(self):
        GLib.idle_add(self._change_ui_availability, False)

    def _change_ui_availability(self, is_available):
        self.change_ui_availability_state_lock.acquire()
        self.perform_connection_change_btn_item.set_sensitive(is_available)
        self.open_settings_menu_item.set_sensitive(is_available)
        self.change_ui_availability_state_lock.release()

    def unlock(self):
        GLib.idle_add(self._change_ui_availability, True)

    def build_app(self):
        # No changes to this method needed
        # Left intact for completeness
        self.menu = gtk.Menu()
        self.ip_addr_item = gtk.MenuItem(label=self.ip_info.get_ip_address(), sensitive=False)
        self.ip_details_item = gtk.MenuItem(label=self.ip_info.get_ip_details(), sensitive=False)

        self.connection_status_label = ApplicationStatus.DISCONNECTED.name
        self.connection_status_menu_item = gtk.MenuItem(label=self.connection_status_label, sensitive=False)
        self.perform_connection_change_btn_item = gtk.MenuItem(label=resources.ESTABLISH_CONNECTION)
        self.perform_connection_change_btn_item.connect("activate", self.toggle_vpn_connection)

        self.open_settings_menu_item = gtk.MenuItem(label=resources.SETTINGS_BTN_LABEL)
        self.open_settings_menu_item.connect('activate', self.open_settings)

        self.quit_app_menu_item = gtk.MenuItem(label="Quit")
        self.quit_app_menu_item.connect('activate', self.quit_application)

        self.menu.append(self.ip_addr_item)
        self.menu.append(self.ip_details_item)
        self.menu.append(self.connection_status_menu_item)
        self.menu.append(gtk.SeparatorMenuItem())
        self.menu.append(self.perform_connection_change_btn_item)
        self.menu.append(gtk.SeparatorMenuItem())
        self.menu.append(self.open_settings_menu_item)
        self.menu.append(gtk.SeparatorMenuItem())
        self.menu.append(self.quit_app_menu_item)
        self.menu.show_all()
        return self.menu

    def initialize(self):
        self.notify_user("Started {}".format(resources.APPLICATION_NAME))
        if self.settings_window.user_settings.auto_connect_when_launched:
            GLib.idle_add(self.request_connection)
