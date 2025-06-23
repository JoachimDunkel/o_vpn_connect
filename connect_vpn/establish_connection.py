import ctypes
import ctypes.util
import getpass
import signal
import sys
from typing import Optional
import pexpect

from connect_vpn.child_terminator import ChildTerminator
from .common.tasks import CallbackTask
from gi.repository import GLib

PR_SET_PDEATHSIG = 1


def _set_pdeathsig():
    libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
    if libc.prctl(PR_SET_PDEATHSIG, signal.SIGKILL) != 0:
        raise OSError(ctypes.get_errno(), 'SET_PDEATHSIG')


class ConnectionConfiguration:
    def __init__(self):
        self.USER_PW: str = ""
        self.USER_NAME: str = ""
        self.SUDO_PW: str = ""
        self.OPENVPN_SCRIPT_PATH: str = ""
        self.VPN_PUB_IP = ""


class ConnectorBackend:
    def __init__(self, debug=False):
        self.config = ConnectionConfiguration()
        self.child_process: Optional[pexpect.spawn] = None
        self.debug = debug

    def setup(self, on_read_credentials_failed, on_already_connected_by_other_process,
              on_connection_failed, on_connection_established, on_connection_stopped):

        self.on_read_credentials_failed = on_read_credentials_failed
        self.on_already_connected_by_other_process = on_already_connected_by_other_process
        self.on_connection_failed = on_connection_failed
        self.on_connection_established = on_connection_established
        self.on_connection_stopped = on_connection_stopped

    def stop_connection(self):
        self.ensure_child_stopped()
        self.on_connection_stopped(False)

    def handle_connection_failed(self, exception):
        self.ensure_child_stopped()
        self.on_connection_failed(exception)

    def ensure_child_stopped(self):
        # def ensure_child_stopped(self):
        if self.child_process is None:
            return


        terminator = ChildTerminator(self.child_process)
        terminator.terminate()
        self.child_process = None


    def _connect_task(self, args):
        if self.child_process is None:
            raise RuntimeError("ovpn-cli child process is not initialized")
            
        self.child_process.expect_exact('[sudo] password for {}: '.format(getpass.getuser()))
        self.child_process.sendline(self.config.SUDO_PW)
        self.child_process.expect_exact('Enter Auth Username: ')
        self.child_process.sendline(self.config.USER_NAME)
        self.child_process.expect_exact('Enter Auth Password: ')
        self.child_process.sendline(self.config.USER_PW)
        self.child_process.expect_exact('Initialization Sequence Completed')

    def establish_connection(self, curr_ip):
        establishing_is_possible = self.check_connection_status(curr_ip)
        if not establishing_is_possible:
            self.stop_connection()
            return
        # For some reason the vpn connection does not work if pexpect spawns the child process inside a thread
        # (that's why it is not inside _connect_task) ??
        self.child_process = pexpect.spawn(self.config.OPENVPN_SCRIPT_PATH, preexec_fn=_set_pdeathsig)
        if self.debug:
            self.child_process.logfile = sys.stdout.buffer

        self.connect_task = CallbackTask(self._connect_task, [], on_succeeded=self.on_connection_established,
                                         on_failed=self.handle_connection_failed)
        self.connect_task.start()

    def check_connection_status(self, curr_ip) -> bool:
        if curr_ip is None:
            self.on_connection_failed("Could not determine IP-Address. Check Network")
            return False
        elif curr_ip == self.config.VPN_PUB_IP:
            self.on_already_connected_by_other_process(curr_ip)
            return False

        return True