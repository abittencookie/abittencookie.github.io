# -*- coding: utf-8 -*-
from apis.furk_api import FurkAPI
from modules import source_utils
from modules.utils import clean_file_name, normalize
from modules.settings import filter_by_name
# from modules.kodi_utils import logger

Furk = FurkAPI()
internal_results, check_title = source_utils.internal_results, source_utils.check_title
get_file_info, release_info_format = source_utils.get_file_info, source_utils.release_info_format

class source:
	def __init__(self):
		self.scrape_provider = 'furk'
		self.sources = []

	def results(self, info):
		try:
			title_filter = filter_by_name('furk')
			self.media_type, title, self.year, self.season, self.episode = info.get('media_type'), info.get('title'), int(info.get('year')), info.get('season'), info.get('episode')
			self.search_title = clean_file_name(title).replace(' ', '+').replace('&', 'and')
			files = Furk.search(self._search_name(), info.get('expiry_times')[0])
			if not files: return internal_results(self.scrape_provider, self.sources)
			cached_files = [i for i in files if i.get('type') not in ('default', 'audio', '') and i.get('is_ready') == '1']
			aliases = source_utils.get_aliases_titles(info.get('aliases', []))
			def _process():
				for i in cached_files:
					try:
						if self.media_type == 'movie': files_num_video = 1
						else: files_num_video = int(i['files_num_video'])
						if files_num_video > 3: package, season_compare, size = 'true', 'pack', float(round(float(int(i['size']))/1073741824, 2))/files_num_video
						else: package, season_compare, size = 'false', self.season, round(float(int(i['size']))/1073741824, 2)
						file_name = normalize(i['name'])
						if title_filter and not check_title(title, file_name, aliases, self.year, season_compare, self.episode): continue
						file_id, file_dl = i['id'], i['url_dl']
						URLName = clean_file_name(file_name).replace('html', ' ').replace('+', ' ').replace('-', ' ')
						video_quality, details = get_file_info(name_info=release_info_format(file_name))
						source_item = {'name': file_name, 'title': file_name, 'URLName': URLName, 'quality': video_quality, 'size': size, 'size_label': '%.2f GB' % size,
									'extraInfo': details, 'url_dl': file_dl, 'id': file_id, 'local': False, 'direct': True, 'package': package, 'source': self.scrape_provider,
									'scrape_provider': self.scrape_provider}
						yield source_item
					except Exception as e:
						from modules.kodi_utils import logger
						logger('FURK ERROR - 65', e)
			self.sources = list(_process())
		except Exception as e:
			from modules.kodi_utils import logger
			logger('EZRA furk scraper Exception', e)
		internal_results(self.scrape_provider, self.sources)
		return self.sources

	def _search_name(self):
		if self.media_type == 'movie': return '@name+%s+%d+|+%d+|+%d' % (self.search_title, self.year-1, self.year, self.year+1)
		else: return '@name+%s+@files+%s+|+%s+|+%s+|+%s+|+%s+|+%s+|+%s' % self.tvshow_query()

	def tvshow_query(self):
		return (self.search_title, 's%de%02d' % (self.season, self.episode), 's%02de%02d' % (self.season, self.episode), '%dx%02d' % (self.season, self.episode),
				'%02dx%02d' % (self.season, self.episode), '"season %d episode %d"' % (self.season, self.episode), '"season %d episode %02d"' % (self.season, self.episode),
				'"season %02d episode %02d"' % (self.season, self.episode))
