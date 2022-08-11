import requests
from datetime import datetime, timedelta

from ..models.Extractor import Extractor

class YahooHighlightsNHL(Extractor):
    def __init__(self) -> None:
        self.name = "Yahoo Sports - NHL Highlights"
        self.short_name = "YAHOO_HL"

    def _get_games(self, date):
        games = []
        for league in ["NHL"]:
            try:
                r_scores = requests.get("https://api-secure.sports.yahoo.com/v1/editorial/s/scoreboard", params={"leagues": league.lower(), "date": date.strftime("%Y-%m-%d")}).json()
                scoreboard = r_scores["service"]["scoreboard"]
                for _, highlight in scoreboard["gamehighlight"].items():
                    games.append(Game(title=highlight["title"], icon=highlight["thumbnail"]["url"], league=league, starttime=date.replace(hour=12, minute=0), links=[Link(address="https://video.media.yql.yahoo.com/v1/video/sapi/hlsstreams/%s.m3u8?site=sports&region=US&lang=en-US&devtype=desktop&src=sapi" % highlight["uuid"])]))
            except: continue
        return games

    def get_games(self):
        games = self._get_games(datetime.now()) + self._get_games(datetime.now() - timedelta(days=1))
        return games
