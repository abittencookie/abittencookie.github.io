import requests, re, random, string, base64, os, time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from ..models.Extractor import Extractor
from urllib.parse import urlparse

from ..models.Game import Game
from ..models.Link import Link

class JokerHDPass(Extractor):
    def __init__(self) -> None:
        self.domains = ["vip.jokerhdpass.com"]
        self.name = "JokerHDPass"
        self.short_name = "JHDP"
        self.base_url = "https://" + self.domains[0]

    def form_data(self, boundary, params):
        output = ""
        for key, value in params.items():
            output += "--%s\r\n" % boundary
            output += 'Content-Disposition: form-data; name="%s"\r\n\r\n' % key
            output += f"{value}\r\n"
        output += "--%s--\r\n" % boundary
        return output

    def get_link(self, url):
        url_split = url.split("|")
        href = url_split[0]
        cookie_split = url_split[1].split("&")
        user_id = cookie_split[0]
        phpsessid = cookie_split[1]

        r = requests.get(href, headers={"Cookie": "amember_nr=%s; PHPSESSID=%s" % (user_id, phpsessid), "User-Agent": self.user_agent}).text
        if 'http-equiv="refresh"' in r:
            refresh_url = re.compile(r'url=(.+?)"').findall(r)[0]
            r = requests.get(refresh_url, headers={"Cookie": "amember_nr=%s; PHPSESSID=%s" % (user_id, phpsessid), "User-Agent": self.user_agent}).text
        re_iframe = re.compile(r'<iframe.+?src="(.+?)" name="MainPlayer"').findall(r)[0]
        r_iframe = requests.get(re_iframe, headers={"User-Agent": self.user_agent, "Referer": self.base_url}).text
        if "source: " in r_iframe:
            re_m3u8 = re.compile(r"source: '(.+?)',").findall(r_iframe)[0]
        elif "iframe src=" in r_iframe:
            re_embed = re.compile(r'iframe src="(.+?)" ').findall(r_iframe)[0]
            r_embed = requests.get(re_embed, headers={"Referer": re_iframe}).text
            re_m3u8 = re.compile(r'source: "(.+?)",').findall(r_embed)[0]
            if re_m3u8.startswith("/"):
                re_m3u8 = "https://" + urlparse(re_embed).hostname + re_m3u8
        
        return Link(address=re_m3u8)

    def get_games(self):
        games = []

        r_login = requests.get(self.base_url + "/dashboard/login")
        phpsessid = r_login.cookies.get_dict()["PHPSESSID"]
        re_login_attempt_id = re.compile(r'<input type="hidden" name="login_attempt_id" value="(.+?)"').findall(r_login.text)[0]
        boundary = "--WebKitFormBoundary" +  ("".join(random.choice(string.ascii_letters + string.digits) for _ in range(15)))
        params = dict(amember_login="Adammonster", amember_pass=base64.b64decode("jkTYp5WYk5WYtlmb1pWQ"[::-1]).decode("utf-8"), login_attempt_id=re_login_attempt_id, amember_redirect_url="http://vip.jokerhdpass.com/home/")
        payload = self.form_data(boundary, params)
        r = requests.post(self.base_url + "/dashboard/login", data=payload, headers={"User-Agent": self.user_agent, "Accept": "application/json", "Content-Type": "multipart/form-data; boundary=" + boundary, "Cookie": "PHPSESSID=" + phpsessid})
        if '"ok":true' not in r.text:
            return games
        user_id = r.cookies.get_dict()["amember_nr"]

        # Get games
        r_schedule = requests.get(self.base_url + "/schedule/", headers={"Cookie": "amember_nr=" + user_id, "User-Agent": self.user_agent, "PHPSESSID": phpsessid}).text
        soup_schedule = BeautifulSoup(r_schedule, "html.parser")
        for date_header in soup_schedule.find_all("h1"):
            header_day = datetime(*(time.strptime(date_header.text, "%A %d %B")[:6]))
            
            table = date_header.next_sibling.find("table")
            for game in table.find_all("tr", {"class": "row-style"}):
                game_time = datetime(*(time.strptime(game.find("center", {"class": "event"}).text, "%H:%M")[:6]))
                game_time = header_day.replace(hour=game_time.hour, minute=game_time.minute, year=datetime.now().year) - timedelta(hours=1)
                game_icon = game.find_all("img", {"class": "teamlogo"})[-1].get("src")
                game_league = os.path.basename(game_icon)[:os.path.basename(game_icon).index(".")].capitalize()
                game_title = game.find("td", {"class": "team"}).text
                game_title = game_title[:game_title.index("Live on:")].replace("  -\n                    ", "").strip()
                game_hrefs = game.find_all("a")
                hrefs = []
                for href in game_hrefs:
                    hrefs.append(Link(self.base_url + href.get("href")  + "|%s&%s" % (user_id, phpsessid)))
                games.append(Game(title=game_title, links=hrefs, icon=game_icon, league=game_league, starttime=game_time))
        
        return games