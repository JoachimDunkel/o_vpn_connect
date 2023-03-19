from pathlib import Path
import os
from enum import Enum


def _path_to_project_root(project_name):
    path = os.getcwd()
    while not str(path).endswith(project_name):
        path = Path(path).parent

    return path


APPLICATION_NAME = 'O-VPN-Connect'

PROJECT_ROOT_NAME = 'o_vpn_connect'
PATH_ROOT_DIR = Path(_path_to_project_root(PROJECT_ROOT_NAME))
PATH_CONFIG_DIR = PATH_ROOT_DIR / 'config'
PATH_SRC = PATH_ROOT_DIR / 'connect_vpn'
PATH_CREDENTIALS_FILE = PATH_CONFIG_DIR / 'configure_connection.yaml'
PATH_USER_SETTINGS_FILE = PATH_CONFIG_DIR / 'user_settings.yaml'

PATH_UI_DIR = PATH_SRC / 'ui'
PATH_SETTINGS_UI_GLADE = PATH_UI_DIR / 'settings_ui.glade'

PATH_HOME_DIR = Path(os.path.expanduser('~'))
PATH_BASH_ALIASES = PATH_HOME_DIR / '.bash_aliases'
PATH_CONNECT_VPN = PATH_ROOT_DIR / 'connect_vpn'
PATH_DATA_DIR = PATH_CONNECT_VPN / 'data'
PATH_IP2LOCATION_DB = PATH_DATA_DIR / 'IP2LOCATION-LITE-DB11.BIN'

PATH_IMAGES = PATH_CONNECT_VPN / 'images'
PATH_VPN_ICON_DISCONNECTED = PATH_IMAGES / 'key_white.png'
PATH_VPN_ICON_CONNECTED = PATH_IMAGES / 'key_green.png'
PATH_VPN_ICON_ESTABLISH_CONNECTION_1 = PATH_IMAGES / "key_white.png"
PATH_VPN_ICON_ESTABLISH_CONNECTION_2 = PATH_IMAGES / 'grey_green.png'

LAUNCH_DESKTOP_FILENAME = PROJECT_ROOT_NAME + '.desktop'
PATH_USER_LOCAL_SHARE = Path('/usr/local/share')
PATH_USER_LOCAL_SHARE_APPLICATION = PATH_USER_LOCAL_SHARE / 'applications'
PATH_LAUNCH_DESKTOP_FILE_DESTINATION = PATH_USER_LOCAL_SHARE_APPLICATION / LAUNCH_DESKTOP_FILENAME

LAUNCH_ICON_FILE_NAME = 'connect_vpn_logo.png'
PATH_USER_LOCAL_SHARE_ICONS = PATH_USER_LOCAL_SHARE / 'icons'
PATH_VPN_LAUNCH_ICON_SOURCE = PATH_IMAGES / LAUNCH_ICON_FILE_NAME
PATH_VPN_LAUNCH_ICON_DESTINATION = PATH_USER_LOCAL_SHARE_ICONS / LAUNCH_ICON_FILE_NAME

PATH_BIN_DIR = PATH_ROOT_DIR / 'bin'
RUN_CONNECT_VPN_SCRIPT = './connect_vpn'
RUN_ONE_TIME_SETUP_SCRIPT = './one_time_setup'


class ApplicationStatus(Enum):
    DISCONNECTED = 0
    CONNECTED = 1
    CONNECTED_BY_OTHER_PROCESS = 2


ESTABLISH_CONNECTION = 'Connect to VPN'
STOP_CONNECTION = 'Disconnect from VPN'

ESTABLISHED_CONNECTION_FORMAT = 'Established connection to: {}'
STOPPED_CONNECTION = 'Stopped vpn connection.'

OTHER_PROCESS_HOLDS_CONNECTION_FORMAT = "Your ip: {} \n You are already connected.\nExiting"

READING_CREDENTIALS_FAILED = "Can not read credentials. Make sure they are provided as expected in the " \
                             "configure_connection.yaml\nExiting"

OTHER_CONNECTION_FAILURE_FORMAT = "FAILURE - Unable to establish connection.\nException:\n{}"
SETTINGS_BTN_LABEL = "Settings"

DESKTOP_LAUNCH_FILE_FORMAT = """\n[Desktop Entry]\nTerminal=false\nStartupNotify=false\nType=Application\nName={}\nComment="Connect and monitor script based openvpn connection with an easy to use and intuitive gui"\nExec=bash -c 'cd {} && ./connect_vpn'\nIcon=connect_vpn_logo\n"""
