# -*- coding: utf-8 -*-
import json
import time
from random import shuffle
from threading import Thread
from windows import create_window
from caches.providers_cache import ExternalProvidersCache
from modules import kodi_utils, source_utils
from modules.debrid import debrid_check
from modules.utils import clean_file_name
from modules.settings import display_sleep_time, date_offset
from modules.settings_reader import get_setting
# logger = kodi_utils.logger

ls, sleep, monitor, get_property, set_property = kodi_utils.local_string, kodi_utils.sleep, kodi_utils.monitor, kodi_utils.get_property, kodi_utils.set_property
notification, hide_busy_dialog, clear_property = kodi_utils.notification, kodi_utils.hide_busy_dialog, kodi_utils.clear_property
normalize, get_filename_match, get_file_info, pack_enable_check = source_utils.normalize, source_utils.get_filename_match, source_utils.get_file_info, source_utils.pack_enable_check
pack_display, format_line, total_format = '%s (%s)', '%s[CR]%s[CR]%s', '[COLOR %s][B]%s[/B][/COLOR]'
int_format, ext_format = '[COLOR %s][B]Int:[/B][/COLOR]%s', '[COLOR %s][B]Ext:[/B][/COLOR]%s'
ext_scr_format, unfinshed_import_format = '[COLOR %s][B]%s[/B][/COLOR]', '[COLOR red]+%s[/COLOR]'
diag_format = '4K: %s | 1080p: %s | 720p: %s | SD: %s | %s: %s'
debrid_hash_tuple = (('Real-Debrid', 'rd_cached_hashes'), ('Premiumize.me', 'pm_cached_hashes'), ('AllDebrid', 'ad_cached_hashes'))
season_display, show_display = ls(32537), ls(32089)
pack_check = (season_display, show_display)

