#Application Dictionary addon for NVDA
#This file is covered by the GNU General Public License.
#See the file COPYING.txt for more details.
#Copyright (C) 2018 Ricardo Leonarczyk <ricardo.leonarczyk95@gmail.com>
#Copyright (C) 2022-2023 Rui Fontes <rui.fontes@tiflotecnia.com>
# Thanks by Cyrille Bougot colaboration!

# Import the necessary modules
import os
import shutil
import api
import globalPluginHandler
import globalVars
import gui
try:
	from gui.speechDict import DictionaryDialog
except:
	from gui import DictionaryDialog
import wx
import speechDictHandler
import NVDAState
from scriptHandler import script
try:
	from globalCommands import SCRCAT_CONFIG
except:
	SCRCAT_CONFIG = None
import addonHandler

# Start translation process
addonHandler.initTranslation()

title = ""
# Todo: fix a problem that causes dictionaries not to load sometimes on WUP apps
# Todo: When in NVDA GUI disable previous app dictionary
def getAppName():
	return api.getFocusObject().appModule.appName

def getDictFilePath(appName):
	dictFileName = appName + ".dic"
	dictFilePath = os.path.join(NVDAState.WritePaths.speechDictsDir, dictFileName)
	try:
		oldDictFilePath = os.path.abspath(os.path.join(NVDAState.WritePaths.speechDictsDirdictFileName))
	except:
		oldDictFilePath = os.path.abspath(os.path.join(NVDAState.WritePaths.speechDictsDir, dictFileName))
	if not os.path.isfile(dictFilePath) and os.path.isfile(oldDictFilePath):
		if not os.path.exists(appDictsPath):
			os.makedirs(appDictsPath)
		try:
			shutil.move(oldDictFilePath, dictFilePath)
		except:
			pass
	if os.path.isfile(dictFilePath) and os.path.getsize(dictFilePath) <= 0:
		os.unlink(dictFilePath)
	return dictFilePath

def loadEmptyDicts():
	dirs = os.listdir(appDictsPath) if os.path.exists(appDictsPath) else []
	return dict([(f[:-4], None) for f in dirs if os.path.isfile(os.path.join(appDictsPath, f)) and f.endswith(".dic")])

def loadDict(appName):
	ensureEntryCacheSize(appName)
	dict = speechDictHandler.SpeechDict()
	dict.load(getDictFilePath(appName))
	dicts[appName] = dict
	return dict

def getDict(appName):
	if appName in dicts:
		dict = dicts[appName]
		if dict:
			return dict
		else:
			return loadDict(appName)
	else:
		return loadDict(appName)

def createDict(appName):
	return loadDict(appName)

def ensureEntryCacheSize(appName):
	entries = sorted([(e[0], len(e[1])) for e in dicts.items() if e[1] is not None and e[0] != appName], key = lambda e: e[1])
	acc = 0
	for e in entries:
		acc = acc + e[1]
		if acc >= entryCacheSize:
					dicts[e[0]] = None

try:
	appDictsPath = os.path.abspath(os.path.join(NVDAState.WritePaths.speechDictsDir, "appDicts"))
except:
	appDictsPath = os.path.abspath(os.path.join(NVDAState.WritePaths.speechDictsDir, "appDicts"))
dicts = loadEmptyDicts()
entryCacheSize = 20000


class AppDictionaryDialog(DictionaryDialog):
	def __init__(self, parent):
		super().__init__(
			parent,
			# Translators: Title for app speech dictionary dialog.
			title,
			speechDict = apDict)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		self.__currentDict = None
		self.__currentAppName = None
		self.dictsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu.GetMenuItems()[1].GetSubMenu()
		# Translators: The label for the menu item to open Application specific speech dictionary dialog.
		self.appDictDialog = self.dictsMenu.Append(wx.ID_ANY, _("&Application Dictionary..."), _("A dialog where you can set application-specific dictionary by adding dictionary entries to the list"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.script_editDict, self.appDictDialog)

	def event_gainFocus(self, obj, nextHandler):
		appName = getAppName()
		if not self.__currentAppName or self.__currentAppName != appName:
			self.__currentAppName = appName
			dict = getDict(appName)
			self.__setCurrentDict(dict)
		nextHandler()

	@script( 
		# Translators: Message to be announced during Keyboard Help 
		description = _("Shows the application-specific dictionary dialog"), 
		category = (SCRCAT_CONFIG), 
		gesture = "kb:NVDA+Control+Shift+d")
	def script_editDict(self, gesture):
		prevFocus = gui.mainFrame.prevFocus
		appName = prevFocus.appModule.appName if prevFocus else getAppName()
		global apDict
		apDict = getDict(appName)
		if not apDict:
			apDict = createDict(appName)
		# Translators: title of application dictionary dialog.
		global title
		title = _("Dictionary for {arg0}").format(arg0=appName)
		try:
			gui.mainFrame.popupSettingsDialog(AppDictionaryDialog)
		except:
			gui.mainFrame.popupSettingsDialog(gui.DictionaryDialog, title, dict)

	# Temp dictionary usage taken from emoticons add-on
	def __setCurrentDict(self, dict):
		if self.__currentDict:
			for e in self.__currentDict: speechDictHandler.dictionaries["temp"].remove(e)
		self.__currentDict = dict
		if self.__currentDict:
			speechDictHandler.dictionaries["temp"].extend(self.__currentDict)

	def terminate(self):
		# This terminate function is necessary when creating new menus.
		try:
			if wx.version().startswith("4"):
				self.dictsMenu.Remove(self.appDictDialog)
			else:
				self.dictsMenu.RemoveItem(self.appDictDialog)
		except:
			pass


if globalVars.appArgs.secure:
	# Override the global plugin to disable it.
	GlobalPlugin = globalPluginHandler.GlobalPlugin
