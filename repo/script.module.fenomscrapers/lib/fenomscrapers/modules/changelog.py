# -*- coding: utf-8 -*-
"""
	Fenomscrapers Module
"""

from fenomscrapers.modules.control import addonPath, addonVersion, joinPath
from fenomscrapers.windows.textviewer import TextViewerXML


def get():
	fenomscrapers_path = addonPath()
	fenomscrapers_version = addonVersion()
	changelogfile = joinPath(fenomscrapers_path, 'changelog.txt')
	r = open(changelogfile, 'r', encoding='utf-8', errors='ignore')
	text = r.read()
	r.close()
	heading = '[B]FenomScrapers -  v%s - ChangeLog[/B]' % fenomscrapers_version
	windows = TextViewerXML('textviewer.xml', fenomscrapers_path, heading=heading, text=text)
	windows.run()
	del windows