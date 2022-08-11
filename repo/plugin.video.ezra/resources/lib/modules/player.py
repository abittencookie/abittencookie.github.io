# -*- coding: utf-8 -*-
import re
import os
import json
from sys import argv
from threading import Thread
from apis.trakt_api import make_trakt_slug
from windows import open_window
from modules import kodi_utils, settings, watched_status as indicators
from modules.meta_lists import language_choices
from modules.settings_reader import get_setting
from modules.utils import sec2time, clean_file_name
# from modules.kodi_utils import logger

ls = kodi_utils.local_string
poster_empty = kodi_utils.translate_path('special://home/addons/plugin.video.ezra/resources/media/box_office.png')
fanart_empty = kodi_utils.translate_path('special://home/addons/plugin.video.ezra/fanart.png')

class EzraPlayer(kodi_utils.xbmc_player):
	def __init__ (self):
		kodi_utils.xbmc_player.__init__(self)
		self.set_resume, self.set_watched = 5, 90
		self.media_marked, self.subs_searched, self.nextep_info_gathered = False, False, False
		self.nextep_started, self.random_continual_started = False, False
		self.autoplay_next_episode, self.play_random_continual = False, False
		self.autoplay_nextep = settings.autoplay_next_episode()
		self.volume_check = get_setting('volumecheck.enabled', 'false') == 'true'

	def run(self, url=None, media_type=None):
		if not url: return
		try:
			if media_type == 'video':
				playlist = kodi_utils.make_playlist(media_type)
				playlist.clear()
				listitem = kodi_utils.make_listitem()
				listitem.setInfo(type=media_type, infoLabels={})
				playlist.add(url, listitem)
				kodi_utils.close_all_dialog()
				return self.play(playlist)
			self.meta = json.loads(kodi_utils.get_property('ezra_playback_meta'))
			self.meta_get = self.meta.get
			self.tmdb_id, self.imdb_id, self.tvdb_id = self.meta_get('tmdb_id'), self.meta_get('imdb_id'), self.meta_get('tvdb_id')
			self.media_type, self.title, self.year = self.meta_get('media_type'), self.meta_get('title'), self.meta_get('year')
			self.season, self.episode = self.meta_get('season', ''), self.meta_get('episode', '')
			background = self.meta.get('background', False) == True
			library_item = True if 'from_library' in self.meta else False
			if 'random' in self.meta or 'random_continual' in self.meta: bookmark = 0
			elif library_item: bookmark = self.bookmarkLibrary()
			else: bookmark = self.bookmarkEzra()
			if bookmark == 'cancel': return
			self.meta.update({'url': url, 'bookmark': bookmark})
			try:
				poster_main, poster_backup, fanart_main, fanart_backup = settings.get_art_provider()
				poster = self.meta_get(poster_main) or self.meta_get(poster_backup) or poster_empty
				fanart = self.meta_get(fanart_main) or self.meta_get(fanart_backup) or fanart_empty
				duration, plot, genre, trailer = self.meta_get('duration'), self.meta_get('plot'), self.meta_get('genre'), self.meta_get('trailer')
				rating, votes, premiered, studio = self.meta_get('rating'), self.meta_get('votes'), self.meta_get('premiered'), self.meta_get('studio')
				listitem = kodi_utils.make_listitem()
				listitem.setPath(url)
				if self.media_type == 'movie':
					listitem.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': str(self.tmdb_id)})
					listitem.setInfo('video', {'mediatype': 'movie', 'trailer': trailer, 'title': self.title, 'size': '0', 'duration': duration, 'plot': plot,
						'rating': rating, 'premiered': premiered, 'studio': studio,'year': self.year, 'genre': genre, 'tagline': self.meta_get('tagline'), 'code': self.imdb_id,
						'imdbnumber': self.imdb_id, 'director': self.meta_get('director'), 'writer': self.meta_get('writer'), 'votes': votes})
				else:
					listitem.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': str(self.tmdb_id), 'tvdb': str(self.tvdb_id)})
					listitem.setInfo('video', {'mediatype': 'episode', 'trailer': trailer, 'title': self.meta_get('ep_name'), 'imdbnumber': self.imdb_id,
						'tvshowtitle': self.title, 'size': '0', 'plot': plot, 'year': self.year, 'votes': votes, 'premiered': premiered, 'studio': studio, 'genre': genre,
						'season': self.season, 'episode': self.episode, 'duration': duration, 'rating': rating, 'FileNameAndPath': url})
				listitem.setCast(self.meta_get('cast', []))
				if settings.get_fanart_data():
					banner, clearart, clearlogo, landscape = self.meta_get('banner'), self.meta_get('clearart'), self.meta_get('clearlogo'), self.meta_get('landscape')
				else: banner, clearart, clearlogo, landscape = '', '', '', ''
				listitem.setArt({'poster': poster, 'fanart': fanart, 'icon': poster, 'banner': banner, 'clearart': clearart, 'clearlogo': clearlogo, 'landscape': landscape,
								'tvshow.clearart': clearart, 'tvshow.clearlogo': clearlogo, 'tvshow.landscape': landscape, 'tvshow.banner': banner})
				if not library_item: listitem.setProperty('StartPercent', str(bookmark))
				try:
					kodi_utils.clear_property('script.trakt.ids')
					trakt_ids = {'tmdb': self.tmdb_id, 'imdb': self.imdb_id, 'slug': make_trakt_slug(self.title)}
					if self.media_type == 'episode': trakt_ids['tvdb'] = self.tvdb_id
					kodi_utils.set_property('script.trakt.ids', json.dumps(trakt_ids))
				except: pass
			except: pass
			if library_item and not background:
				listitem.setProperty('IsPlayable', 'true')
				kodi_utils.set_resolvedurl(int(argv[1]), listitem)
			else: self.play(url, listitem)
			self.monitor()
		except: return

	def bookmarkEzra(self):
		bookmark = 0
		watched_indicators = settings.watched_indicators()
		try: resume_point, curr_time, resume_id = indicators.detect_bookmark(indicators.get_bookmarks(watched_indicators, self.media_type), self.tmdb_id, self.season, self.episode)
		except: resume_point, curr_time = 0, 0
		resume_check = float(resume_point)
		if resume_check > 0:
			percent = str(resume_point)
			raw_time = float(curr_time)
			if watched_indicators == 1: _time = '%s%%' % str(percent)
			else: _time = sec2time(raw_time, n_msec=0)
			bookmark = self.getResumeStatus(_time, percent, bookmark)
			if bookmark == 0: indicators.erase_bookmark(self.media_type, self.tmdb_id, self.season, self.episode)
		return bookmark

	def bookmarkLibrary(self):
		from modules.kodi_library import get_bookmark_kodi_library
		bookmark = 0
		try: curr_time = get_bookmark_kodi_library(self.media_type, self.tmdb_id, self.season, self.episode)
		except: curr_time = 0.0
		if curr_time > 0:
			self.kodi_library_resumed = False
			_time = sec2time(curr_time, n_msec=0)
			bookmark = self.getResumeStatus(_time, curr_time, bookmark)
			if bookmark == 0: indicators.erase_bookmark(self.media_type, self.tmdb_id, self.season, self.episode)
		return bookmark

	def getResumeStatus(self, _time, percent, bookmark):
		if settings.auto_resume(self.media_type): return percent
		choice = open_window(('windows.yes_no_progress_media', 'YesNoProgressMedia'), 'yes_no_progress_media.xml',
								meta=self.meta, text=ls(32790) % _time, enable_buttons=True, true_button=ls(32832), false_button=ls(32833), focus_button=10, percent=percent)
		return percent if choice == True else bookmark if choice == False else 'cancel'

	def monitor(self):
		if self.media_type == 'episode':
			self.play_random_continual = 'random_continual' in self.meta
			if not self.play_random_continual and self.autoplay_nextep: self.autoplay_next_episode = 'random' not in self.meta
		while not self.isPlayingVideo(): kodi_utils.sleep(100)
		kodi_utils.close_all_dialog()
		if self.volume_check: kodi_utils.volume_checker(get_setting('volumecheck.percent', '100'))
		kodi_utils.sleep(1000)
		while self.isPlayingVideo():
			try:
				kodi_utils.sleep(1000)
				self.total_time, self.curr_time = self.getTotalTime(), self.getTime()
				self.current_point = round(float(self.curr_time/self.total_time * 100), 1)
				if self.current_point >= self.set_watched and not self.media_marked:
					self.media_watched_marker()
					if self.play_random_continual: self.run_random_continual()
				if self.autoplay_next_episode:
					if not self.nextep_info_gathered: self.info_next_ep()
					self.remaining_time = round(self.total_time - self.curr_time)
					if self.remaining_time <= self.start_prep:
						if not self.nextep_started: self.run_next_ep()
			except: pass
		if not self.media_marked: self.media_watched_marker()
		indicators.clear_local_bookmarks()

	def media_watched_marker(self):
		self.media_marked = True
		try:
			if self.current_point >= self.set_watched:
				if self.media_type == 'movie':
					watched_function = indicators.mark_as_watched_unwatched_movie
					watched_params = {'mode': 'mark_as_watched_unwatched_movie', 'action': 'mark_as_watched', 'tmdb_id': self.tmdb_id, 'title': self.title, 'year': self.year,
									'refresh': 'false', 'from_playback': 'true'}
				else:
					watched_function = indicators.mark_as_watched_unwatched_episode
					watched_params = {'mode': 'mark_as_watched_unwatched_episode', 'action': 'mark_as_watched', 'season': self.season, 'episode': self.episode,
									'tmdb_id': self.tmdb_id, 'title': self.title, 'year': self.year, 'tvdb_id': self.tvdb_id, 'refresh': 'false', 'from_playback': 'true'}
				Thread(target=self.run_media_watched, args=(watched_function, watched_params)).start()
			else:
				kodi_utils.clear_property('ezra_nextep_autoplays')
				kodi_utils.clear_property('ezra_random_episode_history')
				if self.current_point >= self.set_resume:
					indicators.set_bookmark(self.media_type, self.tmdb_id, self.curr_time, self.total_time, self.title, self.season, self.episode)
		except: pass

	def run_media_watched(self, function, params):
		try:
			function(params)
			kodi_utils.sleep(1000)
		except: pass

	def run_next_ep(self):
		self.nextep_started = True
		try:
			from modules.next_episode_tools import execute_nextep
			Thread(target=execute_nextep, args=(self.meta, self.nextep_settings)).start()
		except: pass

	def run_random_continual(self):
		try:
			from modules.random_play import play_random_continual
			Thread(target=play_random_continual, args=(self.tmdb_id,)).start()
		except: pass

	def info_next_ep(self):
		self.nextep_info_gathered = True
		try:
			self.nextep_settings = settings.autoplay_next_settings()
			if not self.nextep_settings['run_popup']:
				window_time = round(0.02 * self.total_time)
				self.nextep_settings['window_time'] = window_time
			elif self.nextep_settings['timer_method'] == 'percentage':
				percentage = self.nextep_settings['window_percentage']
				window_time = round((percentage/100) * self.total_time)
				self.nextep_settings['window_time'] = window_time
			else:
				window_time = self.nextep_settings['window_time']
			threshold_check = window_time + 21
			self.start_prep = self.nextep_settings['scraper_time'] + threshold_check
			self.nextep_settings.update({'threshold_check': threshold_check, 'start_prep': self.start_prep})
		except: pass

	def onAVStarted(self):
		try: kodi_utils.close_all_dialog()
		except: pass

	def onPlayBackStarted(self):
		try: kodi_utils.close_all_dialog()
		except: pass






