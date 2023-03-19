import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk
from connect_vpn.common.user_settings import UserSettings
from connect_vpn.common import resources


class SettingsWindow:
    def __init__(self, app_indicator, on_settings_closed):
        self.app_indicator = app_indicator
        self.on_settings_closed = on_settings_closed
        self.user_settings = UserSettings()
        self.handlers = {
            "on_apply_btn_clicked": self.on_apply,
            "on_ok_btn_clicked": self.on_ok,
            "auto_connect_on_launch_toggled": self.on_auto_connect_toggled,
            "on_supress_notifications_toggled": self.on_suppress_notifications_toggled
        }
        self.showing_window = False

    def on_ok(self, btn):
        self.user_settings.saver_user_changes()
        self.window.close()
        self.showing_window = False

    def on_apply(self, btn):
        self.user_settings.saver_user_changes()

    def on_auto_connect_toggled(self, check_btn):
        self.user_settings.auto_connect_when_launched = check_btn.get_active()

    def on_suppress_notifications_toggled(self, check_btn):
        self.user_settings.suppress_notifications = check_btn.get_active()

    def on_window_closed(self, caller, event):
        self.showing_window = False
        self.on_settings_closed()
        return False  # Always close

    def show(self):
        if self.showing_window:
            return

        builder = Gtk.Builder()
        builder.add_from_file(str(resources.PATH_SETTINGS_UI_GLADE))
        builder.connect_signals(self.handlers)

        auto_connect_on_launch_check_box = builder.get_object('auto_connect_when_launched_check_box')
        auto_connect_on_launch_check_box.set_active(self.user_settings.auto_connect_when_launched)

        suppress_notifications_check_box = builder.get_object('suppress_notifications_checkbox')
        suppress_notifications_check_box.set_active(self.user_settings.suppress_notifications)

        self.window = builder.get_object("settings_window")
        self.window.set_title(resources.APPLICATION_NAME)
        self.window.connect('delete-event', self.on_window_closed)

        self.window.show()
        return self.window


if __name__ == "__main__":

    def on_settings_window_closed():
        print("Settings window closed")
        Gtk.main_quit()

    settings_window = SettingsWindow(None, on_settings_window_closed)
    settings_window.show()
    Gtk.main()
