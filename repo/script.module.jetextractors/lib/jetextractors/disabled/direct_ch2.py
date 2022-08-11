from datetime import datetime

from ..models.Extractor import Extractor
from ..models.Game import Game
from ..models.Link import Link
from ..external.airtable.airtable import Airtable
# from airtable.airtable import Airtable
current_date = datetime.now()

class DirectCh2(Extractor):
    def __init__(self) -> None:
        self.name = "Direct_CH2"
        self.short_name = "DIRECT2"

    def get_games(self):
        channels_table = Airtable("appLN8hccpRoZIikO", "DIRECT_CHANNELS", api_key="keyvWT1TdSyCaibez")
        m3u8_table = Airtable("appLN8hccpRoZIikO", "IPTVmine1", api_key="keyvWT1TdSyCaibez")

        channels_records = channels_table.get_all()
        m3u8_records = m3u8_table.get_all()

        m3u8s = {}
        for m3u8_record in m3u8_records:
            record_id = m3u8_record["id"]
            fields = m3u8_record["fields"]
            urls = []
            # if "url" in fields and "://" in fields["url"]: urls.append(unidecode(fields["url"]))
            if "SERVER2" in fields and "://" in fields["SERVER2"]: urls.append(Link(address=fields["SERVER2"]))
            # if "inks" in fields and "://" in fields["inks"]: urls.append("ffmpegdirect://" + unidecode(fields["inks"]))
            # if "test" in fields and "://" in fields["test"]: urls.append("PlayMedia(&quot;pvr://channels/tv/All%20channels/pvr.iptvsimple_" + unidecode(fields["test"]))
            # for i in range(1, 5):
            #     if "link" + str(i) in fields:
            #         url = fields["link" + str(i)]
            #         if "://" in url: urls.append(unidecode(url))
            m3u8s[record_id] = urls

        games = []
        for record in channels_records:
            fields = record["fields"]
            if "name" in fields:
                name = fields["name"]
                thumbnail = fields.get("icon", "")
                urls = []
                if "url" in fields and fields["url"] != "-": urls.append(Link(address=fields["url"].strip()))
                if "link1" in fields and fields["link1"] != "-": urls.append(Link(address=fields["link1"].strip()))
                if "IPTVmine1" in fields and fields["IPTVmine1"] != "-":
                    for record_id in fields["IPTVmine1"]: urls.extend(m3u8s[record_id])
                # if "IPTVCAT" in fields and fields["IPTVCAT"] != "-":
                    # for record_id in fields["IPTVCAT"]: urls.extend(m3u8s[record_id])    
                games.append(Game(title=name, links=urls, icon=thumbnail))
        
        return games