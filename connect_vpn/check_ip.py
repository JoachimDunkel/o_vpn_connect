import re as r
from requests import get
import concurrent.futures

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

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(api_endpoints)) as executor:
        future_to_endpoint = {executor.submit(endpoint): endpoint for endpoint in api_endpoints}
        for future in concurrent.futures.as_completed(future_to_endpoint):
            try:
                ip = future.result()
                return ip  # Return the first successful result
            except Exception:
                pass  # Try the next one
    return None


if __name__ == "__main__":
    print(get_public_ip())
