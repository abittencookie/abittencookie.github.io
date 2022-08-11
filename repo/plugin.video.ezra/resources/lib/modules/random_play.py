# -*- coding: utf-8 -*-
import json
from random import choice
from threading import Thread
import metadata
from modules.sources import Sources
from modules.player import EzraPlayer
from modules.settings import date_offset, metadata_user_info
from modules.kodi_utils import execute_builtin, build_url, get_property, set_property, clear_property, sleep
from modules.utils import adjust_premiered_date, get_datetime
# from modules.kodi_utils import logger

def get_random_episode(tmdb_id, continual=False):
	meta_user_info, adjust_hours, current_date = metadata_user_info(), date_offset(), get_datetime()
	tmdb_key = str(tmdb_id)
	meta = metadata.tvshow_meta('tmdb_id', tmdb_id, meta_user_info, current_date)
	try:
		episodes_data = metadata.all_episodes_meta(meta, meta_user_info, Thread)
		episodes_data = [i for i in episodes_data if not i['season']  == 0 and adjust_premiered_date(i['premiered'], adjust_hours)[0] <= current_date]
	except: episodes_data = []
	if not episodes_data: return None
	if continual:
		episode_list = []
		try:
			episode_history = json.loads(get_property('ezra_random_episode_history'))
			if tmdb_key in episode_history: episode_list = episode_history[tmdb_key]
			else: set_property('ezra_random_episode_history', '')
		except: pass
		first_run = len(episode_list) == 0
		episodes_data = [i for i in episodes_data if not i in episode_list]
		if not episodes_data:
			set_property('ezra_random_episode_history', '')
			return get_random_episode(tmdb_id, continual=True)
	else: first_run = True
	chosen_episode = choice(episodes_data)
	if continual:
		episode_list.append(chosen_episode)
		episode_history = {str(tmdb_id): episode_list}
		set_property('ezra_random_episode_history', json.dumps(episode_history))
	title, season, episode = meta['title'], int(chosen_episode['season']), int(chosen_episode['episode'])
	query = title + ' S%.2dE%.2d' % (season, episode)
	display_name = '%s - %dx%.2d' % (title, season, episode)
	ep_name, plot = chosen_episode['title'], chosen_episode['plot']
	try: premiered = adjust_premiered_date(chosen_episode['premiered'], adjust_hours)[1]
	except: premiered = chosen_episode['premiered']
	meta.update({'media_type': 'episode', 'rootname': display_name, 'season': season, 'episode': episode, 'premiered': premiered, 'ep_name': ep_name, 'plot': plot})
	if continual: meta['random_continual'] = 'true'
	else: meta['random'] = 'true'
	url_params = {'mode': 'play_media', 'media_type': 'episode', 'tmdb_id': meta['tmdb_id'], 'query': query,
					'tvshowtitle': meta['rootname'], 'season': season, 'episode': episode, 'autoplay': 'True', 'meta': json.dumps(meta)}
	if not first_run: url_params['background'] = 'true'
	return url_params

def play_random(tmdb_id):
	url_params = get_random_episode(tmdb_id)
	if not url_params: return {'pass': True}
	return execute_builtin('RunPlugin(%s)' % build_url(url_params))

def play_random_continual(tmdb_id):
	url_params = get_random_episode(tmdb_id, continual=True)
	if not url_params: return {'pass': True}
	player = EzraPlayer()
	Sources().playback_prep(url_params)
	url = get_property('ezra_background_url')
	clear_property('ezra_background_url')
	while player.isPlayingVideo(): sleep(100)
	player.run(url)
