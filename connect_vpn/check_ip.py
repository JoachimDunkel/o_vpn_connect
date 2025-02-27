import re as r
from requests import get
import time
import random

INDIVIDUAL_TIMEOUT_SEC = 2

def _query_checkip_dyndns():
    url = 'http://checkip.dyndns.com/'
    body = get(url, verify=False, timeout=INDIVIDUAL_TIMEOUT_SEC).content.decode('utf8')
    return r.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(body).group(1)


def _query_amazon_aws():
    return get('https://checkip.amazonaws.com', timeout=INDIVIDUAL_TIMEOUT_SEC).text.strip()


def _query_api_ipify():
    url = 'https://api.ipify.org'
    return get(url, timeout=INDIVIDUAL_TIMEOUT_SEC).content.decode('utf8')


def get_public_ip():
    api_endpoints = [_query_amazon_aws, _query_checkip_dyndns, _query_api_ipify]
    for query_endpoint in api_endpoints:
        try:
            ip = query_endpoint()
            return ip
        except Exception as _:
            print("Failed getting Public IP")
            pass  # Ignore


if __name__ == "__main__":
    print(get_public_ip())
