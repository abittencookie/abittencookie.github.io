# -*- coding: utf-8 -*-
from apis.trakt_api import trakt_fetch_collection_watchlist, trakt_get_hidden_items, trakt_get_my_calendar
from indexers.episodes import build_single_episode
from modules.utils import get_datetime
from modules.settings import nextep_content_settings, watched_indicators
from modules.watched_status import get_in_progress_episodes, get_next_episodes, get_watched_info_tv
# from modules.kodi_utils import logger

def build_in_progress_episode():
	data = get_in_progress_episodes()
	build_single_episode('progress', data)

def build_next_episode():
	nextep_settings = nextep_content_settings()
	include_unwatched = nextep_settings['include_unwatched']
	indicators = watched_indicators()
	watched_info = get_watched_info_tv(indicators)
	data = get_next_episodes(watched_info)
	if indicators == 1:
		list_type = 'next_episode_trakt'
		try:
			hidden_data = trakt_get_hidden_items('progress_watched')
			data = [i for i in data if not i['media_ids']['tmdb'] in hidden_data]
		except: pass
	else: list_type = 'next_episode_ezra'
	if include_unwatched:
		try: unwatched = [{'media_ids': i['media_ids'], 'season': 1, 'episode': 0, 'unwatched': True} for i in trakt_fetch_collection_watchlist('watchlist', 'tvshow')]
		except: unwatched = []
		data += unwatched
	build_single_episode(list_type, data)

def build_my_calendar(params):
	recently_aired = params.get('recently_aired', None)
	data = trakt_get_my_calendar(recently_aired, get_datetime())
	if recently_aired: list_type, data = 'trakt_recently_aired', data[:20]
	else: list_type, data = 'trakt_calendar', sorted(data, key=lambda k: k['sort_title'], reverse=False)
	build_single_episode(list_type, data)
