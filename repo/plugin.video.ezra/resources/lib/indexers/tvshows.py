# -*- coding: utf-8 -*-
from sys import argv
from threading import Thread
from metadata import tvshow_meta
from modules import kodi_utils, settings
from modules.utils import manual_function_import, get_datetime, make_thread_list_enumerate
from modules.watched_status import get_watched_info_tv, get_watched_status_tvshow
# logger = kodi_utils.logger

meta_function, get_datetime_function, add_item, select_dialog = tvshow_meta, get_datetime, kodi_utils.add_item, kodi_utils.select_dialog
get_watched_function, get_watched_info_function = get_watched_status_tvshow, get_watched_info_tv
set_content, end_directory, set_view_mode, get_infolabel = kodi_utils.set_content, kodi_utils.end_directory, kodi_utils.set_view_mode, kodi_utils.get_infolabel
string, ls, tp, external_browse, add_items = str, kodi_utils.local_string, kodi_utils.translate_path, kodi_utils.external_browse, kodi_utils.add_items
make_listitem, build_url, remove_meta_keys, dict_removals = kodi_utils.make_listitem, kodi_utils.build_url, kodi_utils.remove_meta_keys, kodi_utils.tvshow_dict_removals
metadata_user_info, watched_indicators, include_year_in_title = settings.metadata_user_info, settings.watched_indicators, settings.include_year_in_title
extras_open_action, get_art_provider, default_all_episodes = settings.extras_open_action, settings.get_art_provider, settings.default_all_episodes
tmdb_main, trakt_main = ('tmdb_tv_popular', 'tmdb_tv_premieres', 'tmdb_tv_airing_today','tmdb_tv_on_the_air','tmdb_tv_upcoming'), 'trakt_tv_trending'
trakt_personal, imdb_personal = ('trakt_collection', 'trakt_watchlist', 'trakt_collection_lists'), ('imdb_watchlist', 'imdb_user_list_contents', 'imdb_keywords_list_contents')
personal, similar = ('in_progress_tvshows', 'favourites_tvshows', 'watched_tvshows'), ('tmdb_tv_similar', 'tmdb_tv_recommendations')
tmdb_special = ('tmdb_tv_languages', 'tmdb_tv_networks', 'tmdb_tv_year')
tmdb_special_key_dict = {'tmdb_tv_languages': 'language', 'tmdb_tv_networks': 'network_id', 'tmdb_tv_year': 'year'}
personal_dict = {'in_progress_tvshows': ('modules.watched_status', 'get_in_progress_tvshows'), 'favourites_tvshows': ('modules.favourites', 'retrieve_favourites'),
				'watched_tvshows': ('modules.watched_status', 'get_watched_items')}
run_plugin, container_update, container_refresh = 'RunPlugin(%s)', 'Container.Update(%s)', 'Container.Refresh(%s)'
item_jump, item_next = tp('special://home/addons/plugin.video.ezra/resources/media/item_jump.png'), tp('special://home/addons/plugin.video.ezra/resources/media/item_next.png')
poster_empty, fanart_empty = tp('special://home/addons/plugin.video.ezra/resources/media/box_office.png'), tp('special://home/addons/plugin.video.ezra/fanart.png')
watched_str, unwatched_str, traktmanager_str = ls(32642), ls(32643), ls(32198)
favmanager_str, extras_str, options_str, random_str, recomm_str = ls(32197), ls(32645), ls(32646), ls(32611), '[B]%s...[/B]' % ls(32503)
exit_str, nextpage_str, switchjump_str, browse_str, jumpto_str = ls(32650), ls(32799), ls(32784), ls(32652), ls(32964)

