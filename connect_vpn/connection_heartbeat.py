import threading
import time
from gi.repository import GLib


class ConnectionHeartbeat:

    def __init__(self, ip_info, expected_vpn_ip, on_connection_lost, check_interval=15):
        self.ip_info = ip_info
        self.expected_vpn_ip = expected_vpn_ip
        self.on_connection_lost = on_connection_lost
        self.check_interval = check_interval
        self.monitoring = False
        self._monitor_thread = None

    def start_monitoring(self):
        if self._monitor_thread is not None and self._monitor_thread.is_alive():
            return  # Already monitoring

        self.monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_task)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=1.0)
            self._monitor_thread = None

    def _is_connection_still_intact(self):
        try:
            print("Doing heart-beat")
            self.ip_info.update()
            current_ip = self.ip_info.ip_address

            if current_ip != self.expected_vpn_ip and self.expected_vpn_ip:
                return False
            return True
        except Exception as e:
            print(f"Error in connection heartbeat: {str(e)}")
            return False

    def _monitor_task(self):
        while self.monitoring:
            still_running = self._is_connection_still_intact()
            if not still_running:
                GLib.idle_add(self.on_connection_lost)

            time.sleep(self.check_interval)
