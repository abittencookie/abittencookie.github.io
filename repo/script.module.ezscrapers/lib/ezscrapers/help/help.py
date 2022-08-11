# -*- coding: utf-8 -*-
"""
	Ezscrapers Module
"""

from ezscrapers.modules.control import addonPath, addonVersion, joinPath
from ezscrapers.windows.textviewer import TextViewerXML


def get(file):
	ezscrapers_path = addonPath()
	ezscrapers_version = addonVersion()
	helpFile = joinPath(ezscrapers_path, 'lib', 'ezscrapers', 'help', file + '.txt')
	r = open(helpFile, 'r', encoding='utf-8', errors='ignore')
	text = r.read()
	r.close()
	heading = '[B]ezScrapers -  v%s - %s[/B]' % (ezscrapers_version, file)
	windows = TextViewerXML('textviewer.xml', ezscrapers_path, heading=heading, text=text)
	windows.run()
	del windows
