# -*- coding: utf-8 -*-
import json
from sys import argv
from caches.navigator_cache import navigator_cache as nc
from modules import kodi_utils as k, settings as s
from modules.settings_reader import get_setting
# logger = k.logger

tp, ls, build_url, notification, addon, make_listitem, list_dirs = k.translate_path, k.local_string, k.build_url, k.notification, k.addon, k.make_listitem, k.list_dirs
add_item, set_content, end_directory, set_view_mode, add_items, set_sort_method = k.add_item, k.set_content, k.end_directory, k.set_view_mode, k.add_items, k.set_sort_method
download_directory, furk_active, easynews_active, source_folders_directory = s.download_directory, s.furk_active, s.easynews_active, s.source_folders_directory
get_shortcut_folders, currently_used_list, get_shortcut_folder_contents, wi = nc.get_shortcut_folders, nc.currently_used_list, nc.get_shortcut_folder_contents, s.watched_indicators
_in_str, mov_str, tv_str, edit_str, browse_str, add_menu_str, s_folder_str = ls(32484), ls(32028), ls(32029), ls(32705), ls(32706), ls(32730), ls(32731)
icon_directory, fanart = 'special://home/addons/plugin.video.ezra/resources/media/%s', tp('special://home/addons/plugin.video.ezra/fanart.png')
non_folder_items = ('get_search_term', 'build_popular_people')

