from .common import resources as res
import os
import yaml
from .common.util import ensure_file_exists

CONFIGURATION_FORMAT = {
    'SUDO_PW': '',
    'USER_NAME': '',
    'USER_PW': '',
    'VPN_PUB_IP': '',
    'OPENVPN_SCRIPT_PATH': ''
}


def ensure_configuration_exists(config_path, config_format):
    created_anew = ensure_file_exists(config_path, default_content=config_format, create_anew=create_configuration_anew)
    return created_anew


def ensure_configuration_up_to_date(config_path, config_format):
    created_anew = ensure_configuration_exists(config_path, config_format)
    if created_anew:
        return

    with open(config_path, 'r') as stream:
        config = yaml.safe_load(stream)
        if set(config_format.keys()) != set(config.keys()):
            create_configuration_anew(config_path, config_format)


def create_configuration_anew(config_path, config_format):
    with open(config_path, 'w') as file:
        yaml.dump(config_format, file)


def _ensure_config_value_provided(source_param, error_list: list, failure_msg):
    if source_param == '':
        error_list.append(failure_msg)
    return source_param

SPACING_LINE = "======================================================================="
WARNING = "(WARNING - There is currently no way of knowing if they are actually correct\n so the program will just not work without telling you why.)"
ERROR_IPV4_MISSING = "VPN_PUB_IP:            Provide the expected ipv4 address of your desired vpn."
ERROR_OPENVPN_SCRIPT_PATH_MISSING = "OPENVPN_SCRIPT_PATH:   Provide a correct path to your openvpn-script."
ERROR_SUDP_PW_MISSING = "SUDO_PW:               Provide a correct sudo-pw."
ERROR_USER_NAME_MISSING = "USER_NAME:             Please provide the correct username to your openvpn login."
ERROR_OPENVPN_PW_MISSING = "USER_PW:               Please provide the correct password to your openvpn login."
PROVIDE_USER_WITH_ERRORS_MSG_FORMAT = SPACING_LINE + "\nAll parameters in \n{}\nneed correct values. " + WARNING + " \n" + SPACING_LINE + "\n{}"


def read_credentials(connection_backend):
    created_anew = ensure_configuration_exists(str(res.PATH_CREDENTIALS_FILE), CONFIGURATION_FORMAT)
    if created_anew:
        print("Configuration created anew.\nPlease fill out all the necessary credentials for your openvpn-login in:\n{}\n".format(
            res.PATH_CREDENTIALS_FILE))
        exit(-1)

    with open(str(res.PATH_CREDENTIALS_FILE), 'r') as stream:
        try:
            credentials = yaml.safe_load(stream)

            errors = []

            connection_backend.config.VPN_PUB_IP = _ensure_config_value_provided(credentials['VPN_PUB_IP'], errors,
                                                                                 ERROR_IPV4_MISSING)
            connection_backend.config.OPENVPN_SCRIPT_PATH = _ensure_config_value_provided(
                credentials['OPENVPN_SCRIPT_PATH'], errors, ERROR_OPENVPN_SCRIPT_PATH_MISSING)
            connection_backend.config.SUDO_PW = _ensure_config_value_provided(credentials['SUDO_PW'], errors,
                                                                              ERROR_SUDP_PW_MISSING)
            connection_backend.config.USER_NAME = _ensure_config_value_provided(credentials['USER_NAME'], errors,
                                                                                ERROR_USER_NAME_MISSING)
            connection_backend.config.USER_PW = _ensure_config_value_provided(credentials['USER_PW'], errors,
                                                                              ERROR_OPENVPN_PW_MISSING)

            if len(errors) > 0:
                failure_reason = "\n".join(errors)
                msg = PROVIDE_USER_WITH_ERRORS_MSG_FORMAT.format(res.PATH_CREDENTIALS_FILE, failure_reason)
                print(msg)
                exit(-1)

        except yaml.YAMLError as e:
            connection_backend.on_read_credentials_failed()
