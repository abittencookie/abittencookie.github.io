import requests, time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from ..models.Extractor import Extractor
from ..models.Game import Game
from ..models.Link import Link
from ..external.airtable.airtable import Airtable
# from airtable.airtable import Airtable
current_date = datetime.now()

class YahooSports(Extractor):
    def __init__(self) -> None:
        self.name = "Yahoo Sports"
        self.short_name = "YAHOO"

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
            if "SERVER2" in fields and "://" in fields["SERVER2"]: urls.append(Link(fields["SERVER2"].strip()))
            if "SERVER" in fields and "://" in fields["SERVER"]: urls.append(Link(fields["SERVER"], jetproxy=True))
            if "IPTVCAT" in fields and "://" in fields["IPTVCAT"]: urls.append(Link(fields["IPTVCAT"]))
            # for i in range(1, 5):
            #     if "link" + str(i) in fields:
            #         url = fields["link" + str(i)]
            #         if "://" in url: urls.append(unidecode(url))
            m3u8s[record_id] = urls

        channels = {}
        for record in channels_records:
            fields = record["fields"]
            if "label" in fields:
                label = fields["label"]
                urls = []
                if "url" in fields and fields["url"] != "-": urls.append(Link(fields["url"].strip()))
                if "link1" in fields and fields["link1"] != "-": urls.append(Link(fields["link1"].strip()))
                if "IPTVmine1" in fields and fields["IPTVmine1"] != "-":
                    for record_id in fields["IPTVmine1"]: urls.extend(m3u8s[record_id])
                # if "IPTVCAT" in fields and fields["IPTVCAT"] != "-":
                # for record_id in fields["IPTVCAT"]: urls.extend(m3u8s[record_id])
                channels[label] = urls
            

        # Get games
        games = []
        for league in ["NFL", "NCAAF", "NBA", "NCAAB", "NHL", "MLB"]:
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
                        home_score += int(period["home_points"]) if period["home_points"] != "X" else 0
                        away_score += int(period["away_points"]) if period["away_points"] != "X" else 0
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
                    game_title = "[COLORorange]%s %s-%s[/COLOR]: %s" % (status, str(home_score), str(away_score), game_title)
                    game_time = datetime(*(time.strptime(game["start_time"], "%a, %d %b %Y %H:%M:%S +0000")[:6]))
                    games.append(Game(title=game_title, links=links, icon=icon, league=league, starttime=game_time))
            except: continue
        
        soccer_games = {}
        for soccer_site in ["https://sportsontvusa.com", "https://ukfootballontv.co.uk"]:
            r = requests.post(soccer_site, {"opSearch": 1}).text
            soup = BeautifulSoup(r, "html.parser")
            table = soup.select_one("table.table")
            try: table_date = datetime(*(time.strptime(table.select_one("td.dia-partido").next.replace("Today ", ""), "%A, %B %d, %Y")[:6]))
            except:
                try: table_date = datetime(*(time.strptime(table.select_one("td.dia-partido").next.replace("Today ", ""), "%A, %d %B %Y")[:6]))
                except: continue
            for game in table.select("tr.event-row"):
                game_time = game.select_one("td.hora").next
                game_time_split = game_time.split(":")
                game_hour = int(game_time_split[0])
                game_minute = int(game_time_split[1])
                game_date = table_date.replace(hour=game_hour, minute=game_minute) + timedelta(hours=4)
                teams = [team.get("title") for team in game.select("span")]
                game_channels = list(filter(lambda x: "Fanatiz" not in x, [channel.text for channel in game.select("li.premium") + game.select("li.abierto")]))
                try: game_icon = game.select_one("img").get("data-ezsrc")
                except: game_icon = ""
                links = []
                if len(teams) > 1: game_title = "%s vs %s" % (teams[0], teams[1])
                else: game_title = game.select_one("td.evento").text
                for channel in game_channels:
                    try: links += channels[channel]
                    except: continue
                if links == []:
                    continue
                if game_title not in soccer_games:
                    soccer_games[game_title] = Game(title=game_title, links=links, icon=game_icon, league="Soccer", starttime=game_date)
                else:
                    soccer_games[game_title].links += links
        soccer_games = sorted(soccer_games.values(), key=lambda x: x.starttime)
        games += soccer_games
        
        return games