class source:
	def __init__(self, source_dict, debrid_torrents, debrid_hosters, internal_scrapers, prescrape_sources, display_uncached_torrents, progress_dialog, disabled_ignored=False):
		self.scrape_provider = 'external'
		self.debrid_torrents, self.debrid_hosters = debrid_torrents, debrid_hosters
		self.source_dict, self.hostDict = source_dict, self.make_host_dict()
		self.internal_scrapers, self.prescrape_sources = internal_scrapers, prescrape_sources
		self.display_uncached_torrents = display_uncached_torrents
		self.disabled_ignored, self.progress_dialog = disabled_ignored, progress_dialog
		self.internal_activated, self.internal_prescraped = len(self.internal_scrapers) > 0, len(self.prescrape_sources) > 0
		self.processed_prescrape, self.threads_completed = False, False
		self.sources, self.final_sources, self.processed_internal_scrapers = [], [], []
		self.processed_internal_scrapers_append = self.processed_internal_scrapers.append
		self.sleep_time = display_sleep_time()
		self.pause_scrape = (self.sleep_time*1.05)/1000
		self.int_dialog_highlight, self.ext_dialog_highlight = get_setting('int_dialog_highlight', 'darkgoldenrod'), get_setting('ext_dialog_highlight', 'dodgerblue')
		self.finish_early = get_setting('search.finish.early') == 'true'
		self.int_total, self.ext_total = total_format % (self.int_dialog_highlight, '%s'), total_format % (self.ext_dialog_highlight, '%s')
		self.timeout = 60 if self.disabled_ignored else int(get_setting('scrapers.timeout.1', '30'))
		self.meta = json.loads(get_property('ezra_playback_meta'))
		self.background = self.meta.get('background', False)
		self.internal_sources_total = self.internal_sources_4K = self.internal_sources_1080p = self.internal_sources_720p = self.internal_sources_sd = 0
		self.sources_total = self.sources_4k = self.sources_1080p = self.sources_720p = self.sources_sd = 0

	def results(self, info):
		if not self.source_dict: return 
		self.media_type, self.tmdb_id, self.orig_title = info['media_type'], str(info['tmdb_id']), info['title']
		self.season, self.episode, self.total_seasons = info['season'], info['episode'], info['total_seasons']
		self.title, self.year = normalize(info['title']), info['year']
		ep_name, aliases = normalize(info['ep_name']), info['aliases']
		self.single_expiry, self.season_expiry, self.show_expiry = info['expiry_times']
		if self.media_type == 'movie':
			self.season_divider, self.show_divider = 0, 0
			self.data = {'imdb': info['imdb_id'], 'title': self.title, 'aliases': aliases, 'year': self.year}
		else:
			self.season_divider = [int(x['episode_count']) for x in self.meta['season_data'] if int(x['season_number']) == int(self.meta['season'])][0]
			self.show_divider = int(self.meta['total_aired_eps'])
			self.data = {'imdb': info['imdb_id'], 'tvdb': info['tvdb_id'], 'tvshowtitle': self.title, 'aliases': aliases,'year': self.year,
						'title': ep_name, 'season': str(self.season), 'episode': str(self.episode)}
		return self.get_sources()

	def get_sources(self):
		def _scraperDialog():
			hide_busy_dialog()
			self.make_progress_dialog()
			string1, string2 = ls(32676), ls(32677)
			if self.internal_activated or self.internal_prescraped:
				string3 = int_format % (self.int_dialog_highlight, '%s')
				string4 = ext_format % (self.ext_dialog_highlight, '%s')
			else: string4 = ext_scr_format % (self.ext_dialog_highlight, ls(32118))
			line1 = line2 = line3 = ''
			start_time = time.time()
			end_time = start_time + self.timeout
			unfinshed_import_time, close_dialog = 0, True
			while not self.progress_dialog.iscanceled():
				try:
					if monitor.abortRequested() is True: break
					ext_4k, ext_1080 = self.ext_total % self.sources_4k, self.ext_total % self.sources_1080p
					ext_720, ext_sd = self.ext_total % self.sources_720p, self.ext_total % self.sources_sd
					source_total_label = self.ext_total % self.sources_total
					info = [x.getName() for x in threads if x.is_alive()]
					if self.internal_activated or self.internal_prescraped:
						remaining_internal_scrapers = self.process_internal_results()
						int_4k, int_1080 = self.int_total % self.internal_sources_4K, self.int_total % self.internal_sources_1080p
						int_720, int_sd = self.int_total % self.internal_sources_720p, self.int_total % self.internal_sources_sd
						internalSource_total_label = self.int_total % self.internal_sources_total
						info.extend(remaining_internal_scrapers)
						line1 = string3 % diag_format % (int_4k, int_1080, int_720, int_sd, string2, internalSource_total_label)
						line2 = string4 % diag_format % (ext_4k, ext_1080, ext_720, ext_sd, string2, source_total_label)
					else:
						line1 = string4
						line2 = diag_format % (ext_4k, ext_1080, ext_720, ext_sd, string2, source_total_label)
					len_alive_threads = len(info)
					if not self.threads_completed:
						unfinshed_import_time += self.pause_scrape
						line3 = string1 % unfinshed_import_format % str(len_alive_threads)
					elif len_alive_threads > 5: line3 = string1 % str(len_alive_threads)
					else: line3 = string1 % ', '.join(info).upper()
					current_time = time.time()
					current_progress = max((current_time - start_time - unfinshed_import_time), 0)
					percent = (current_progress/float(self.timeout))*100
					self.progress_dialog.update(format_line % (line1, line2, line3), percent)
					if self.threads_completed:
						if self.finish_early and percent >= 50:
							if len_alive_threads <= 5: close_dialog = False; break
							if len(self.sources) >= 100 * len_alive_threads: close_dialog = False; break
						if len_alive_threads == 0: close_dialog = False; break
						if percent >= 100: close_dialog = False; break
					sleep(self.sleep_time)
				except: pass
			if close_dialog: self.kill_progress_dialog()
			return
		def _background():
			sleep(1500)
			start_time = time.time()
			end_time = start_time + self.timeout
			while time.time() < end_time:
				alive_threads = [x for x in threads if x.is_alive()]
				sleep(self.sleep_time)
				if len(alive_threads) <= 5: return
				if len(self.sources) >= 100 * len(alive_threads): return
		threads = []
		self.threads_append = threads.append
		if self.media_type == 'movie': Thread(target=self.process_movie_threads, args=(self.source_dict,)).start()
		else:
			self.season_packs, self.show_packs = pack_enable_check(self.meta, self.season, self.episode)
			if self.season_packs:
				self.source_dict = [(i[0], i[1], '') for i in self.source_dict]
				pack_capable = [i for i in self.source_dict if i[1].pack_capable]
				if pack_capable:
					self.source_dict.extend([(i[0], i[1], ls(32537)) for i in pack_capable])
					if self.show_packs: self.source_dict.extend([(i[0], i[1], ls(32089)) for i in pack_capable])
					shuffle(self.source_dict)
			Thread(target=self.process_episode_threads, args=(self.source_dict,)).start()
		if self.background: _background()
		else: _scraperDialog()
		sleep(500)
		self.final_sources.extend(self.sources)
		self.process_duplicates()
		self.process_filters()
		clear_property('fs_filterless_search')
		return self.final_sources

	def get_movie_source(self, provider, module):
		_cache = ExternalProvidersCache()
		sources = _cache.get(provider, self.media_type, self.tmdb_id, self.title, self.year, '', '')
		if sources == None:
			if not module.hasMovies: return
			sources = module().sources(self.data, self.hostDict)			
			sources = self.process_sources(provider, sources)
			_cache.set(provider, self.media_type, self.tmdb_id, self.title, self.year, '', '', sources, self.single_expiry)
		if sources:
			self.process_quality_count(sources)
			self.sources.extend(sources)

	def get_episode_source(self, provider, module, pack):
		_cache = ExternalProvidersCache()
		if pack in pack_check:
			if pack == show_display: s_check = ''
			else: s_check = self.season
			e_check = ''
		else: s_check, e_check = self.season, self.episode
		sources = _cache.get(provider, self.media_type, self.tmdb_id, self.title, self.year, s_check, e_check)
		if sources == None:
			if not module.hasEpisodes: return
			if pack == show_display:
				expiry_hours = self.show_expiry
				sources = module().sources_packs(self.data, self.hostDict, search_series=True, total_seasons=self.total_seasons)
			elif pack == season_display:
				expiry_hours = self.season_expiry
				sources = module().sources_packs(self.data, self.hostDict)
			else:
				expiry_hours = self.single_expiry
				sources = module().sources(self.data, self.hostDict)
			sources = self.process_sources(provider, sources)
			_cache.set(provider, self.media_type, self.tmdb_id, self.title, self.year, s_check, e_check, sources, expiry_hours)
		if sources:
			if pack == season_display: sources = [i for i in sources if not 'episode_start' in i or i['episode_start'] <= self.episode <= i['episode_end']]
			elif pack == show_display: sources = [i for i in sources if i['last_season'] >= self.season]
			self.process_quality_count(sources)
			self.sources.extend(sources)

	def process_movie_threads(self, source_dict):
		for i in source_dict:
			provider, module = i[0], i[1]
			threaded_object = Thread(target=self.get_movie_source, args=(provider, module), name=provider)
			threaded_object.start()
			self.threads_append(threaded_object)
		self.threads_completed = True

	def process_episode_threads(self, source_dict):
		for i in source_dict:
			provider, module = i[0], i[1]
			try: pack_arg = i[2]
			except: pack_arg = ''
			if pack_arg: provider_display = pack_display % (i[0], i[2])
			else: provider_display = provider
			threaded_object = Thread(target=self.get_episode_source, args=(provider, module, pack_arg), name=provider_display)
			threaded_object.start()
			self.threads_append(threaded_object)
		self.threads_completed = True

	def process_duplicates(self):
		def _process(sources):
			uniqueURLs = set()
			uniqueHashes = set()
			for provider in sources:
				try:
					url = provider['url'].lower()
					if url not in uniqueURLs:
						uniqueURLs.add(url)
					if 'hash' in provider:
						if provider['hash'] not in uniqueHashes:
							uniqueHashes.add(provider['hash'])
							yield provider
					else: yield provider
				except: yield provider
		if len(self.final_sources) > 0: self.final_sources = list(_process(self.final_sources))

	def process_filters(self):
		def _process(result_list, target):
			for item in result_list:
				obj = Thread(target=target, args=(item,))
				obj.start()
				threads_append(obj)
		def _process_torrents(item):
			self.filter += [dict(i, **{'debrid':item}) for i in torrent_sources if item == i.get('cache_provider')]
			if self.display_uncached_torrents:
				self.filter += [dict(i, **{'debrid':item}) for i in torrent_sources if 'Uncached' in i.get('cache_provider') and item in i.get('cache_provider')]
		def _process_hosters(item):
			for k, v in item.items():
				valid_hosters = [i for i in result_hosters if i in v]
				self.filter += [dict(i, **{'debrid':k}) for i in hoster_sources if i['source'] in valid_hosters]
		threads = []
		threads_append = threads.append
		self.filter = []
		torrent_sources = self.process_torrents([i for i in self.final_sources if 'hash' in i])
		hoster_sources = [i for i in self.final_sources if not 'hash' in i]
		result_hosters = list(set([i['source'].lower() for i in hoster_sources]))
		if self.debrid_torrents and torrent_sources: _process(self.debrid_torrents, _process_torrents)
		if self.debrid_hosters and hoster_sources: _process(self.debrid_hosters, _process_hosters)
		if threads: [i.join() for i in threads]
		self.final_sources = self.filter

	def process_sources(self, provider, sources):
		try:
			for i in sources:
				try:
					i_get = i.get
					if 'hash' in i:
						_hash = i_get('hash').lower()
						i['hash'] = str(_hash)
					size, size_label, divider = 0, None, None
					if 'name' in i: URLName = clean_file_name(i_get('name')).replace('html', ' ').replace('+', ' ').replace('-', ' ')
					else: URLName = get_filename_match(self.orig_title, i_get('url'), i_get('name', None))
					if 'name_info' in i: quality, extraInfo = get_file_info(name_info=i_get('name_info'))
					else: quality, extraInfo = get_file_info(url=i_get('url'))
					try:
						size = i_get('size')
						if 'package' in i and provider != 'torrentio':
							if i_get('package') == 'season': divider = self.season_divider
							else: divider = self.show_divider
							size = float(size) / divider
							size_label = '%.2f GB' % size
						else: size_label = '%.2f GB' % size
					except: pass
					i.update({'provider': provider, 'external': True, 'scrape_provider': self.scrape_provider, 'extraInfo': extraInfo,
								'URLName': URLName, 'quality': quality, 'size_label': size_label, 'size': round(size, 2)})
				except: pass
		except: pass
		return sources
	
	def process_quality_count(self, sources, internal=False):
		if internal:
			for i in sources:
				quality = i['quality']
				if quality == '4K': self.internal_sources_4K += 1
				elif quality == '1080p': self.internal_sources_1080p += 1
				elif quality == '720p': self.internal_sources_720p += 1
				else: self.internal_sources_sd += 1
				self.internal_sources_total += 1
		else:
			for i in sources:
				quality = i['quality']
				if quality == '4K': self.sources_4k += 1
				elif quality == '1080p': self.sources_1080p += 1
				elif quality == '720p': self.sources_720p += 1
				else: self.sources_sd += 1
				self.sources_total += 1

	def process_torrents(self, torrent_sources):
		if not torrent_sources or not self.debrid_torrents:
			self.kill_progress_dialog()
			return []
		hash_list = [i['hash'] for i in torrent_sources]
		torrent_results = []
		try:
			hash_list = list(set(hash_list))
			cached_hashes = debrid_check.run(hash_list, self.background, self.debrid_torrents, self.meta, self.progress_dialog)
			for item in debrid_hash_tuple:
				if item[0] in self.debrid_torrents:
					torrent_results.extend([dict(i, **{'cache_provider':item[0]}) for i in torrent_sources if i['hash'] in cached_hashes[item[1]]])
					if self.display_uncached_torrents:
						torrent_results.extend([dict(i, **{'cache_provider':'Uncached %s' % item[0]}) for i in torrent_sources if not i['hash'] in cached_hashes[item[1]]])
		except:
			self.kill_progress_dialog()
			notification(32574, 2500)
		return torrent_results

	def process_internal_results(self):
		if self.internal_prescraped and not self.processed_prescrape:
			self.process_quality_count(self.prescrape_sources, internal=True)
			self.processed_prescrape = True
		for i in self.internal_scrapers:
			win_property = get_property('%s.internal_results' % i)
			if win_property in ('checked', '', None): continue
			try: internal_sources = json.loads(win_property)
			except: continue
			set_property('%s.internal_results' % i, 'checked')
			self.processed_internal_scrapers_append(i)
			self.process_quality_count(internal_sources, internal=True)
		return [i for i in self.internal_scrapers if not i in self.processed_internal_scrapers]

	def make_host_dict(self):
		pr_list = []
		pr_list_extend = pr_list.extend
		for item in self.debrid_hosters:
			for k, v in item.items(): pr_list_extend(v)
		return list(set(pr_list))

	def make_progress_dialog(self):
		if self.progress_dialog: return
		self.progress_dialog = create_window(('windows.yes_no_progress_media', 'YesNoProgressMedia'), 'yes_no_progress_media.xml', meta=self.meta)
		Thread(target=self.progress_dialog.run).start()

	def kill_progress_dialog(self):
		try: self.progress_dialog.close()
		except: pass
		try: del self.progress_dialog
		except: pass
		self.progress_dialog = None