class TVShows:
	def __init__(self, params):
		self.params = params
		self.id_type, self.list, self.action = self.params.get('id_type', 'tmdb_id'), self.params.get('list', []), self.params.get('action', None)
		self.items, self.new_page, self.total_pages, self.exit_list_params, self.is_widget = [], {}, None, None, 'unchecked'

	def fetch_list(self):
		try:
			params_get = self.params.get
			self.is_widget = external_browse()
			self.exit_list_params = params_get('exit_list_params', None) or get_infolabel('Container.FolderPath')
			self.handle = int(argv[1])
			content_type = 'tvshows'
			mode = params_get('mode')
			try: page_no = int(params_get('new_page', '1'))
			except ValueError: page_no = params_get('new_page')
			letter = params_get('new_letter', 'None')
			if self.action in personal: var_module, import_function = personal_dict[self.action]
			else: var_module, import_function = 'apis.%s_api' % self.action.split('_')[0], self.action
			try: function = manual_function_import(var_module, import_function)
			except: pass
			if self.action in tmdb_main:
				data = function(page_no)
				self.list = [i['id'] for i in data['results']]
				self.new_page = {'new_page': string(data['page'] + 1)}
			elif self.action == trakt_main:
				self.id_type = 'trakt_dict'
				data = function(page_no)
				self.list = [i['show']['ids'] for i in data]
				self.new_page = {'new_page': string(page_no + 1)}
			elif self.action in trakt_personal:
				self.id_type = 'trakt_dict'
				data, total_pages = function('shows', page_no, letter)
				self.list = [i['media_ids'] for i in data]
				if total_pages > 2: self.total_pages = total_pages
				try:
					if total_pages > page_no: self.new_page = {'new_page': string(page_no + 1), 'new_letter': letter}
				except: pass
			elif self.action in imdb_personal:
				self.id_type = 'imdb_id'
				list_id = params_get('list_id', None)
				data, next_page = function('tvshow', list_id, page_no)
				self.list = [i['imdb_id'] for i in data]
				if next_page: self.new_page = {'list_id': list_id, 'new_page': string(page_no + 1), 'new_letter': letter}
			elif self.action in personal:
				data, total_pages = function('tvshow', page_no, letter)
				self.list = [i['media_id'] for i in data]
				if total_pages > 2: self.total_pages = total_pages
				if total_pages > page_no: self.new_page = {'new_page': string(page_no + 1), 'new_letter': letter}
			elif self.action in similar:
				tmdb_id = self.params['tmdb_id']
				data = function(tmdb_id, page_no)
				self.list = [i['id'] for i in data['results']]
				if data['page'] < data['total_pages']: self.new_page = {'new_page': string(data['page'] + 1), 'tmdb_id': tmdb_id}
			elif self.action in tmdb_special:
				key = tmdb_special_key_dict[self.action]
				function_var = params_get(key, None)
				if not function_var: return
				data = function(function_var, page_no)
				self.list = [i['id'] for i in data['results']]
				if data['page'] < data['total_pages']: self.new_page = {'new_page': string(data['page'] + 1), key: function_var}
			elif self.action == 'tmdb_tv_discover':
				from indexers.discover import set_history
				name = self.params['name']
				query = self.params['query']
				if page_no == 1: set_history('tvshow', name, query)
				data = function(query, page_no)
				self.list = [i['id'] for i in data['results']]
				if data['page'] < data['total_pages']: self.new_page = {'query': query, 'name': name, 'new_page': string(data['page'] + 1)}
			elif self.action == 'tmdb_tv_genres':
				genre_id = self.params['genre_id']
				if not genre_id: return
				data = function(genre_id, page_no)
				self.list = [i['id'] for i in data['results']]
				if data['page'] < data['total_pages']: self.new_page = {'new_page': string(data['page'] + 1), 'genre_id': genre_id}
			elif self.action == 'tmdb_tv_search':
				query = self.params['query']
				data = function(query, page_no)
				self.list = [i['id'] for i in data['results']]
				total_pages = data['total_pages']
				if total_pages > page_no: self.new_page = {'new_page': string(page_no + 1), 'query': query}
			elif self.action == 'trakt_tv_certifications':
				self.id_type = 'trakt_dict'
				data = function(self.params['certification'], page_no)
				self.list = [i['show']['ids'] for i in data]
				self.new_page = {'new_page': string(page_no + 1), 'certification': self.params['certification']}
			elif self.action == 'trakt_recommendations':
				self.id_type = 'trakt_dict'
				data = function('shows')
				self.list = [i['ids'] for i in data]
			elif self.action == 'trakt_tv_most_watched':
				self.id_type = 'trakt_dict'
				data = function(page_no)
				self.list = [i['show']['ids'] for i in data]
				self.new_page = {'new_page': string(page_no + 1)}
			if self.total_pages and not self.is_widget:
				url_params = {'mode': 'build_navigate_to_page', 'media_type': 'TV Shows', 'current_page': page_no, 'total_pages': self.total_pages, 'transfer_mode': mode,
							'transfer_action': self.action, 'query': params_get('search_name', ''), 'actor_id': params_get('actor_id', '')}
				self.add_dir(url_params, jumpto_str, item_jump, False)
			add_items(self.handle, self.worker())
			if self.new_page:
					self.new_page.update({'mode': mode, 'action': self.action, 'exit_list_params': self.exit_list_params})
					self.add_dir(self.new_page)
		except: pass
		set_content(self.handle, content_type)
		end_directory(self.handle, False if self.is_widget else None)
		set_view_mode('view.tvshows', content_type)

	def build_tvshow_content(self, item_position, _id):
		try:
			cm = []
			cm_append = cm.append
			meta, playcount, total_watched, total_unwatched = self.get_meta(_id)
			meta_get = meta.get
			if meta_get('blank_entry', False): return
			listitem = make_listitem()
			set_property = listitem.setProperty
			rootname, title, year, trailer = meta_get('rootname'), meta_get('title'), meta_get('year'), meta_get('trailer')
			tmdb_id, tvdb_id, imdb_id = meta_get('tmdb_id'), meta_get('tvdb_id'), meta_get('imdb_id')
			total_seasons, total_aired_eps = meta_get('total_seasons'), meta_get('total_aired_eps')
			poster = meta_get(self.poster_main) or meta_get(self.poster_backup) or poster_empty
			fanart = meta_get(self.fanart_main) or meta_get(self.fanart_backup) or fanart_empty
			options_params = build_url({'mode': 'options_menu_choice', 'content': 'tvshow', 'tmdb_id': tmdb_id})
			recommended_params = build_url({'mode': 'build_tvshow_list', 'action': 'tmdb_tv_recommendations', 'tmdb_id': tmdb_id})
			extras_params = build_url({'mode': 'extras_menu_choice', 'tmdb_id': tmdb_id, 'media_type': 'tvshow', 'is_widget': self.is_widget})
			random_params = build_url({'mode': 'random_choice', 'tmdb_id': tmdb_id, 'poster': poster})
			trakt_manager_params = build_url({'mode': 'trakt_manager_choice', 'tmdb_id': tmdb_id, 'imdb_id': imdb_id, 'tvdb_id': tvdb_id, 'media_type': 'tvshow'})
			fav_manager_params = build_url({'mode': 'favorites_choice', 'media_type': 'tvshow', 'tmdb_id': tmdb_id, 'title': title})
			if self.fanart_enabled: banner, clearart, clearlogo, landscape = meta_get('banner'), meta_get('clearart'), meta_get('clearlogo'), meta_get('landscape')
			else: banner, clearart, clearlogo, landscape = '', '', '', ''
			if self.all_episodes:
				if self.all_episodes == 1 and total_seasons > 1: url_params = build_url({'mode': 'build_season_list', 'tmdb_id': tmdb_id})
				else: url_params = build_url({'mode': 'build_episode_list', 'tmdb_id': tmdb_id, 'season': 'all'})
			else: url_params = build_url({'mode': 'build_season_list', 'tmdb_id': tmdb_id})
			if self.open_extras:
				cm_append((browse_str, container_update % url_params))
				url_params = extras_params
			else: cm_append((extras_str, run_plugin % extras_params))
			cm_append((options_str, run_plugin % options_params))
			cm_append((recomm_str, container_update % recommended_params))
			cm_append((random_str, run_plugin % random_params))
			cm_append((traktmanager_str, run_plugin % trakt_manager_params))
			cm_append((favmanager_str, run_plugin % fav_manager_params))
			if not playcount:
				watched_params = build_url({'mode': 'mark_as_watched_unwatched_tvshow', 'action': 'mark_as_watched', 'title': title, 'year': year,
													'tmdb_id': tmdb_id, 'imdb_id': imdb_id, 'tvdb_id': tvdb_id})
				cm_append((watched_str % self.watched_title, run_plugin % watched_params))
			elif self.hide_watched: return
			if total_watched:
				unwatched_params = build_url({'mode': 'mark_as_watched_unwatched_tvshow', 'action': 'mark_as_unwatched', 'title': title, 'year': year,
													'tmdb_id': tmdb_id, 'imdb_id': imdb_id, 'tvdb_id': tvdb_id})
				cm_append((unwatched_str % self.watched_title, run_plugin % unwatched_params))
			cm_append((exit_str, container_refresh % self.exit_list_params))
			listitem.setLabel(rootname if self.include_year_in_title else title)
			listitem.setContentLookup(False)
			listitem.addContextMenuItems(cm)
			listitem.setCast(meta_get('cast', []))
			listitem.setUniqueIDs({'imdb': imdb_id, 'tmdb': string(tmdb_id), 'tvdb': string(tvdb_id)})
			listitem.setArt({'poster': poster, 'fanart': fanart, 'icon': poster, 'banner': banner, 'clearart': clearart, 'clearlogo': clearlogo, 'landscape': landscape,
							'tvshow.clearart': clearart, 'tvshow.clearlogo': clearlogo, 'tvshow.landscape': landscape, 'tvshow.banner': banner})
			listitem.setInfo('video', remove_meta_keys(meta, dict_removals))
			set_property('watchedepisodes', string(total_watched))
			set_property('unwatchedepisodes', string(total_unwatched))
			set_property('totalepisodes', string(total_aired_eps))
			set_property('totalseasons', string(total_seasons))
			set_property('ezra_sort_order', string(item_position))
			if self.is_widget:
				set_property('ezra_widget', 'true')
				set_property('ezra_playcount', string(playcount))
				set_property('ezra_extras_menu_params', extras_params)
				set_property('ezra_options_menu_params', options_params)
				set_property('ezra_trakt_manager_params', trakt_manager_params)
				set_property('ezra_fav_manager_params', fav_manager_params)
				set_property('ezra_random_params', random_params)
			else: set_property('ezra_widget', 'false')
			self.append((url_params, listitem, self.is_folder))
		except: pass

	def get_meta(self, _id):
		meta = meta_function(self.id_type, _id, self.meta_user_info, self.current_date)
		if not meta: return
		playcount, overlay, total_watched, total_unwatched = get_watched_function(self.watched_info, string(meta['tmdb_id']), meta.get('total_aired_eps'))
		meta.update({'playcount': playcount, 'overlay': overlay})
		return meta, playcount, total_watched, total_unwatched

	def worker(self):
		if self.is_widget == 'unchecked': self.is_widget = external_browse()
		if not self.exit_list_params: self.exit_list_params = get_infolabel('Container.FolderPath')
		self.current_date = get_datetime_function()
		self.meta_user_info = metadata_user_info()
		self.watched_indicators = watched_indicators()
		self.watched_info = get_watched_info_function(self.watched_indicators)
		self.all_episodes = default_all_episodes()
		self.include_year_in_title = include_year_in_title('tvshow')
		self.open_extras = extras_open_action('tvshow')
		self.fanart_enabled = self.meta_user_info['extra_fanart_enabled']
		self.hide_watched = self.is_widget and self.meta_user_info['widget_hide_watched']
		self.watched_title = 'Trakt' if self.watched_indicators == 1 else 'Ezra'
		self.is_folder = False if self.open_extras else True
		self.poster_main, self.poster_backup, self.fanart_main, self.fanart_backup = get_art_provider()
		self.append = self.items.append
		threads = list(make_thread_list_enumerate(self.build_tvshow_content, self.list, Thread))
		[i.join() for i in threads]
		self.items.sort(key=lambda k: int(k[1].getProperty('ezra_sort_order')))
		return self.items

	def add_dir(self, url_params, list_name=nextpage_str, iconImage=item_next, isFolder=True):
		url = build_url(url_params)
		listitem = make_listitem()
		listitem.setLabel(list_name)
		set_property = listitem.setProperty
		listitem.setArt({'icon': iconImage, 'fanart': fanart_empty})
		if url_params['mode'] == 'build_navigate_to_page':
			set_property('SpecialSort', 'top')
			listitem.addContextMenuItems([(switchjump_str, run_plugin % build_url({'mode': 'toggle_jump_to'}))])
		else: set_property('SpecialSort', 'bottom')
		add_item(self.handle, url, listitem, isFolder)
