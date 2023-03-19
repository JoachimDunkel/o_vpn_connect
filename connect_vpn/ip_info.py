from .common import resources
from .check_ip import get_public_ip
import IP2Location
class IPInformation:
    def __init__(self):
        self.city = ""
        self.region = ""
        self.ip_address = ""
        self.country_code = ""

        self._ip2_loc_db = IP2Location.IP2Location()
        self._ip2_loc_db.open(str(resources.PATH_IP2LOCATION_DB))
        self.update()

    def update(self):
        self.ip_address = get_public_ip()
        ip_record = self._ip2_loc_db.get_all(self.ip_address)
        self.country_code = ip_record.country_short
        self.region = ip_record.region
        self.city = ip_record.city

    def get_ip_details(self):
        return "{}, {}, {}".format(self.country_code, self.region, self.city)

    def get_ip_address(self):
        return "IP: {}".format(self.ip_address)