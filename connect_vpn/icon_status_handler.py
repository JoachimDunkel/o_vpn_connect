from gi.repository import AppIndicator3, GLib
from .common import resources

import threading
import time
from enum import IntEnum


class IconStatus(IntEnum):
    DISCONNECTED = 0
    ESTABLISH_CONNECTION_1 = 1
    ESTABLISH_CONNECTION_2 = 2
    CONNECTED = 3


class IconStatusHandler:

    def __init__(self, app: AppIndicator3.Indicator):
        self.app = app
        self.icon_status = IconStatus.DISCONNECTED
        self.blink_icon = False

        self.blink_period = 1

    def on_connected(self):
        self.blink_icon = False
        self.update_icon_status(IconStatus.CONNECTED)
        self.update_icon()

    def on_disconnected(self):
        self.update_icon_status(IconStatus.DISCONNECTED)
        self.update_icon()

    def update_icon_status(self, status: IconStatus):
        self.icon_status = status
        self.icon_img = self.get_icon_img()

    def update_icon(self):
        self.app.set_icon(self.icon_img)
        return self.blink_icon

    def get_icon_img(self):
        return {
            self.icon_status.DISCONNECTED: str(resources.PATH_VPN_ICON_DISCONNECTED),
            self.icon_status.CONNECTED: str(resources.PATH_VPN_ICON_CONNECTED),
            self.icon_status.ESTABLISH_CONNECTION_1: str(resources.PATH_VPN_ICON_ESTABLISH_CONNECTION_1),
            self.icon_status.ESTABLISH_CONNECTION_2: str(resources.PATH_VPN_ICON_ESTABLISH_CONNECTION_2)
        }[self.icon_status]

    def get_next_icon_status(self):
        return {
            self.icon_status.DISCONNECTED: IconStatus.ESTABLISH_CONNECTION_1,
            self.icon_status.CONNECTED: IconStatus.CONNECTED,
            self.icon_status.ESTABLISH_CONNECTION_1: IconStatus.ESTABLISH_CONNECTION_2,
            self.icon_status.ESTABLISH_CONNECTION_2: IconStatus.ESTABLISH_CONNECTION_1,
        }[self.icon_status]

    def blink_icon_task(self):
        while self.blink_icon:
            next_icon_status = self.get_next_icon_status()
            self.update_icon_status(next_icon_status)
            time.sleep(self.blink_period)
            GLib.idle_add(self.update_icon)

    def on_establishing_connection(self):
        self.blink_icon = True
        thread = threading.Thread(target=self.blink_icon_task)
        thread.setDaemon(True)
        thread.start()

