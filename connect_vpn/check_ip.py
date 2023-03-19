import re as r
from requests import get
import time
import random

REQUEST_TIMEOUT_SEC = 10


def _query_checkip_dyndns():
    url = 'http://checkip.dyndns.com/'
    body = get(url, verify=False).content.decode('utf8')
    return r.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(body).group(1)


def _query_amazon_aws():
    return get('https://checkip.amazonaws.com').text.strip()


def _query_api_ipify():
    url = 'https://api.ipify.org'
    return get(url).content.decode('utf8')


def get_public_ip():
    api_endpoints = [_query_amazon_aws, _query_checkip_dyndns, _query_api_ipify]

    random_endpoint_idx = random.randint(0, len(api_endpoints) - 1)
    timeout = time.time() + REQUEST_TIMEOUT_SEC  # 10 seconds from now.

    tries = 0

    while time.time() < timeout:
        query_endpoint = api_endpoints[random_endpoint_idx]
        try:
            ip = query_endpoint()
            return ip
        except Exception as _:
            tries += 1  # Try until it works.

    raise ValueError("Connection Timeout-while retrieving ip-address after {} tries.".format(str(tries)))


if __name__ == "__main__":
    print(get_public_ip())
