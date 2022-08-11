# -*- coding: utf-8 -*-
from sys import argv
from apis.imdb_api import imdb_user_lists, imdb_keyword_search
from modules import kodi_utils
# from modules.kodi_utils import logger

ls = kodi_utils.local_string
build_url = kodi_utils.build_url
make_listitem = kodi_utils.make_listitem
default_imdb_icon = kodi_utils.translate_path('special://home/addons/plugin.video.ezra/resources/media/imdb.png')
fanart = kodi_utils.translate_path('special://home/addons/plugin.video.ezra/fanart.png')

def imdb_build_user_lists(media_type):
	def _builder():
		for item in user_lists:
			try:
				cm = []
				cm_append = cm.append
				url = build_url({'mode': mode, 'action': 'imdb_user_list_contents', 'list_id': item['list_id']})
				listitem = make_listitem()
				listitem.setLabel(item['title'])
				listitem.setArt({'icon': default_imdb_icon, 'poster': default_imdb_icon, 'thumb': default_imdb_icon, 'fanart': fanart, 'banner': default_imdb_icon})
				cm_append((ls(32730),'RunPlugin(%s)' % build_url({'mode': 'menu_editor.add_external', 'name': item['title'], 'iconImage': 'imdb.png'})))
				cm_append((ls(32731),'RunPlugin(%s)' % build_url({'mode': 'menu_editor.shortcut_folder_add_item', 'name': item['title'], 'iconImage': 'imdb.png'})))
				listitem.addContextMenuItems(cm)
				yield (url, listitem, True)
			except: pass
	__handle__ = int(argv[1])
	user_lists = imdb_user_lists(media_type)
	mode = 'build_%s_list' % media_type
	kodi_utils.add_items(__handle__, list(_builder()))
	kodi_utils.set_content(__handle__, 'files')
	kodi_utils.end_directory(__handle__)
	kodi_utils.set_view_mode('view.main')

def imdb_build_keyword_results(media_type, query):
	def _builder():
		for count, item in enumerate(results, 1):
			cm = []
			cm_append = cm.append
			keyword = item[0]
			listings = item[1]
			url_params = {'mode': mode, 'action': 'imdb_keywords_list_contents', 'list_id': keyword.lower(), 'iconImage': 'imdb.png'}
			url = build_url(url_params)
			listitem = make_listitem()
			listitem.setLabel('%02d | [B]%s[/B] [I]%s[/I]' % (count, keyword.upper(), listings))
			listitem.setArt({'icon': default_imdb_icon, 'poster': default_imdb_icon, 'thumb': default_imdb_icon, 'fanart': fanart, 'banner': default_imdb_icon})
			cm_append((ls(32730),'RunPlugin(%s)' % build_url({'mode': 'menu_editor.add_external', 'name': '%s (IMDb)' % keyword.upper(), 'iconImage': 'imdb.png'})))
			cm_append((ls(32731),'RunPlugin(%s)' % build_url({'mode': 'menu_editor.shortcut_folder_add_item', 'name': '%s (IMDb)' % keyword.upper(), 'iconImage': 'imdb.png'})))
			listitem.addContextMenuItems(cm)
			yield (url, listitem, True)
	__handle__ = int(argv[1])
	results = imdb_keyword_search(query)
	if not results: return
	mode = 'build_%s_list' % media_type
	kodi_utils.add_items(__handle__, list(_builder()))
	kodi_utils.set_content(__handle__, 'files')
	kodi_utils.end_directory(__handle__)
	kodi_utils.set_view_mode('view.main')




