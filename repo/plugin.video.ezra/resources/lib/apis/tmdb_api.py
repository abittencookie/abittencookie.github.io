# -*- coding: utf-8 -*-
from caches.main_cache import cache_object
from modules.settings import tmdb_api_key, get_language
from modules.requests_utils import make_session
# from modules.kodi_utils import logger

EXPIRY_4_HOURS, EXPIRY_2_DAYS, EXPIRY_1_WEEK, EXPIRY_1_MONTH = 4, 48, 168, 672
base_url = 'https://api.themoviedb.org/3'
timeout = 20.0
session = make_session(base_url)

def tmdb_keyword_id(query):
	string = 'tmdb_keyword_id_%s' % query
	url = '%s/search/keyword?api_key=%s&query=%s' % (base_url, tmdb_api_key(), query)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_company_id(query):
	string = 'tmdb_company_id_%s' % query
	url = '%s/search/company?api_key=%s&query=%s' % (base_url, tmdb_api_key(), query)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_media_images(media_type, tmdb_id):
	if media_type == 'movies': media_type = 'movie'
	string = 'tmdb_media_images_%s_%s' % (media_type, tmdb_id)
	url = '%s/%s/%s/images?api_key=%s' % (base_url, media_type, tmdb_id, tmdb_api_key())
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_media_videos(media_type, tmdb_id):
	if media_type == 'movies': media_type = 'movie'
	if media_type in ('tvshow', 'tvshows'): media_type = 'tv'
	string = 'tmdb_media_videos_%s_%s' % (media_type, tmdb_id)
	url = '%s/%s/%s/videos?api_key=%s' % (base_url, media_type, tmdb_id, tmdb_api_key())
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_movies_discover(query, page_no):
	string = query % page_no
	url = query % page_no
	return cache_object(get_tmdb, string, url)

def tmdb_movies_collection(collection_id):
	string = 'tmdb_movies_collection_%s' % collection_id
	url = '%s/collection/%s?api_key=%s&language=en' % (base_url, collection_id, tmdb_api_key())
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_movies_title_year(title, year=None):
	if year:
		string = 'tmdb_movies_title_year_%s_%s' % (title, year)
		url = '%s/search/movie?api_key=%s&language=en&query=%s&year=%s' % (base_url, tmdb_api_key(), title, year)
	else:
		string = 'tmdb_movies_title_year_%s' % title
		url = '%s/search/movie?api_key=%s&language=en&query=%s' % (base_url, tmdb_api_key(), title)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_MONTH)

