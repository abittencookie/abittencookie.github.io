# -*- coding: utf-8 -*-
# modified by Venom for Fenomscrapers (updated 12-16-2021)
"""
	Fenomscrapers Project
"""

import re
from urllib.parse import quote_plus, unquote_plus
from fenomscrapers.modules import client
from fenomscrapers.modules import source_utils
from fenomscrapers.modules import workers


class source:
	priority = 6
	pack_capable = False
	hasMovies = False
	hasEpisodes = True
	def __init__(self):
		self.language = ['en']
		self.base_link = "https://eztv.re"
		# eztv has api but it sucks. Site query returns more results vs. api (eztv db seems to be missing the imdb_id for many so they are dropped)
		self.search_link = '/search/%s'
		self.min_seeders = 0

	def sources(self, data, hostDict):
		sources = []
		if not data: return sources
		append = sources.append
		try:
			title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ')
			aliases = data['aliases']
			episode_title = data['title']
			year = data['year']
			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode']))

			query = '%s %s' % (title, hdlr)
			# query = re.sub(r'[^A-Za-z0-9\s\.-]+', '', query) #eztv has issues with dashes in titles
			query = re.sub(r'[^A-Za-z0-9\s\.]+', '', query)
			url = self.search_link % (quote_plus(query).replace('+', '-'))
			url = '%s%s' % (self.base_link, url)
			# log_utils.log('url = %s' % url)
			results = client.request(url, timeout=5)
			if not results: return sources
			rows = client.parseDOM(results, 'tr')
			if not rows: return sources
			undesirables = source_utils.get_undesirables()
			check_foreign_audio = source_utils.check_foreign_audio()
		except:
			source_utils.scraper_error('EZTV')
			return sources

		for row in rows:
			try:
				try:
					columns = re.findall(r'<td\s.+?>(.*?)</td>', row, re.DOTALL)
					link = re.findall(r'href\s*=\s*["\'](magnet:[^"\']+)["\'].*?title\s*=\s*["\'](.+?)["\']', columns[2], re.DOTALL | re.I)[0]
				except: continue

				url = unquote_plus(client.replaceHTMLCodes(link[0])).split('&tr')[0]
				hash = re.search(r'btih:(.*?)&', url, re.I).group(1)
				name = ''.join(link[1].partition('[eztv]')[:2])
				name = source_utils.clean_name(name)

				if not source_utils.check_title(title, aliases, name, hdlr, year): continue
				name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title)
				if source_utils.remove_lang(name_info, check_foreign_audio): continue
				if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

				try:
					seeders = int(re.search(r'>(\d+|\d+\,\d+)<', columns[5]).group(1).replace(',', ''))
					if self.min_seeders > seeders: continue
				except: seeders = 0

				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					dsize, isize = source_utils._size(columns[3])
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				append({'provider': 'eztv', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info,
							'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
			except:
				source_utils.scraper_error('EZTV')
		return sources