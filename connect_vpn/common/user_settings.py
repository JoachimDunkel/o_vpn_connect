import os
import yaml
from .resources import PATH_USER_SETTINGS_FILE
from connect_vpn.configuration_handler import ensure_configuration_exists, create_configuration_anew, ensure_configuration_up_to_date


class UserSettings:
    def __init__(self):
        self.user_settings_path = str(PATH_USER_SETTINGS_FILE)
        self.auto_connect_when_launched = False
        self.suppress_notifications = False
        self._settings = {
            'auto_connect_when_launched': False,
            'suppress_notifications': False
        }
        self.restore_last_user_settings()

    def restore_last_user_settings(self):
        ensure_configuration_up_to_date(self.user_settings_path, self._settings)

        with open(self.user_settings_path, 'r') as stream:
            settings = yaml.safe_load(stream)
            self._settings = settings

        self.auto_connect_when_launched = self._settings['auto_connect_when_launched']
        self.suppress_notifications = self._settings['suppress_notifications']

    def saver_user_changes(self):
        self._settings['auto_connect_when_launched'] = self.auto_connect_when_launched
        self._settings['suppress_notifications'] = self.suppress_notifications

        with open(self.user_settings_path, 'w') as file:
            yaml.dump(self._settings, file)