def tmdb_movies_popular(page_no):
	string = 'tmdb_movies_popular_%s' % page_no
	url = '%s/movie/popular?api_key=%s&language=en&with_original_language=en&page=%s' % (base_url, tmdb_api_key(), page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_blockbusters(page_no):
	string = 'tmdb_movies_blockbusters_%s' % page_no
	url = '%s/discover/movie?api_key=%s&language=en&with_original_language=en&sort_by=revenue.desc&page=%s' % (base_url, tmdb_api_key(), page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_in_theaters(page_no):
	string = 'tmdb_movies_in_theaters_%s' % page_no
	url = '%s/movie/now_playing?api_key=%s&language=en&with_original_language=en&page=%s' % (base_url, tmdb_api_key(), page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_premieres(page_no):
	current_date, previous_date = get_dates(31, reverse=True)
	string = 'tmdb_movies_premieres_%s' % page_no
	url = '%s/discover/movie?api_key=%s&language=en&with_original_language=en&release_date.gte=%s&release_date.lte=%s&with_release_type=1|3|2&page=%s' \
							% (base_url, tmdb_api_key(), previous_date, current_date, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_latest_releases(page_no):
	current_date, previous_date = get_dates(31, reverse=True)
	string = 'tmdb_movies_latest_releases_%s' % page_no
	url = '%s/discover/movie?api_key=%s&language=en&with_original_language=en&release_date.gte=%s&release_date.lte=%s&with_release_type=4|5&page=%s' \
							% (base_url, tmdb_api_key(), previous_date, current_date, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_upcoming(page_no):
	current_date, future_date = get_dates(31, reverse=False)
	string = 'tmdb_movies_upcoming_%s' % page_no
	url = '%s/discover/movie?api_key=%s&language=en&with_original_language=en&release_date.gte=%s&release_date.lte=%s&with_release_type=3|2|1&page=%s' \
							% (base_url, tmdb_api_key(), current_date, future_date, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_genres(genre_id, page_no):
	string = 'tmdb_movies_genres_%s_%s' % (genre_id, page_no)
	url = '%s/discover/movie?api_key=%s&with_genres=%s&language=en&with_original_language=en&sort_by=popularity.desc&page=%s' % (base_url, tmdb_api_key(), genre_id, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_languages(language, page_no):
	string = 'tmdb_movies_languages_%s_%s' % (language, page_no)
	url = '%s/discover/movie?api_key=%s&language=en&sort_by=popularity.desc&with_original_language=%s&page=%s' % (base_url, tmdb_api_key(), language, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_certifications(certification, page_no):
	string = 'tmdb_movies_certifications_%s_%s' % (certification, page_no)
	url = '%s/discover/movie?api_key=%s&language=en&with_original_language=en&sort_by=popularity.desc&certification_country=US&certification=%s&page=%s' \
							% (base_url, tmdb_api_key(), certification, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_year(year, page_no):
	string = 'tmdb_movies_year_%s_%s' % (year, page_no)
	url = '%s/discover/movie?api_key=%s&language=en&with_original_language=en&sort_by=popularity.desc&certification_country=US&primary_release_year=%s&page=%s' \
							% (base_url, tmdb_api_key(), year, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_networks(network_id, page_no):
	string = 'tmdb_movies_networks_%s_%s' % (network_id, page_no)
	url = '%s/discover/movie?api_key=%s&language=en&with_original_language=en&sort_by=popularity.desc&certification_country=US&with_companies=%s&page=%s' \
							% (base_url, tmdb_api_key(), network_id, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_similar(tmdb_id, page_no):
	string = 'tmdb_movies_similar_%s_%s' % (tmdb_id, page_no)
	url = '%s/movie/%s/similar?api_key=%s&language=en&page=%s' % (base_url, tmdb_id, tmdb_api_key(), page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_recommendations(tmdb_id, page_no):
	string = 'tmdb_movies_recommendations_%s_%s' % (tmdb_id, page_no)
	url = '%s/movie/%s/recommendations?api_key=%s&language=en&page=%s' % (base_url, tmdb_id, tmdb_api_key(), page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_movies_search(query, page_no):
	string = 'tmdb_movies_search_%s_%s' % (query, page_no)
	url = '%s/search/movie?api_key=%s&language=en&query=%s&page=%s' % (base_url, tmdb_api_key(), query, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_4_HOURS)

def tmdb_movies_search_collections(query, page_no):
	string = 'tmdb_movies_search_collections_%s_%s' % (query, page_no)
	url = '%s/search/collection?api_key=%s&language=en&query=%s&page=%s' % (base_url, tmdb_api_key(), query, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_tv_discover(query, page_no):
	string = url = query % page_no
	return cache_object(get_tmdb, string, url)

def tmdb_tv_title_year(title, year=None):
	if year:
		string = 'tmdb_tv_title_year_%s_%s' % (title, year)
		url = '%s/search/tv?api_key=%s&query=%s&first_air_date_year=%s&language=en' % (base_url, tmdb_api_key(), title, year)
	else:
		string = 'tmdb_tv_title_year_%s' % title
		url = '%s/search/tv?api_key=%s&query=%s&language=en' % (base_url, tmdb_api_key(), title)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_MONTH)

def tmdb_tv_popular(page_no):
	string = 'tmdb_tv_popular_%s' % page_no
	url = '%s/tv/popular?api_key=%s&language=en&with_original_language=en&page=%s' % (base_url, tmdb_api_key(), page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_tv_premieres(page_no):
	current_date, previous_date = get_dates(31, reverse=True)
	string = 'tmdb_tv_premieres_%s' % page_no
	url = '%s/discover/tv?api_key=%s&language=en&with_original_language=en&sort_by=popularity.desc&first_air_date.gte=%s&first_air_date.lte=%s&page=%s' \
							% (base_url, tmdb_api_key(), previous_date, current_date, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_tv_airing_today(page_no):
	string = 'tmdb_tv_airing_today_%s' % page_no
	url = '%s/tv/airing_today?api_key=%s&language=en&with_original_language=en&page=%s' % (base_url, tmdb_api_key(), page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_tv_on_the_air(page_no):
	string = 'tmdb_tv_on_the_air_%s' % page_no
	url = '%s/tv/on_the_air?api_key=%s&language=en&with_original_language=en&page=%s' % (base_url, tmdb_api_key(), page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_tv_upcoming(page_no):
	current_date, future_date = get_dates(31, reverse=False)
	string = 'tmdb_tv_upcoming_%s' % page_no
	url = '%s/discover/tv?api_key=%s&language=en&sort_by=popularity.desc&first_air_date.gte=%s&first_air_date.lte=%s&page=%s' \
							% (base_url, tmdb_api_key(), current_date, future_date, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_tv_genres(genre_id, page_no):
	string = 'tmdb_tv_genres_%s_%s' % (genre_id, page_no)
	url = '%s/discover/tv?api_key=%s&with_genres=%s&sort_by=popularity.desc&include_null_first_air_dates=false&page=%s' \
							% (base_url, tmdb_api_key(), genre_id, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_tv_languages(language, page_no):
	string = 'tmdb_tv_languages_%s_%s' % (language, page_no)
	url = '%s/discover/tv?api_key=%s&language=en&sort_by=popularity.desc&include_null_first_air_dates=false&with_original_language=%s&page=%s' \
							% (base_url, tmdb_api_key(), language, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_tv_year(year, page_no):
	string = 'tmdb_tv_year_%s_%s' % (year, page_no)
	url = '%s/discover/tv?api_key=%s&language=en&with_original_language=en&sort_by=popularity.desc&include_null_first_air_dates=false&first_air_date_year=%s&page=%s' \
							% (base_url, tmdb_api_key(), year, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_tv_networks(network_id, page_no):
	string = 'tmdb_tv_networks_%s_%s' % (network_id, page_no)
	url = '%s/discover/tv?api_key=%s&language=en&with_original_language=en&sort_by=popularity.desc&include_null_first_air_dates=false&with_networks=%s&page=%s' \
							% (base_url, tmdb_api_key(), network_id, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_tv_similar(tmdb_id, page_no):
	string = 'tmdb_tv_similar_%s_%s' % (tmdb_id, page_no)
	url = '%s/tv/%s/similar?api_key=%s&language=en&page=%s' % (base_url, tmdb_id, tmdb_api_key(), page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_tv_recommendations(tmdb_id, page_no):
	string = 'tmdb_tv_recommendations_%s_%s' % (tmdb_id, page_no)
	url = '%s/tv/%s/recommendations?api_key=%s&language=en&page=%s' % (base_url, tmdb_id, tmdb_api_key(), page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_2_DAYS)

def tmdb_tv_search(query, page_no):
	string = 'tmdb_tv_search_%s_%s' % (query, page_no)
	url = '%s/search/tv?api_key=%s&language=en&query=%s&page=%s' % (base_url, tmdb_api_key(), query, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_4_HOURS)

def tmdb_popular_people(page_no):
	string = 'tmdb_popular_people_%s' % page_no
	url = '%s/person/popular?api_key=%s&language=en&page=%s' % (base_url, tmdb_api_key(), page_no)
	return cache_object(get_tmdb, string, url)

def tmdb_people_full_info(actor_id, language=None):
	if not language: language = get_language()
	string = 'tmdb_people_full_info_%s_%s' % (actor_id, language)
	url = '%s/person/%s?api_key=%s&language=%s&append_to_response=external_ids,combined_credits,images,tagged_images' % (base_url, actor_id, tmdb_api_key(), language)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_people_info(query):
	string = 'tmdb_people_info_%s' % query
	url = '%s/search/person?api_key=%s&language=en&query=%s' % (base_url, tmdb_api_key(), query)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_4_HOURS)['results']

def get_dates(days, reverse=True):
	import datetime
	current_date = datetime.date.today()
	if reverse: new_date = (current_date - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
	else: new_date = (current_date + datetime.timedelta(days=days)).strftime('%Y-%m-%d')
	return str(current_date), new_date

def get_tmdb(url):
	try: response = session.get(url, timeout=timeout)
	except: response = session.get(url, verify=False, timeout=timeout)
	return response
