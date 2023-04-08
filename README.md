# o_vpn_connect

Connecting with open-vpn under Ubuntu is usually done via terminal.
This forces you to keep a terminal open for the connection.

There are existing GUI solutions that monitor an open-vpn connections, 
but these usually do not work if connecting to the network is done via a bash script that has to do additional stuff, like reading the company certificate. 

This solution is especially tailored to this use case. 
It uses pexpect to handle the openvpn-connection and therefore works with any openvpn based connection process.

## Setup

Install apt dependencies:
```shell
sudo apt install libgirepository1.0-dev
```
```shell
sudo apt-get install python3-cairo-dev
```
```shell
sudo apt-get install gir1.2-appindicator3-0.1
```

Clone the repository.

Change to the project directory and run:
```shell
pip install -r requirements.txt
```

Run the setup script:
```shell
sudo ./bin/one_time_setup
```

When first starting the application it will create a `configure_connection.yaml` in the directory root.
No connection will be established until not all of it's parameters are properly supplied.
 (It should look as follows.)

```yaml

# Change this to your credentials (take a look at the source code if you are suspicious at that point. which is understandable)

SUDO_PW: ""
USER_NAME: ""
USER_PW: ""

# The public ipv4 address visible from the outside after connecting with the vpn.
# This is there to check if a connection was established. Or if you are already connected to the vpn via another ürpces.

VPN_PUB_IP: ""

# Path to the script that will run openvpn internally

OPENVPN_SCRIPT_PATH: ""

```

## Check out your setup

Run the application from terminal which will provide you with additional information if everything was setup correctly.
```shell
./bin/connect_vpn
```

## Running this project

After the setup a launch menu entry named: `O-VPN-Connect` is added and can just be clicked / or run it from the terminal like above.

After startup an application indicator will appear next to the wifi symbol (in ubuntu atleast).
You will figure it out from there? right ?


## Improvements

May the reader be encouraged to improve the below described issue and any other he/she may encounter.

### Security issue

At the moment login credentials reside in a plain text file. This is a security issue, obviously. 

! Use this project and any of it's content fully at your own risk !.

## Attribution

This site or product includes IP2Location LITE data available from <a href="https://lite.ip2location.com">https://lite.ip2location.com</a>.

