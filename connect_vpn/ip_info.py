from abc import ABC
from dataclasses import dataclass

import IP2Location

from .check_ip import get_public_ip
from .common import resources


@dataclass
class IPInfoData:
    city: str = ""
    region: str = ""
    ip_address: str = ""
    country_code: str = ""

    def get_ip_details(self):
        return "{}, {}, {}".format(self.country_code, self.region, self.city)

    def get_ip_address(self):
        return "IP: {}".format(self.ip_address)


fallback_ip_info_data = IPInfoData(city="?", region="`?", ip_address="?", country_code="?")


class IPInformationQuery:
    def __init__(self):
        self.data = IPInfoData()

        self._ip2_loc_db = IP2Location.IP2Location()
        self._ip2_loc_db.open(str(resources.PATH_IP2LOCATION_DB))
        self.update()

    def update(self):
        self.ip_address = get_public_ip()
        try:
            ip_record = self._ip2_loc_db.get_all(self.ip_address)
            self.data.country_code = ip_record.country_short
            self.data.region = ip_record.region
            self.data.city = ip_record.city
        except Exception as _:
            self.data = fallback_ip_info_data

    def get_ip_details(self):
        return self.data.get_ip_details()

    def get_ip_address(self):
        return self.data.get_ip_address()
