# -*- coding: utf-8 -*-
from threading import Thread
from modules import service_functions
from modules.settings_reader import make_settings_dict, get_setting
from modules.kodi_utils import set_property, clear_property, sleep, xbmc_monitor, logger

class EzraMonitor(xbmc_monitor):
	def __init__ (self):
		xbmc_monitor.__init__(self)
		logger('EZRA', 'Main Monitor Service Starting')
		logger('EZRA', 'Settings Monitor Service Starting')
		self.startUpServices()
	
	def startUpServices(self):
		threads = []
		functions = (service_functions.DatabaseMaintenance().run, service_functions.TraktMonitor().run)
		for item in functions: threads.append(Thread(target=item))
		while not self.abortRequested():
			try: service_functions.InitializeDatabases().run()
			except: pass
			try: service_functions.CheckSettingsFile().run()
			except: pass
			try: service_functions.SyncMyAccounts().run()
			except: pass
			[i.start() for i in threads]
			try: service_functions.ClearSubs().run()
			except: pass
			try: service_functions.ViewsSetWindowProperties().run()
			except: pass
			try: service_functions.AutoRun().run()
			except: pass
			try: service_functions.ReuseLanguageInvokerCheck().run()
			except: pass
			break

	def onScreensaverActivated(self):
		set_property('ezra_pause_services', 'true')

	def onScreensaverDeactivated(self):
		clear_property('ezra_pause_services')

	def onSettingsChanged(self):
		clear_property('ezra_settings')
		sleep(50)
		make_settings_dict()
		set_property('ezra_kodi_menu_cache', get_setting('kodi_menu_cache'))

	def onNotification(self, sender, method, data):
		if method == 'System.OnSleep': set_property('ezra_pause_services', 'true')
		elif method == 'System.OnWake': clear_property('ezra_pause_services')


EzraMonitor().waitForAbort()

logger('EZRA', 'Settings Monitor Service Finished')
logger('EZRA', 'Main Monitor Service Finished')
