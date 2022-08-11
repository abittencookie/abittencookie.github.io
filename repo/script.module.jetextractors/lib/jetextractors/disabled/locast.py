import requests

from ..models.Link import Link
from ..models.Extractor import Extractor
from ..util.keys import Keys

class Locast(Extractor):
    def __init__(self) -> None:
        self.domains = ["api.locastnet.org"]

    def get_links(self, url):
        key = Keys.get_key(Keys.locast)
        r = requests.get(url, headers={"Authorization": "Bearer " + key, "User-Agent": self.user_agent}).json()
        return Link(address=r["streamUrl"])