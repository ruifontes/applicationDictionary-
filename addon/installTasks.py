#Application Dictionary addon for NVDA
#This file is covered by the GNU General Public License.
#See the file COPYING.txt for more details.
#Copyright (C) 2018 Ricardo Leonarczyk <ricardo.leonarczyk95@gmail.com>
#Copyright (C) 2022 Rui Fontes <rui.fontes@tiflotecnia.com>

import addonHandler
import gui
import wx

addonHandler.initTranslation()

# Code from Emoticons add-on
def onInstall():
	for addon in addonHandler.getAvailableAddons():
		if addon.name == "applicationsDictionary":
			if gui.messageBox(
				# Translators: the label of a message box dialog.
				_("You have installed an incompatible version of the add-on. Do you want to uninstall the incompatible version?"),
				# Translators: the title of a message box dialog.
				_("Uninstall incompatible add-on"),
				wx.YES|wx.NO|wx.ICON_WARNING)==wx.YES:
					addon.requestRemove()
