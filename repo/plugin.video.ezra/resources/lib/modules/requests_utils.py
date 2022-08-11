# -*- coding: utf-8 -*-
import requests
# from modules.kodi_utils import logger

def make_session(url='https://'):
	session = requests.Session()
	session.mount(url, requests.adapters.HTTPAdapter(pool_maxsize=100))
	return session	

def make_requests():
	return requests