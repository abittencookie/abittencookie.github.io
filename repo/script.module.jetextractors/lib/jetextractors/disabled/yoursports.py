import requests, re, base64
from urllib.parse import urlparse

from ..models.Link import Link
from ..models.Extractor import Extractor

class Yoursports(Extractor):
    def __init__(self) -> None:
        self.domains = ["yoursports.stream"]
        self.name = "Yoursports"
        self.short_name = "YS"

    def get_regex_yoursports(self, text):
        if "rbnhd" in text:
            return r"var rbnhd = '(.+?)'"
        else:
            return r'var mustave.?=.?atob\((.+?)\)'

    def get_link(self, url):
        stream = requests.get(url, headers={"User-Agent": self.user_agent}).text
        try:
            link = re.compile(self.get_regex_yoursports(stream)).findall(stream)[0]
        except:
            iframe_src = re.compile('iframe.+?src="(.+?)" allowfullscreen="yes".+?>', re.DOTALL).findall(stream)[0]
            r_embed = requests.get(iframe_src, headers={"User-Agent": self.user_agent, "Referer": url}).text
            link = re.compile(self.get_regex_yoursports(r_embed)).findall(r_embed)[0]

        if not link.startswith("http") and not link.startswith("/"):
            link = base64.b64decode(link).decode("ascii").replace("'", "")
            if link.startswith('/'):
                try: link = "http://" + urlparse(iframe_src).netloc + link
                except: link = "http://%s" % self.domains[0] + link
        
        try: link = Link(address=link, headers={"Referer": iframe_src, "User-Agent": self.user_agent})
        except: link = Link(address=link, headers={"Referer": self.domains[0], "User-Agent": self.user_agent})

        return link