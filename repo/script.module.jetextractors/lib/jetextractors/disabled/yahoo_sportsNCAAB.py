import requests, time
from datetime import datetime

from ..models.Extractor import Extractor
from ..models.Game import Game
from ..models.Link import Link
from ..external.airtable.airtable import Airtable
# from airtable.airtable import Airtable
current_date = datetime.now()

class YahooSportsNCAAB(Extractor):
    def __init__(self) -> None:
        self.name = "Yahoo Sports NCAAB"
        self.short_name = "YAHOONCAAB"

    def get_games(self):
        channels_table = Airtable("appE6mAL3izoxgdp7", "SPORT_CHANNELS", api_key="keyvWT1TdSyCaibez")
        m3u8_table = Airtable("appE6mAL3izoxgdp7", "IPTVmine1", api_key="keyvWT1TdSyCaibez")

        channels_records = channels_table.get_all()
        m3u8_records = m3u8_table.get_all()

        m3u8s = {}
        for m3u8_record in m3u8_records:
            record_id = m3u8_record["id"]
            fields = m3u8_record["fields"]
            urls = []
            if "url" in fields and "://" in fields["url"]: urls.append(Link(fields["url"]))
            for i in range(1, 5):
                if "link" + str(i) in fields:
                    url = fields["link" + str(i)]
                    if "://" in url: urls.append(Link(url))
            m3u8s[record_id] = urls

        channels = {}
        for record in channels_records:
            fields = record["fields"]
            if "label" in fields:
                label = fields["label"]
                urls = []
                if "url" in fields and fields["url"] != "-": urls.append(Link(fields["url"]))
                if "IPTVmine1" in fields and fields["IPTVmine1"] != "-":
                    for record_id in fields["IPTVmine1"]: urls += m3u8s[record_id]
                channels[label] = urls

        # Get games
        games = []
        for league in ["NCAAB"]:
            try:
                r_scores = requests.get("https://api-secure.sports.yahoo.com/v1/editorial/s/scoreboard", params={"leagues": league.lower(), "date": current_date.strftime("%Y-%m-%d")}).json()
                scoreboard = r_scores["service"]["scoreboard"]
                teams = scoreboard["teams"]
                for game in scoreboard["games"].values():
                    home_team_name = teams[game["home_team_id"]]["full_name"]
                    icon = scoreboard["teamsportacularLogo"][game["home_team_id"]]
                    away_team_name = teams[game["away_team_id"]]["full_name"]
                    home_score = 0
                    away_score = 0
                    for period in game["game_periods"]:
                        home_score += int(period["home_points"])
                        away_score += int(period["away_points"])
                    status = game["status_display_name"]
                    
                    links = []
                    if game["tv_coverage"] != "":
                        tv_coverage = game["tv_coverage"].split(", ")
                        for channel in tv_coverage: 
                            try: links += channels[channel]
                            except: continue
                    
                    if links == []:
                        continue
                        
                    game_title = "%s vs. %s" % (home_team_name, away_team_name)
                    title = "[COLORorange]%s %s-%s[/COLOR]: %s" % (status, str(home_score), str(away_score), game_title)
                    game_time = datetime(*(time.strptime(game["start_time"], "%a, %d %b %Y %H:%M:%S +0000")[:6]))
                    games.append(Game(title=title, links=links, icon=icon, league=league, starttime=game_time))
            except: continue

        return games