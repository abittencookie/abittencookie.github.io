# -*- coding: utf-8 -*-
from threading import Thread
from modules import kodi_utils
from modules.utils import make_thread_list
# logger = kodi_utils.logger

database = kodi_utils.database
delete_file = kodi_utils.delete_file
navigator_db = kodi_utils.navigator_db
watched_db = kodi_utils.watched_db
favorites_db = kodi_utils.favorites_db
views_db = kodi_utils.views_db
trakt_db = kodi_utils.trakt_db
maincache_db = kodi_utils.maincache_db
metacache_db = kodi_utils.metacache_db
debridcache_db = kodi_utils.debridcache_db
external_db = kodi_utils.external_db
databases_path = kodi_utils.databases_path
current_dbs = kodi_utils.current_dbs

def check_databases():
	if not kodi_utils.path_exists((databases_path)): kodi_utils.make_directory(databases_path)
	remove_old_caches()
	#Navigator
	dbcon = database.connect(navigator_db)
	dbcon.execute("""CREATE TABLE IF NOT EXISTS navigator
				(list_name text, list_type text, list_contents text, unique(list_name, list_type))""")
	dbcon.close()
	# Watched Status
	dbcon = database.connect(watched_db)
	dbcon.execute("""CREATE TABLE IF NOT EXISTS watched_status
					(db_type text, media_id text, season integer, episode integer, last_played text, title text, unique(db_type, media_id, season, episode))""")
	dbcon.execute("""CREATE TABLE IF NOT EXISTS progress
					(db_type text, media_id text, season integer, episode integer, resume_point text, curr_time text,
					last_played text, resume_id integer, title text, unique(db_type, media_id, season, episode))""")
	dbcon.close()
	# Favourites
	dbcon = database.connect(favorites_db)
	dbcon.execute("""CREATE TABLE IF NOT EXISTS favourites (db_type text, tmdb_id text, title text, unique (db_type, tmdb_id))""")
	dbcon.close()
	# Views
	dbcon = database.connect(views_db)
	dbcon.execute("""CREATE TABLE IF NOT EXISTS views (view_type text, view_id text, unique (view_type))""")
	dbcon.close()
	# Trakt
	dbcon = database.connect(trakt_db)
	dbcon.execute("""CREATE TABLE IF NOT EXISTS trakt_data (id text unique, data text)""")
	dbcon.execute("""CREATE TABLE IF NOT EXISTS watched_status
					(db_type text, media_id text, season integer, episode integer, last_played text, title text, unique(db_type, media_id, season, episode))""")
	dbcon.execute("""CREATE TABLE IF NOT EXISTS progress
					(db_type text, media_id text, season integer, episode integer, resume_point text, curr_time text,
					last_played text, resume_id integer, title text, unique(db_type, media_id, season, episode))""")
	dbcon.close()
	# Main Cache
	dbcon = database.connect(maincache_db)
	dbcon.execute("""CREATE TABLE IF NOT EXISTS maincache (id text unique, data text, expires integer)""")
	dbcon.close()
	# Meta Cache
	dbcon = database.connect(metacache_db)
	dbcon.execute("""CREATE TABLE IF NOT EXISTS metadata
					  (db_type text not null, tmdb_id text not null, imdb_id text, tvdb_id text, meta text, expires integer, unique (db_type, tmdb_id))""")
	dbcon.execute("""CREATE TABLE IF NOT EXISTS season_metadata (tmdb_id text not null unique, meta text, expires integer)""")
	dbcon.execute("""CREATE TABLE IF NOT EXISTS function_cache (string_id text not null, data text, expires integer)""")
	dbcon.close()
	# Debrid Cache
	dbcon = database.connect(debridcache_db)
	dbcon.execute("""CREATE TABLE IF NOT EXISTS debrid_data (hash text not null, debrid text not null, cached text, expires integer, unique (hash, debrid))""")
	dbcon.close()
	# External Providers Cache
	dbcon = database.connect(external_db)
	dbcon.execute("""CREATE TABLE IF NOT EXISTS results_data
					(provider text, db_type text, tmdb_id text, title text, year integer, season text, episode text, results text,
					expires integer, unique (provider, db_type, tmdb_id, title, year, season, episode))""")
	dbcon.close()

def remove_old_caches():
	files = kodi_utils.list_dirs(databases_path)[1]
	for item in files:
		if not item in current_dbs:
			try: delete_file(databases_path + item)
			except: pass

def clean_databases(current_time=None, database_check=True, silent=False):
	def _process(args):
		try:
			dbcon = database.connect(args[0], timeout=60.0)
			dbcur = dbcon.cursor()
			dbcur.execute('''PRAGMA synchronous = OFF''')
			dbcur.execute('''PRAGMA journal_mode = OFF''')
			dbcur.execute(args[1], (current_time,))
			dbcon.commit()
			dbcur.execute('VACUUM')
		except: pass
	if database_check: check_databases()
	if not current_time: current_time = get_current_time()
	command_base = 'DELETE from %s WHERE CAST(%s AS INT) <= ?'
	functions_list = ((external_db, command_base % ('results_data', 'expires')),
					(maincache_db, command_base % ('maincache', 'expires')),
					(metacache_db, command_base % ('metadata', 'expires')),
					(metacache_db, command_base % ('function_cache', 'expires')),
					(metacache_db, command_base % ('season_metadata', 'expires')),
					(debridcache_db, command_base % ('debrid_data', 'expires')))
	threads = list(make_thread_list(_process, functions_list, Thread))
	[i.join() for i in threads]
	limit_metacache_database()
	if not silent: kodi_utils.notification(32576, time=2000)

def limit_metacache_database(max_size=50):
	with kodi_utils.open_file(metacache_db) as f: s = f.size()
	size = round(float(s)/1048576, 1)
	if size < max_size: return
	dbcon = database.connect(metacache_db, timeout=60.0)
	dbcur = dbcon.cursor()
	dbcur.execute('''PRAGMA synchronous = OFF''')
	dbcur.execute('''PRAGMA journal_mode = OFF''')
	dbcur.execute('DELETE FROM metadata WHERE ROWID IN (SELECT ROWID FROM metadata ORDER BY ROWID DESC LIMIT -1 OFFSET 4000)')
	dbcur.execute('DELETE FROM function_cache WHERE ROWID IN (SELECT ROWID FROM function_cache ORDER BY ROWID DESC LIMIT -1 OFFSET 100)')
	dbcur.execute('DELETE FROM season_metadata WHERE ROWID IN (SELECT ROWID FROM season_metadata ORDER BY ROWID DESC LIMIT -1 OFFSET 100)')
	dbcon.commit()
	dbcon.execute('VACUUM')

def get_current_time():
	import time, datetime
	return int(time.mktime(datetime.datetime.now().timetuple()))