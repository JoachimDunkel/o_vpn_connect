import signal

from connect_vpn.establish_connection import ConnectorBackend
from connect_vpn.configuration_handler import read_credentials
from connect_vpn.vpn_connector_app import VPNConnectorApp, gtk


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    connection_backend = ConnectorBackend(debug=True)
    read_credentials(connection_backend)
    app = VPNConnectorApp(on_disconnect_vpn=connection_backend.stop_connection,
                          on_connect_vpn=connection_backend.establish_connection)

    # Configure heartbeat with the expected VPN IP
    app.configure_heartbeat(connection_backend.config.VPN_PUB_IP)

    connection_backend.setup(app.on_read_credentials_failed, app.on_other_process_holds_connection,
                             app.on_other_connection_failure, app.on_connected, app.on_disconnected)
    connection_backend.check_connection_status(app.ip_info.ip_address)

    app.initialize()
    gtk.main()

if __name__ == "__main__":
    main()