import json
from sys import argv
from modules import settings
from modules.nav_utils import paginate_list
from modules.utils import sort_for_article
from modules.kodi_utils import notification, execute_builtin, select_dialog, confirm_dialog, database, favorites_db, local_string as ls
# from modules.kodi_utils import logger

class Favourites:
	def __init__(self, params):
		self.media_type = params.get('media_type')
		self.tmdb_id = params.get('tmdb_id')
		self.title = params.get('title')
		self.make_database_connection()
		self.set_PRAGMAS()

	def add_to_favourites(self):
		try:
			self.dbcur.execute("INSERT INTO favourites VALUES (?, ?, ?)", (self.media_type, str(self.tmdb_id), self.title))
			notification(32576, 3500)
		except: notification(32574, 3500)

	def remove_from_favourites(self):
		try:
			self.dbcur.execute("DELETE FROM favourites where db_type=? and tmdb_id=?", (self.media_type, str(self.tmdb_id)))
			execute_builtin('Container.Refresh')
			notification(32576, 3500)
		except: notification(32574, 3500)

	def get_favourites(self, media_type):
		self.dbcur.execute('''SELECT tmdb_id, title FROM favourites WHERE db_type=?''', (media_type,))
		result = self.dbcur.fetchall()
		result = [{'tmdb_id': str(i[0]), 'title': str(i[1])} for i in result]
		return result

	def clear_favourites(self):
		favorites = ls(32453)
		fl = [('%s %s' % (ls(32028), ls(32453)), 'movie'), ('%s %s' % (ls(32029), ls(32453)), 'tvshow')]
		list_items = [{'line1': item[0]} for item in fl]
		kwargs = {'items': json.dumps(list_items), 'heading': ls(32036), 'enumerate': 'false', 'multi_choice': 'false', 'multi_line': 'false'}
		self.media_type = select_dialog([item[1] for item in fl], **kwargs)
		if self.media_type == None: return
		if not confirm_dialog(): return
		self.dbcur.execute("DELETE FROM favourites WHERE db_type=?", (self.media_type,))
		self.dbcur.execute('VACUUM')
		notification(32576, 3000)

	def make_database_connection(self):
		self.dbcon = database.connect(favorites_db, timeout=40.0, isolation_level=None)

	def set_PRAGMAS(self):
		self.dbcur = self.dbcon.cursor()
		self.dbcur.execute('''PRAGMA synchronous = OFF''')
		self.dbcur.execute('''PRAGMA journal_mode = OFF''')

def retrieve_favourites(media_type, page_no, letter):
	paginate = settings.paginate()
	limit = settings.page_limit()
	data = Favourites({}).get_favourites(media_type)
	data = sort_for_article(data, 'title', settings.ignore_articles())
	original_list = [{'media_id': i['tmdb_id'], 'title': i['title']} for i in data]
	if paginate: final_list, total_pages = paginate_list(original_list, page_no, letter, limit)
	else: final_list, total_pages = original_list, 1
	return final_list, total_pages