class Navigator:
	def __init__(self, params):
		self.view = 'view.main'
		self.params = params
		self.params_get = self.params.get
		self.list_name = self.params_get('action', 'RootList')

	def main(self):
		self.build_main_lists()

	def downloads(self):
		dl_str, pr_str, im_str = ls(32107), ls(32485), ls(32798)
		n_ins, lst_ins = _in_str % (dl_str.upper(), '%s'), '%s %s' % ('%s', dl_str)
		mov_path, ep_path = download_directory('movie'), download_directory('episode')
		prem_path, im_path = download_directory('premium'), download_directory('image')
		self.AD({'mode': 'navigator.folder_navigator', 'folder_path': mov_path, 'list_name': lst_ins % mov_str}, n_ins % mov_str, 'movies.png')
		self.AD({'mode': 'navigator.folder_navigator', 'folder_path': ep_path, 'list_name': lst_ins % tv_str}, n_ins % tv_str, 'tv.png')
		self.AD({'mode': 'navigator.folder_navigator', 'folder_path': prem_path, 'list_name': lst_ins % pr_str}, n_ins % pr_str, 'premium.png')
		self.AD({'mode': 'browser_image', 'folder_path': im_path, 'list_name': lst_ins % im_str}, n_ins % im_str, 'people.png', False)
		self._end_directory()

	def discover_main(self):
		discover_str, his_str, help_str = ls(32451), ls(32486), ls(32487)
		movh_str, tvh_str = '%s %s' % (mov_str, his_str), '%s %s' % (tv_str, his_str)
		n_ins, lst_ins = _in_str % (discover_str.upper(), '%s'), '%s %s' % (discover_str, '%s')
		self.AD({'mode': 'discover.movie', 'media_type': 'movie', 'list_name': lst_ins % mov_str}, n_ins % mov_str, 'discover.png')
		self.AD({'mode': 'discover.tvshow', 'media_type': 'tvshow', 'list_name': lst_ins % tv_str}, n_ins % tv_str, 'discover.png')
		self.AD({'mode': 'discover.history', 'media_type': 'movie', 'list_name': lst_ins % movh_str}, n_ins % movh_str, 'discover.png')
		self.AD({'mode': 'discover.history', 'media_type': 'tvshow', 'list_name': lst_ins % tvh_str}, n_ins % tvh_str, 'discover.png')
		self.AD({'mode': 'discover.help', 'list_name': lst_ins % help_str}, n_ins % help_str, 'discover.png', False)
		self._end_directory()

	def premium(self):
		from modules.debrid import debrid_enabled
		n_ins = _in_str % (ls(32488).upper(), '%s')
		furk_str, easy_str, rd_str, pm_str, ad_str = ls(32069), ls(32070), ls(32054), ls(32061), ls(32063)
		furk, easynews = furk_active(), easynews_active()
		debrids = debrid_enabled()
		if furk: self.AD({'mode': 'navigator.furk', 'list_name': furk_str}, n_ins % furk_str, 'furk.png')
		if easynews: self.AD({'mode': 'navigator.easynews', 'list_name': easy_str}, n_ins % easy_str, 'easynews.png')
		if 'Real-Debrid' in debrids: self.AD({'mode': 'navigator.real_debrid', 'list_name': rd_str}, n_ins % rd_str, 'realdebrid.png')
		if 'Premiumize.me' in debrids: self.AD({'mode': 'navigator.premiumize', 'list_name': pm_str}, n_ins % pm_str, 'premiumize.png')
		if 'AllDebrid' in debrids: self.AD({'mode': 'navigator.alldebrid', 'list_name': ad_str}, n_ins % ad_str, 'alldebrid.png')
		self._end_directory()

	def furk(self):
		f_str, act_str, fl_str, vid_str, fl_str = ls(32069), ls(32489), ls(32490), ls(32491), ls(32493)
		se_str, his_str, acc_str, dl_str = ls(32450), ls(32486), ls(32494), ls(32107)
		n_ins, lst_ins = _in_str % (f_str.upper(), '%s %s'), (_in_str % (f_str, '%s %s')).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'search_history', 'action': 'furk_video', 'list_name': lst_ins % (se_str, '')}, n_ins % (se_str, ''), 'search.png')
		self.AD({'mode': 'furk.my_furk_files', 'list_type': 'file_get_video', 'list_name': lst_ins % (vid_str, fl_str)}, n_ins % (vid_str, fl_str), 'lists.png')
		self.AD({'mode': 'furk.my_furk_files', 'list_type': 'file_get_active', 'list_name': lst_ins % (act_str, dl_str)}, n_ins % (act_str, dl_str), 'lists.png')
		self.AD({'mode': 'furk.my_furk_files', 'list_type': 'file_get_failed', 'list_name': lst_ins % (fl_str, dl_str)}, n_ins % (fl_str, dl_str), 'lists.png')
		self.AD({'mode': 'furk.account_info', 'list_name': lst_ins % (acc_str, '')}, n_ins % (acc_str, ''), 'furk.png', False)
		self._end_directory()

	def easynews(self):
		easy_str, se_str, his_str, acc_str = ls(32070), ls(32450), ls(32486), ls(32494)
		lst_ins, n_ins = (_in_str % (easy_str, '%s')).replace('[B]', '').replace(': [/B]', ' '), _in_str % (easy_str.upper(), '%s')
		self.AD({'mode': 'search_history', 'action': 'easynews_video', 'list_name': lst_ins % se_str}, n_ins % se_str, 'search.png')
		self.AD({'mode': 'easynews.account_info', 'list_name': lst_ins % acc_str}, n_ins % acc_str, 'easynews.png', False)
		self._end_directory()

	def real_debrid(self):
		rd_str, acc_str, his_str, cloud_str = ls(32054), ls(32494), ls(32486), ls(32496)
		clca_str, n_ins, lst_ins = ls(32497) % rd_str, _in_str % (rd_str.upper(), '%s'), (_in_str % (rd_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'real_debrid.rd_torrent_cloud', 'list_name': lst_ins % cloud_str}, n_ins % cloud_str, 'realdebrid.png')
		self.AD({'mode': 'real_debrid.rd_downloads', 'list_name': lst_ins % his_str}, n_ins % his_str, 'realdebrid.png')
		self.AD({'mode': 'real_debrid.rd_account_info', 'list_name': lst_ins % acc_str}, n_ins % acc_str, 'realdebrid.png', False)
		self.AD({'mode': 'clear_cache', 'cache': 'rd_cloud', 'list_name': lst_ins % clca_str}, n_ins % clca_str, 'realdebrid.png', False)
		self._end_directory()

	def premiumize(self):
		pm_str, acc_str, his_str, cloud_str = ls(32061), ls(32494), ls(32486), ls(32496)
		clca_str, n_ins, lst_ins = ls(32497) % pm_str, _in_str % (pm_str.upper(), '%s'), (_in_str % (pm_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'premiumize.pm_torrent_cloud', 'list_name': lst_ins % cloud_str}, n_ins % cloud_str, 'premiumize.png')
		self.AD({'mode': 'premiumize.pm_transfers', 'list_name': lst_ins % his_str}, n_ins % his_str, 'premiumize.png')
		self.AD({'mode': 'premiumize.pm_account_info', 'list_name': lst_ins % acc_str}, n_ins % acc_str, 'premiumize.png', False)
		self.AD({'mode': 'clear_cache', 'cache': 'pm_cloud', 'list_name': lst_ins % clca_str}, n_ins % clca_str, 'premiumize.png', False)
		self._end_directory()

	def alldebrid(self):
		ad_str, acc_str, cloud_str = ls(32063), ls(32494), ls(32496)
		clca_str, n_ins, lst_ins = ls(32497) % ad_str, _in_str % (ad_str.upper(), '%s'), (_in_str % (ad_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'alldebrid.ad_torrent_cloud', 'list_name': lst_ins % cloud_str}, n_ins % cloud_str, 'alldebrid.png')
		self.AD({'mode': 'alldebrid.ad_account_info', 'list_name': lst_ins % acc_str}, n_ins % acc_str, 'alldebrid.png', False)
		self.AD({'mode': 'clear_cache', 'cache': 'ad_cloud', 'list_name': lst_ins % clca_str}, n_ins % clca_str, 'alldebrid.png', False)
		self._end_directory()

	def favourites(self):
		fav_str = ls(32453)
		n_ins, lst_ins = _in_str % (fav_str.upper(), '%s'), (_in_str % ('%s', fav_str)).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'build_movie_list', 'action': 'favourites_movies', 'list_name': lst_ins % mov_str}, n_ins % mov_str, 'movies.png')
		self.AD({'mode': 'build_tvshow_list', 'action': 'favourites_tvshows', 'list_name': lst_ins % tv_str}, n_ins % tv_str, 'tv.png')
		self._end_directory()

	def my_content(self):
		trakt_str, imdb_str, coll_str, wlist_str, ls_str = ls(32037), ls(32064), ls(32499), ls(32500), ls(32501)
		t_n_ins, t_lst_ins = _in_str % (trakt_str.upper(), '%s'), (_in_str % (trakt_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		i_n_ins, i_lst_ins = _in_str % (imdb_str.upper(), '%s'), (_in_str % (imdb_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		trakt_status = get_setting('trakt_user') not in ('', None)
		imdb_status = get_setting('imdb_user') not in ('', None)
		if trakt_status or imdb_status:
			if trakt_status:
				self.AD({'mode': 'navigator.trakt_collections', 'list_name': t_lst_ins % coll_str}, t_n_ins % coll_str, 'trakt.png')
				self.AD({'mode': 'navigator.trakt_watchlists', 'list_name': t_lst_ins % wlist_str}, t_n_ins % wlist_str, 'trakt.png')
				self.AD({'mode': 'navigator.trakt_lists', 'list_name': t_lst_ins % ls_str}, t_n_ins % ls_str, 'trakt.png')
			if imdb_status:
				self.AD({'mode': 'navigator.imdb_watchlists', 'list_name': i_lst_ins % wlist_str}, i_n_ins % wlist_str, 'imdb.png')
				self.AD({'mode': 'navigator.imdb_lists', 'list_name': i_lst_ins % ls_str}, i_n_ins % ls_str, 'imdb.png')
			self._end_directory()
		else: notification(33022)

	def trakt_collections(self):
		# use 'new_page' to pass the type of list to be processed when using 'trakt_collection_lists'...
		t_str, col_str = ls(32037), ls(32499)
		tcol_str = '%s %s' % (t_str, col_str)
		n_ins, lst_ins = _in_str % (tcol_str.upper(), '%s'), (_in_str % (tcol_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		mrec_str, mran_str = '%s %s' % (ls(32498), mov_str), '%s %s' % (ls(32504), mov_str)
		tvrec_str, tvran_str, ra_str = '%s %s' % (ls(32498), tv_str), '%s %s' % (ls(32504), tv_str), '%s %s' % (ls(32505), ls(32506))
		n_ins, lst_ins = _in_str % (col_str.upper(), '%s'), (_in_str % (col_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'build_movie_list', 'action': 'trakt_collection', 'list_name': lst_ins % mov_str}, n_ins % mov_str, 'trakt.png')
		self.AD({'mode': 'build_tvshow_list', 'action': 'trakt_collection', 'list_name': lst_ins % tv_str}, n_ins % tv_str, 'trakt.png')
		self.AD({'mode': 'build_movie_list', 'action': 'trakt_collection_lists', 'new_page': 'recent', 'list_name': lst_ins % mrec_str}, n_ins % mrec_str, 'trakt.png')
		self.AD({'mode': 'build_movie_list', 'action': 'trakt_collection_lists', 'new_page': 'random', 'list_name': lst_ins % mran_str}, n_ins % mran_str, 'trakt.png')
		self.AD({'mode': 'build_tvshow_list', 'action': 'trakt_collection_lists', 'new_page': 'recent', 'list_name': lst_ins % tvrec_str}, n_ins % tvrec_str, 'trakt.png')
		self.AD({'mode': 'build_tvshow_list', 'action': 'trakt_collection_lists', 'new_page': 'random', 'list_name': lst_ins % tvran_str}, n_ins % tvran_str, 'trakt.png')
		self.AD({'mode': 'build_my_calendar', 'recently_aired': 'true', 'list_name': lst_ins % ra_str}, n_ins % ra_str, 'trakt.png')
		self._end_directory()

	def trakt_watchlists(self):
		t_str, watchlist_str = ls(32037), ls(32500)
		trakt_watchlist_str = '%s %s' % (t_str, watchlist_str)
		n_ins, lst_ins = _in_str % (trakt_watchlist_str.upper(), '%s'), (_in_str % (trakt_watchlist_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'build_movie_list', 'action': 'trakt_watchlist', 'list_name': lst_ins % mov_str}, n_ins % mov_str, 'trakt.png')
		self.AD({'mode': 'build_tvshow_list', 'action': 'trakt_watchlist', 'list_name': lst_ins % tv_str}, n_ins % tv_str, 'trakt.png')
		self._end_directory()

	def trakt_lists(self):
		t_str, user_str, l_str, ml_str, ll_str, rec_str, cal_str = ls(32037), ls(32065), ls(32501), ls(32454), ls(32502), ls(32503), ls(32081)
		tu_str, pu_str = '%s %s %s' % (ls(32458), user_str, l_str), '%s %s %s' % (ls(32459), user_str, l_str)
		sea_str, n_ins, lst_ins = '%s %s' % (ls(32477), l_str), _in_str % (t_str.upper(), '%s'), (_in_str % (t_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'trakt.list.get_trakt_lists', 'list_type': 'my_lists', 'build_list': 'true', 'list_name': lst_ins % ml_str}, n_ins % ml_str, 'trakt.png')
		self.AD({'mode': 'trakt.list.get_trakt_lists', 'list_type': 'liked_lists', 'build_list': 'true', 'list_name': lst_ins % ll_str}, n_ins % ll_str, 'trakt.png')
		self.AD({'mode': 'navigator.trakt_recommendations', 'list_name': lst_ins % rec_str}, n_ins % rec_str, 'trakt.png')
		self.AD({'mode': 'build_my_calendar', 'list_name': lst_ins % cal_str}, n_ins % cal_str, 'trakt.png')
		self.AD({'mode': 'trakt.list.get_trakt_trending_popular_lists', 'list_type': 'trending', 'list_name': lst_ins % tu_str}, n_ins % tu_str, 'trakt.png')
		self.AD({'mode': 'trakt.list.get_trakt_trending_popular_lists', 'list_type': 'popular', 'list_name': lst_ins % pu_str}, n_ins % pu_str, 'trakt.png')
		self.AD({'mode': 'trakt.list.search_trakt_lists', 'list_name': lst_ins % sea_str}, n_ins % sea_str, 'trakt.png')
		self._end_directory()

	def trakt_recommendations(self):
		rec_str = ls(32503)
		n_ins, lst_ins = _in_str % (rec_str.upper(), '%s'), (_in_str % (rec_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'build_movie_list', 'action': 'trakt_recommendations', 'list_name': lst_ins % mov_str}, n_ins % mov_str, 'trakt.png')
		self.AD({'mode': 'build_tvshow_list', 'action': 'trakt_recommendations', 'list_name': lst_ins % tv_str}, n_ins % tv_str, 'trakt.png')
		self._end_directory()

	def imdb_watchlists(self):
		imdb_str, watchlist_str = ls(32064), ls(32500)
		imdb_watchlist_str = '%s %s' % (imdb_str, watchlist_str)
		n_ins, lst_ins = _in_str % (imdb_watchlist_str.upper(), '%s'), (_in_str % (imdb_watchlist_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'build_movie_list', 'action': 'imdb_watchlist', 'list_name': lst_ins % mov_str}, n_ins % mov_str, 'imdb.png')
		self.AD({'mode': 'build_tvshow_list', 'action': 'imdb_watchlist', 'list_name': lst_ins % tv_str}, n_ins % tv_str, 'imdb.png')
		self._end_directory()

	def imdb_lists(self):
		imdb_str, lists_str = ls(32064), ls(32501)
		imdb_lists_str = '%s %s' % (imdb_str, lists_str)
		n_ins, lst_ins = _in_str % (imdb_lists_str.upper(), '%s'), (_in_str % (imdb_lists_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'imdb_build_user_lists', 'media_type': 'movie', 'list_name': lst_ins % mov_str}, n_ins % mov_str, 'imdb.png')
		self.AD({'mode': 'imdb_build_user_lists', 'media_type': 'tvshow', 'list_name': lst_ins % tv_str}, n_ins % tv_str, 'imdb.png')
		self._end_directory()

	def search(self):
		search_str, people_str = ls(32450), ls(32507)
		search_str_upper = search_str.upper()
		kw_mov, kw_tv, coll_str = '%s %s (%s)' % (ls(32064), ls(32092), mov_str), '%s %s (%s)' % (ls(32064), ls(32092), tv_str), '%s %s (%s)' % (mov_str, ls(32499), ls(32068))
		self.AD({'mode': 'search_history', 'action': 'movie', 'list_name': '%s %s' % (search_str, mov_str)}, _in_str % (search_str_upper, mov_str), 'search_movie.png')
		self.AD({'mode': 'search_history', 'action': 'tvshow', 'list_name': '%s %s' % (search_str, tv_str)}, _in_str % (search_str_upper, tv_str), 'search_tv.png')
		self.AD({'mode': 'search_history', 'action': 'people', 'list_name': '%s %s' % (search_str, people_str)}, _in_str % (search_str_upper, people_str), 'search_people.png')
		self.AD({'mode': 'search_history', 'action': 'imdb_keyword_movie', 'list_name': '%s %s' % (search_str, kw_mov)}, _in_str % (search_str_upper, kw_mov), 'search_imdb.png')
		self.AD({'mode': 'search_history', 'action': 'imdb_keyword_tvshow', 'list_name': '%s %s' % (search_str, kw_tv)}, _in_str % (search_str_upper, kw_tv), 'search_imdb.png')
		self.AD({'mode': 'search_history', 'action': 'tmdb_collections', 'list_name': '%s %s' % (search_str, coll_str)}, _in_str % (search_str_upper, coll_str), 'search_tmdb.png')
		self._end_directory()

	def tools(self):
		tools_str, manager_str, changelog_str, ext_str, short_str, source_str = ls(32456), ls(32513), ls(32508), ls(32118), ls(32514), ls(32515)
		log_utils, tips_str, views_str = ls(32777), ls(32518), ls(32510)
		clean_str, lang_inv_str = ls(32512), ls(33017)
		changelog_log_viewer_str = '%s & %s' % (changelog_str, log_utils)
		shortcut_manager_str, source_manager_str = '%s %s' % (short_str, manager_str), '%s %s' % (source_str, manager_str)
		n_ins, lst_ins = _in_str % (tools_str.upper(), '%s'), (_in_str % (tools_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'navigator.log_utils', 'list_name': lst_ins % changelog_log_viewer_str}, n_ins % changelog_log_viewer_str, 'settings2.png')
		self.AD({'mode': 'navigator.tips', 'list_name': lst_ins % tips_str}, n_ins % tips_str, 'settings2.png')
		self.AD({'mode': 'navigator.set_view_modes', 'list_name': lst_ins % views_str}, n_ins % views_str, 'settings2.png')
		self.AD({'mode': 'navigator.clear_info', 'list_name': lst_ins % clean_str}, n_ins % clean_str, 'settings2.png')
		self.AD({'mode': 'navigator.shortcut_folders', 'list_name': lst_ins % shortcut_manager_str}, n_ins % shortcut_manager_str, 'settings2.png')
		self.AD({'mode': 'navigator.sources_folders', 'list_name': lst_ins % source_manager_str}, n_ins % source_manager_str, 'settings2.png')
		self.AD({'mode': 'toggle_language_invoker', 'list_name': lst_ins % lang_inv_str}, n_ins % lang_inv_str, 'settings2.png', False)
		self._end_directory()

	def settings(self):
		settings_str = ls(32247)
		ezra_str, ez_scr_str, myaccounts_str = ls(32036), ls(32522), ls(33025)
		n_ins, lst_ins = _in_str % (settings_str.upper(), '%s'), (_in_str % (settings_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		self.AD({'mode': 'open_settings', 'query': '0.0', 'list_name': lst_ins % ezra_str}, n_ins % ezra_str, 'settings.png', False)
		self.AD({'mode': 'external_settings', 'ext_addon': 'script.module.ezscrapers', 'list_name': lst_ins % ez_scr_str},
																				n_ins % ez_scr_str, 'settings.png', False)
		self.AD({'mode': 'external_settings', 'ext_addon': 'script.module.myaccounts', 'list_name': lst_ins % myaccounts_str},
																				n_ins % myaccounts_str, 'settings.png', False)
		self._end_directory()

	def clear_info(self):
		cache_str, clca_str, clean_str, all_str, settings_str, fav_str = ls(32524), ls(32497), ls(32526), ls(32525), ls(32247), ls(32453)
		clean_set_cache_str = '[B]%s:[/B] %s %s %s' % (clean_str.upper(), clean_str, ls(32247), ls(32524))
		clean_set_cache_str_list_name = '%s %s %s' % (clean_str, ls(32247), ls(32524))
		clean_databases_str = '[B]%s:[/B] %s %s' % (clean_str.upper(), clean_str, ls(32003))
		clean_databases_str_list_name = '%s %s' % (clean_str, ls(32003))
		clean_all_str = '[B]%s:[/B] %s %s %s' % (clean_str.upper(), clean_str, all_str, settings_str)
		clean_all_str_list_name, search_str = '%s %s %s' % (clean_str, all_str, settings_str), '%s %s' % (ls(32450), ls(32486))
		clear_all_str, clear_meta_str = clca_str % all_str, clca_str % ls(32527)
		clear_list_str, clear_trakt_str = clca_str % ls(32501), clca_str % ls(32037)
		clear_imdb_str, clint_str, clext_str = clca_str % ls(32064), clca_str % ls(32096), clca_str % ls(32118)
		clear_rd_str, clear_pm_str, clear_ad_str = clca_str % ls(32054), clca_str % ls(32061), clca_str % ls(32063)
		clear_fav_str, clear_search_str = clca_str % fav_str, clca_str % search_str
		n_ins, lst_ins = _in_str % (cache_str.upper(), '%s'), (_in_str % (cache_str, '%s')).replace('[B]', '').replace(': [/B]', ' ')
		clear_all_amble = '[B][I][COLOR=grey] (%s %s & %s)[/COLOR][/I][/B]' % (ls(32189), fav_str, search_str)
		clear_all = '[B]%s:[/B] %s' % (clear_all_str.upper(), clear_all_amble)
		self.AD({'mode': 'clean_settings', 'list_name': clean_all_str_list_name}, clean_all_str, 'settings2.png', False)
		self.AD({'mode': 'clear_settings_window_properties', 'list_name': clean_set_cache_str_list_name}, clean_set_cache_str, 'settings2.png', False)
		self.AD({'mode': 'clean_databases', 'list_name': clean_databases_str_list_name}, clean_databases_str, 'settings2.png', False)
		self.AD({'mode': 'clear_all_cache', 'list_name': clear_all_str}, clear_all, 'settings2.png', False)
		self.AD({'mode': 'clear_favourites', 'list_name': lst_ins % clear_fav_str}, n_ins % clear_fav_str, 'settings2.png', False)
		self.AD({'mode': 'clear_search_history', 'list_name': lst_ins % clear_search_str}, n_ins % clear_search_str, 'settings2.png', False)
		self.AD({'mode': 'clear_cache', 'cache': 'meta', 'list_name': lst_ins % clear_meta_str}, n_ins % clear_meta_str, 'settings2.png', False)
		self.AD({'mode': 'clear_cache', 'cache': 'list', 'list_name': lst_ins % clear_list_str}, n_ins % clear_list_str, 'settings2.png', False)
		self.AD({'mode': 'clear_cache', 'cache': 'trakt', 'list_name': lst_ins % clear_trakt_str}, n_ins % clear_trakt_str, 'settings2.png', False)
		self.AD({'mode': 'clear_cache', 'cache': 'imdb', 'list_name': lst_ins % clear_imdb_str}, n_ins % clear_imdb_str, 'settings2.png', False)
		self.AD({'mode': 'clear_cache', 'cache': 'internal_scrapers', 'list_name': lst_ins % clint_str}, n_ins % clint_str, 'settings2.png', False)
		self.AD({'mode': 'clear_cache', 'cache': 'external_scrapers', 'list_name': lst_ins % clint_str}, n_ins % clext_str, 'settings2.png', False)
		self.AD({'mode': 'clear_cache', 'cache': 'rd_cloud', 'list_name': lst_ins % clear_rd_str}, n_ins % clear_rd_str, 'settings2.png', False)
		self.AD({'mode': 'clear_cache', 'cache': 'pm_cloud', 'list_name': lst_ins % clear_pm_str}, n_ins % clear_pm_str, 'settings2.png', False)
		self.AD({'mode': 'clear_cache', 'cache': 'ad_cloud', 'list_name': lst_ins % clear_ad_str}, n_ins % clear_ad_str, 'settings2.png', False)
		self._end_directory()

	def set_view_modes(self):
		set_views_str, lists_str, root_str, movies_str = ls(32510), ls(32501), ls(32457), ls(32028)
		tvshows_str, season_str, episode_str = ls(32029), ls(32537), ls(32506)
		premium_files_str, ep_lists_str = ls(32485), '%s %s' % (episode_str, lists_str)
		n_ins = _in_str % (set_views_str.upper(), '%s')
		self.AD({'mode': 'choose_view', 'view_type': 'view.main', 'content': '', 'exclude_external': 'true'},n_ins % root_str, 'settings.png')
		self.AD({'mode': 'choose_view', 'view_type': 'view.movies', 'content': 'movies', 'exclude_external': 'true'},n_ins % movies_str, 'settings.png')
		self.AD({'mode': 'choose_view', 'view_type': 'view.tvshows', 'content': 'tvshows', 'exclude_external': 'true'},n_ins % tvshows_str, 'settings.png')
		self.AD({'mode': 'choose_view', 'view_type': 'view.seasons', 'content': 'seasons', 'exclude_external': 'true'},n_ins % season_str, 'settings.png')
		self.AD({'mode': 'choose_view', 'view_type': 'view.episodes', 'content': 'episodes', 'exclude_external': 'true'},n_ins % episode_str, 'settings.png')
		self.AD({'mode': 'choose_view', 'view_type': 'view.episode_lists', 'content': 'episodes','exclude_external': 'true'},n_ins % ep_lists_str, 'settings.png')
		self.AD({'mode': 'choose_view', 'view_type': 'view.premium', 'content': 'files', 'exclude_external': 'true'},n_ins % premium_files_str, 'settings.png')
		self._end_directory()

	def log_utils(self):
		log_path = 'special://home/addons/%s/changelog.txt'
		ezra_str, cl_str, fs_str, ma_str, lut_str, k_str = ls(32036), ls(32508), ls(32522), ls(33025), ls(32777), ls(32538)
		lv_str, lu_str = ls(32509), ls(32853)
		ezra_vstr = addon().getAddonInfo('version')
		sc_v, ma_v = addon('script.module.ezscrapers').getAddonInfo('version'), addon('script.module.myaccounts').getAddonInfo('version')
		mt_str, mh_str = tp(log_path % 'plugin.video.ezra/resources/text'), '[B]%s[/B]: %s  [I](v.%s)[/I]' % (cl_str.upper(), ezra_str, ezra_vstr)
		sct_str, mat_str = tp(log_path % 'script.module.ezscrapers'), tp(log_path % 'script.module.myaccounts')
		sch_str, mah_str = '[B]%s[/B]: %s  [I](v.%s)[/I]' % (cl_str.upper(), fs_str, sc_v), '[B]%s[/B]: %s  [I](v.%s)[/I]' % (cl_str.upper(), ma_str, ma_v)
		klv_h, klu_h, kl_loc = '[B]%s[/B]: %s %s' % (lut_str.upper(), k_str, lv_str), '[B]%s[/B]: %s' % (lut_str.upper(), lu_str), tp('special://logpath/kodi.log')
		self.AD({'mode': 'show_text', 'heading': mh_str, 'file': mt_str, 'exclude_external': 'true'}, mh_str, 'lists.png', False)
		self.AD({'mode': 'show_text', 'heading': sch_str, 'file': sct_str, 'exclude_external': 'true'}, sch_str, 'lists.png', False)
		self.AD({'mode': 'show_text', 'heading': mah_str, 'file': mat_str, 'exclude_external': 'true'}, mah_str, 'lists.png', False)
		self.AD({'mode': 'show_text', 'heading': klv_h, 'file': kl_loc, 'kodi_log': 'true', 'exclude_external': 'true'}, klv_h, 'lists.png', False)
		self.AD({'mode': 'upload_logfile', 'exclude_external': 'true'}, klu_h, 'lists.png', False)
		self._end_directory()

	def certifications(self):
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie': from modules.meta_lists import movie_certifications as certifications
		else: from modules.meta_lists import tvshow_certifications as certifications
		mode = 'build_movie_list' if menu_type == 'movie' else 'build_tvshow_list'
		action = 'tmdb_movies_certifications' if menu_type == 'movie' else 'trakt_tv_certifications'
		lst_ins = self.make_list_name(menu_type)
		for cert in certifications:
			list_name = '%s %s %s' % (lst_ins, cert.upper(), ls(32473))
			self.AD({'mode': mode, 'action': action, 'certification': cert, 'list_name': list_name}, cert.upper(), 'certifications.png')
		self._end_directory()

	def languages(self):
		from modules.meta_lists import languages
		menu_type = self.params_get('menu_type')
		mode = 'build_movie_list' if menu_type == 'movie' else 'build_tvshow_list'
		action = 'tmdb_movies_languages' if menu_type == 'movie' else 'tmdb_tv_languages'
		lst_ins = self.make_list_name(menu_type)
		for lang in languages:
			list_name = '%s %s %s' % (lst_ins, lang[0], ls(32471))
			self.AD({'mode': mode, 'action': action, 'language': lang[1], 'list_name': list_name}, lang[0], 'languages.png')
		self._end_directory()

	def years(self):
		from modules.meta_lists import years
		menu_type = self.params_get('menu_type')
		mode = 'build_movie_list' if menu_type == 'movie' else 'build_tvshow_list'
		action = 'tmdb_movies_year' if menu_type == 'movie' else 'tmdb_tv_year'
		lst_ins = self.make_list_name(menu_type)
		for i in years():
			list_name = '%s %s %s' % (lst_ins, str(i), ls(32460))
			self.AD({'mode': mode, 'action': action, 'year': str(i), 'list_name': list_name}, str(i), 'calender.png')
		self._end_directory()

	def genres(self):
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie':
			from modules.meta_lists import movie_genres as genre_list
			mode, action = 'build_movie_list', 'tmdb_movies_genres'
		else:
			from modules.meta_lists import tvshow_genres as genre_list
			mode, action = 'build_tvshow_list', 'tmdb_tv_genres'
		lst_ins = self.make_list_name(menu_type)
		self.AD({'mode': 'navigator.multiselect_genres', 'genre_list': json.dumps(genre_list), 'menu_type': menu_type, 'exclude_external': 'true'}, ls(32789), 'genres.png', False)
		for genre, value in sorted(genre_list.items()):
			list_name = '%s %s %s' % (lst_ins, genre, ls(32470))
			self.AD({'mode': mode, 'action': action, 'genre_id': value[0], 'list_name': list_name}, genre, value[1])
		self._end_directory()

	def multiselect_genres(self):
		def _builder():
			for genre, value in sorted(genre_list.items()):
				function_list_append(value[0])
				yield {'line1': genre, 'icon': tp(''.join([icon_directory, value[1]]))}
		menu_type, genre_list = self.params['menu_type'], self.params['genre_list']
		function_list = []
		function_list_append = function_list.append
		icon_directory = 'special://home/addons/plugin.video.ezra/resources/media/'
		genre_list = json.loads(genre_list)
		list_items = list(_builder())
		kwargs = {'items': json.dumps(list_items), 'heading': ls(32847), 'enumerate': 'false', 'multi_choice': 'true', 'multi_line': 'false'}
		genre_ids = k.select_dialog(function_list, **kwargs)
		if genre_ids == None: return
		genre_id = ','.join(genre_ids)
		if menu_type == 'movie': url = {'mode': 'build_movie_list', 'action': 'tmdb_movies_genres', 'genre_id': genre_id}
		else: url = {'mode': 'build_tvshow_list', 'action': 'tmdb_tv_genres', 'genre_id': genre_id}
		return k.execute_builtin('Container.Update(%s)' % build_url(url))

	def networks(self):
		from modules.meta_lists import networks
		lst_ins = self.make_list_name(self.params_get('menu_type'))
		for item in sorted(networks, key=lambda k: k['name']):
			list_name = '%s %s %s' % (lst_ins, item['name'], ls(32480))
			self.AD({'mode': 'build_tvshow_list', 'action': 'tmdb_tv_networks', 'network_id': item['id'], 'list_name': list_name}, item['name'], item['logo'])
		self._end_directory()

	def folder_navigator(self):
		import os
		from modules.utils import clean_file_name, normalize
		def _process():
			for tup in items:
				try:
					item = tup[0]
					url = os.path.join(folder_path, item)
					listitem = make_listitem()
					listitem.setLabel(clean_file_name(normalize(item)))
					listitem.setArt({'fanart': fanart})
					yield (url, listitem, tup[1])
				except: pass
		folder_path = self.params_get('folder_path')
		sources_folders = self.params_get('sources_folders', None)
		dirs, files = list_dirs(folder_path)
		items = [(i, True) for i in dirs] + [(i, False) for i in files]
		item_list = list(_process())
		__handle__ = int(argv[1])
		add_items(__handle__, item_list)
		set_sort_method(__handle__, 'files')
		self._end_directory()
	
	def sources_folders(self):
		name_str = '[B]%s (%s): %s[/B]\n     [I]%s[/I]'
		for source in ('folder1', 'folder2', 'folder3', 'folder4', 'folder5'):
			for media_type in ('movie', 'tvshow'):
				folder_path = source_folders_directory(media_type, source)
				if not folder_path: continue
				name = name_str % (source.upper(), self.make_list_name(media_type).upper(), get_setting('%s.display_name' % source).upper(), folder_path)
				self.AD({'mode': 'navigator.folder_navigator','sources_folders': 'True', 'folder_path': folder_path, 'list_name': name}, name, 'most__collected.png')
		self._end_directory()

	def tips(self):
		tips_location = 'special://home/addons/plugin.video.ezra/resources/text/tips'
		files = sorted(list_dirs(tips_location)[1])
		tips_location = tips_location + '/%s'
		help_str, new_str, spotlight_str = ls(32487).upper(), ls(32857).upper(), ls(32858).upper()
		n_ins = '%s: %s'  % (ls(32546).upper(), '%s')
		tips_list = []
		append = tips_list.append
		for item in files:
			tip = item.replace('.txt', '')[4:]
			if '!!' in tip:
				if '!!HELP!!' in tip: tip, sort_order = tip.replace('!!HELP!!', '[COLOR crimson]%s!!![/COLOR] ' % help_str), 0
				elif '!!NEW!!' in tip: tip, sort_order = tip.replace('!!NEW!!', '[COLOR chartreuse]%s!![/COLOR] ' % new_str), 1
				else: tip, sort_order = tip.replace('!!SPOTLIGHT!!', '[COLOR orange]%s![/COLOR] ' % spotlight_str), 2 #orange
			else: sort_order = 3
			tip_name = n_ins % tip
			action = {'mode': 'show_text', 'heading': tip, 'file': tp(tips_location % item)}
			append((action, tip_name, sort_order))
		item_list = sorted(tips_list, key=lambda x: x[2])
		for c, i in enumerate(item_list, 1): self.AD(i[0], '%02d. %s' % (c, i[1]), 'information.png', False)
		self._end_directory()

	def because_you_watched(self):
		from modules.watched_status import get_watched_info_movie, get_watched_info_tv
		def _convert_ezra_watched_episodes_info(watched_indicators):
			seen = set()
			_watched = get_watched_info_tv(watched_indicators)
			_watched.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
			return [(i[0], i[3], i[4], [(i[1], i[2])]) for i in _watched if not (i[0] in seen or seen.add(i[0]))]
		watched_indicators = wi()
		media_type = self.params_get('menu_type')
		function = get_watched_info_movie if media_type == 'movie' else _convert_ezra_watched_episodes_info
		mode = 'build_movie_list' if media_type == 'movie' else 'build_tvshow_list'
		action = 'tmdb_movies_recommendations' if media_type == 'movie' else 'tmdb_tv_recommendations'
		recently_watched = function(watched_indicators)
		recently_watched = sorted(recently_watched, key=lambda k: k[2], reverse=True)
		because_ins = '[I]%s[/I]  [B]%s[/B]' % (ls(32474), '%s')
		for item in recently_watched:
			tmdb_id = item[0]
			if media_type == 'movie': name = because_ins % item[1]
			else:
				season, episode = item[3][-1]
				name = because_ins % '%s - %sx%s' % (item[1], season, episode)
			self.AD({'mode': mode, 'action': action, 'tmdb_id': tmdb_id, 'exclude_external': 'true'}, name, 'because_you_watched.png')
		self._end_directory()

	def make_list_name(self, menu_type):
		return menu_type.replace('tvshow', tv_str).replace('movie', mov_str)
	
	def shortcut_folders(self):
		def _make_icon(chosen_icon):
			return tp(icon_directory % chosen_icon)
		def _make_new_item():
			icon = _make_icon('new.png')
			display_name = '[I]%s...[/I]' % ls(32702)
			url_params = {'mode': 'menu_editor.shortcut_folder_make'}
			url = build_url(url_params)
			listitem = make_listitem()
			listitem.setLabel(display_name)
			listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon})
			add_item(__handle__, url, listitem, False)
		def _builder():
			short_str, delete_str = ls(32514), ls(32703)
			icon = tp(icon_directory % 'genre_foreign.png')
			for i in folders:
				try:
					cm = []
					cm_append = cm.append
					name = i[0]
					display_name = '[B]%s : [/B] %s ' % (short_str.upper(), i[0])
					contents = eval(i[1])
					url_params = {'mode': 'navigator.build_shortcut_folder_list', 'name': name, 'iconImage': 'genre_foreign.png',
								'shortcut_folder': 'True', 'external_list_item': 'True'}
					url = build_url(url_params)
					listitem = make_listitem()
					listitem.setLabel(display_name)
					listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon})
					cm_append((delete_str,'RunPlugin(%s)'% build_url({'mode': 'menu_editor.shortcut_folder_delete', 'list_name': name})))
					listitem.addContextMenuItems(cm)
					yield (url, listitem, True)
				except: pass
		__handle__ = int(argv[1])
		_make_new_item()
		folders = get_shortcut_folders()
		if folders: add_items(__handle__, list(_builder()))
		self._end_directory()

	def build_main_lists(self):
		def _process():
			for item_position, item in enumerate(list_items):
				try:
					cm = []
					cm_append = cm.append
					item_get = item.get
					icon = item_get('iconImage') if item_get('network_id', '') != '' else tp(icon_directory % item_get('iconImage'))
					cm_append((edit_str,'RunPlugin(%s)' % build_url({'mode': 'menu_editor.edit_menu', 'active_list': self.list_name, 'position': item_position})))
					cm_append((browse_str,'RunPlugin(%s)' % build_url({'mode': 'menu_editor.browse', 'active_list': self.list_name})))
					listitem = make_listitem()
					listitem.setLabel(ls(item_get('name', '')))
					listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon})
					listitem.addContextMenuItems(cm)
					yield (build_url(item), listitem, item_get('mode', '') not in non_folder_items)
				except: pass
		list_items = currently_used_list(self.list_name)
		__handle__ = int(argv[1])
		add_items(__handle__, list(_process()))
		self._end_directory()
	
	def build_shortcut_folder_list(self):
		def _process():
			for item_position, item in enumerate(contents):
				try:
					cm = []
					is_folder = item['mode'] not in non_folder_items
					item_get = item.get
					name = item_get('name', 'Error: No Name')
					icon = item_get('iconImage') if item_get('network_id', '') != '' else tp(icon_directory % item_get('iconImage'))
					url = build_url(item)
					cm.append((ls(32705),'RunPlugin(%s)' % build_url(
						{'mode': 'menu_editor.edit_menu_shortcut_folder', 'active_list': list_name, 'position': item_position})))
					listitem = make_listitem()
					listitem.setLabel(name)
					listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon})
					listitem.addContextMenuItems(cm)
					yield (url, listitem, is_folder)
				except: pass
		__handle__ = int(argv[1])
		list_name = self.params_get('name')
		contents = get_shortcut_folder_contents(list_name)
		add_items(__handle__, list(_process()))
		self._end_directory()

	def AD(self, url_params, list_name, iconImage='DefaultFolder.png', isFolder=True):
		cm = []
		cm_append = cm.append
		icon = iconImage if 'network_id' in url_params else tp(icon_directory % iconImage)
		url_params['iconImage'] = icon
		url = build_url(url_params)
		listitem = make_listitem()
		listitem.setLabel(list_name)
		listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon, 'landscape': icon})
		if not 'exclude_external' in url_params:
			list_name = url_params['list_name'] if 'list_name' in url_params else self.list_name
			cm_append((add_menu_str,'RunPlugin(%s)'% build_url({'mode': 'menu_editor.add_external', 'name': list_name, 'iconImage': iconImage})))
			cm_append((s_folder_str,'RunPlugin(%s)' % build_url({'mode': 'menu_editor.shortcut_folder_add_item', 'name': list_name, 'iconImage': iconImage})))
			listitem.addContextMenuItems(cm)
		add_item(int(argv[1]), url, listitem, isFolder)

	def _end_directory(self):
		__handle__ = int(argv[1])
		set_content(__handle__, '')
		end_directory(__handle__)
		set_view_mode(self.view, '')


