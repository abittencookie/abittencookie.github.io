# -*- coding: utf-8 -*-
"""
	Ezscrapers Module
"""

from ezscrapers.modules.control import addonPath, addonVersion, joinPath
from ezscrapers.windows.textviewer import TextViewerXML


def get():
	ezscrapers_path = addonPath()
	ezscrapers_version = addonVersion()
	changelogfile = joinPath(ezscrapers_path, 'changelog.txt')
	r = open(changelogfile, 'r', encoding='utf-8', errors='ignore')
	text = r.read()
	r.close()
	heading = '[B]ezScrapers -  v%s - ChangeLog[/B]' % ezscrapers_version
	windows = TextViewerXML('textviewer.xml', ezscrapers_path, heading=heading, text=text)
	windows.run()
	del windows
