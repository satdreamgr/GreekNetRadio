from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import InputBox
from Components.FileList import FileList
import urllib
from urllib2 import urlopen
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap,NumberActionMap
from Components.MenuList import MenuList
import xml.dom.minidom
import os
from Screens.Console import Console
import gettext
from Components.Button import Button
from Tools.Directories import fileExists
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from enigma import eListboxPythonMultiContent, getDesktop, gFont, loadPNG
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Screens.MessageBox import MessageBox
from Components.Label import Label
from Components.ServiceEventTracker import ServiceEventTracker
from enigma import iPlayableService, iServiceInformation,eServiceReference,eListboxPythonMultiContent, getDesktop, gFont, loadPNG
from Tools.LoadPixmap import LoadPixmap
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import config, ConfigDirectory, ConfigSubsection, ConfigSubList, \
	ConfigEnableDisable, ConfigNumber, ConfigText, ConfigSelection, \
	ConfigYesNo, ConfigPassword, getConfigListEntry, configfile

config.plugins.Cradio = ConfigSubsection()
config.plugins.Cradio.stations = ConfigSubList()
config.plugins.Cradio.stations_count = ConfigNumber(default=0)
version="v 1.0"
currxmlversion="1.0"
url_sc="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/flex.sh"

try:
	cat = gettext.translation('lang', '/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/po', [config.osd.language.getText()])
	_ = cat.gettext
except IOError:
	pass

def initProfileConfig():
	s = ConfigSubsection()
	s.name =  ConfigText(default = "")
	s.code= ConfigText(default = "")
	config.plugins.Cradio.stations.append(s)
	return s

def initConfig():
	count = config.plugins.Cradio.stations_count.value
	if count != 0:
		i = 0
		while i < count:
			initProfileConfig()
			i += 1

initConfig()

def lsSelected():
           lst = []
           count = config.plugins.Cradio.stations_count.value
	   if count != 0:
		for i in range(0,count):
			name = config.plugins.Cradio.stations[i].name.value
			code = config.plugins.Cradio.stations[i].code.value
			lst.append(name)

	   else:
			lst=[]
	   return lst

def AddOnCategoryComponent(name, png):
	res = [ name ]

	res.append(MultiContentEntryText(pos=(140, 5), size=(300, 35), font=0, text=name))
	res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 0), size=(100, 60), png = png))

class GreekMenuscrn(Screen):
	try:
		sz_w = getDesktop(0).size().width()
	except:
		sz_w = 720
	if (sz_w == 1280):
		skin = """
		<screen flags="wfNoBorder" position="0,0" size="1280,720" title=" Greek NetRadio" >
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,240" size="40,40" zPosition="-1"/>	
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,280" size="40,40" zPosition="-1"/>		
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/downloads.png" position="60,320" size="40,40" zPosition="-1"/>		
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/about.png" position="60,360" size="40,40" zPosition="-1"/>				
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/main.png" position="0,0" size="1280,720" zPosition="-2"/>
		<widget name="menu" itemHeight="40" position="100,240" size="520,240" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/barreb.png" transparent="1" zPosition="9"/>
		</screen>"""
	else:
		skin = """
		<screen position="center,center" size="500,300" title=" Greek Net Radio" >
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/radio.png" position="100,60" size="1280,300" zPosition="-1"/>
		<widget name="menu" itemHeight="35" position="0,0" size="500,150" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/barreb.png" transparent="1" zPosition="9"/>
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		menu = []
		menu.append((_("Fm Stations"),"Stations"))
		menu.append((_("Web Stations"),"WebStations"))
		menu.append((_("Update Stations"),"update"))		
		menu.append((_("About %s")%version,"About"))

        	self["menu"] = MenuList(menu)
        	self["actions"] = ActionMap(["WizardActions", "DirectionActions"],{"ok": self.go,"back": self.close,}, -1)
    	def go(self):
    		if self["menu"].l.getCurrentSelection() is not None:
        		choice = self["menu"].l.getCurrentSelection()[1]		
			
			if choice == "Stations":
			    self.session.open(GreekStationsScreen)	
			    		
			if choice == "WebStations":
			    self.session.open(WebStationsScreen)			
			
			if choice == "About":
			    self.session.open(classicAboutScreen)	

			 
			if choice == "update":			
				self.session.openWithCallback(self.greek,MessageBox,_("Confirm your selection, or exit"), MessageBox.TYPE_YESNO)								   
				   	   
	def greek(self, answer):
		if answer:
			self.session.open(Console,_("Install sources"),["%s stations" % url_sc])

class WebStationsScreen(Screen):
	def __init__(self, session):
		self.skin = GreekStationsScreen.skin
		Screen.__init__(self,session)
                self.CurrentService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		self.onClose.append(self.__onClose)

		list = []
		self["ButtonYellow"] = Pixmap()
		self["ButtonYellowtext"] = Label(_("Press OK to Play or button yellow"))
	        myfile = "/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/webstations"

                xmlparse = xml.dom.minidom.parse(myfile)
                self.xmlparse=xmlparse
		for stations in self.xmlparse.getElementsByTagName("webstations"):

				for station in stations.getElementsByTagName("station"):
					list.append(station.getAttribute("name").encode("utf8"))
                list.sort()
		self["stationmenu"] = MenuList(list)
		self["actions"] = ActionMap(["SetupActions","ColorActions"],
		{
		        "yellow"    :     self.selstation,
			"ok"  		: self.selstation	,
			"cancel"  :	self.close,
		}, -2)

	def selstation(self):

			selection_station = self["stationmenu"].getCurrent()
			for stations in self.xmlparse.getElementsByTagName("webstations"):

					for station in stations.getElementsByTagName("station"):

						if station.getAttribute("name").encode("utf8") == selection_station:
							urlserver = str(station.getElementsByTagName("url")[0].childNodes[0].data)
                                                        pluginname = station.getAttribute("name").encode("utf8")

		                                	self.prombt(urlserver,pluginname)

       	def prombt(self, com,dom):
       	               self.currentStreamingURL = ""
	               self.currentStreamingStation = ""
	 	       self.session.nav.stopService()

	               self.currentStreamingStation = dom
		       self.playServiceStream(com)

	def playServiceStream(self, url):
		self.session.nav.stopService()
		sref = eServiceReference(4097, 0, url)
		self.session.nav.playService(sref)
		self.currentStreamingURL = url

        def __onClose(self):

		self.session.nav.playService(self.CurrentService)

class GreekStationsScreen(Screen):
        try:
		sz_w = getDesktop(0).size().width()
		if sz_w == 1280:
			HD_Res = True
		else:
			HD_Res = False
	except:
		HD_Res = False

	if HD_Res:
	    skin = """
		<screen flags="wfNoBorder" position="0,0" size="1280,720" title="Greek Net Radio " >
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,80" size="40,40" zPosition="-1"/>	 		
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,120" size="40,40" zPosition="-1"/>	    
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,160" size="40,40" zPosition="-1"/>	 
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,200" size="40,40" zPosition="-1"/>			
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,240" size="40,40" zPosition="-1"/>			
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,280" size="40,40" zPosition="-1"/>	
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,320" size="40,40" zPosition="-1"/>					
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,360" size="40,40" zPosition="-1"/>			
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,400" size="40,40" zPosition="-1"/>			
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,440" size="40,40" zPosition="-1"/>			
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,480" size="40,40" zPosition="-1"/>	
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,520" size="40,40" zPosition="-1"/>	
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,560" size="40,40" zPosition="-1"/>			
		<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/musique.png" position="60,600" size="40,40" zPosition="-1"/>								
	    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/stations.png" position="0,0" size="1280,720"  zPosition="-2"/>
	    <widget name="ButtonYellowtext" position="640,630" size="580,30" valign="left" halign="left" zPosition="10" font="Regular;23" transparent="1" foregroundColor="yellow"  />
	    <widget name="ButtonYellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/buttons/yellow.png" position="640,610" zPosition="10" size="100,60" transparent="1" alphatest="on" />
		<widget name="stationmenu" itemHeight="40" position="100,80" size="520,560" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/barreb.png" transparent="1" scrollbarMode="showNever" zPosition="9"/>
	    </screen>"""

	else:
            skin = """
            <screen position="center,center" size="600,500" title="Greek NetRadio" >
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/stations.png" position="0,0" size="620,450"/>
            <widget name="ButtonYellowtext" position="20,10" size="500,60" valign="center" halign="center" zPosition="10" font="Regular;21" transparent="1" foregroundColor="yellow" />
            <widget name="ButtonYellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/buttons/yellow.png" position="20,10" zPosition="10" size="100,60" transparent="1" alphatest="on" />
            <widget name="stationmenu" position="10,80" size="590,425" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/barreb.png" transparent="1" zPosition="4" />
            </screen>"""

	def __init__(self, session):
		self.skin = GreekStationsScreen.skin
		Screen.__init__(self,session)
                self.CurrentService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		self.onClose.append(self.__onClose)

		list = []
		self["ButtonYellow"] = Pixmap()
		self["ButtonYellowtext"] = Label(_("Press OK to Play or button yellow"))
	        myfile = "/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/fmstations"

                xmlparse = xml.dom.minidom.parse(myfile)
                self.xmlparse=xmlparse
		for stations in self.xmlparse.getElementsByTagName("fmstations"):

				for station in stations.getElementsByTagName("station"):
					list.append(station.getAttribute("name").encode("utf8"))
                list.sort()
		self["stationmenu"] = MenuList(list)
		self["actions"] = ActionMap(["SetupActions","ColorActions"],
		{
		        "yellow"    :     self.selstation,
			"ok"  		: self.selstation	,
			"cancel"  :	self.close,
		}, -2)

	def selstation(self):

			selection_station = self["stationmenu"].getCurrent()
			for stations in self.xmlparse.getElementsByTagName("fmstations"):

					for station in stations.getElementsByTagName("station"):

						if station.getAttribute("name").encode("utf8") == selection_station:
							urlserver = str(station.getElementsByTagName("url")[0].childNodes[0].data)
                                                        pluginname = station.getAttribute("name").encode("utf8")

		                                	self.prombt(urlserver,pluginname)

       	def prombt(self, com,dom):
       	               self.currentStreamingURL = ""
	               self.currentStreamingStation = ""
	 	       self.session.nav.stopService()

	               self.currentStreamingStation = dom
		       self.playServiceStream(com)

	def playServiceStream(self, url):
		self.session.nav.stopService()
		sref = eServiceReference(4097, 0, url)
		self.session.nav.playService(sref)
		self.currentStreamingURL = url

        def __onClose(self):

		self.session.nav.playService(self.CurrentService)

class classicAboutScreen(Screen):
	skin = """
	<screen position="0,0" size="1280,720" title="Greek NetRadio Classic" >
	  <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/GreekNetRadio/icons/main.png" position="0,0" size="1280,720"  zPosition="-2"/>
		<widget name="text" position="80,240" size="520,420" font="Regular;24" transparent="1"/>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		info="\n Greek NetRadio version v.1.0  \n ---------------------------  \n By SatDreamGR\n\n http://www.satdreamgr.com\n --------------------------- \n\n\n\n\n Thanks-Mahmoud Faraj-Tunisiasat"


		self["text"] = ScrollLabel(info)

		self["actions"] = ActionMap(["SetupActions"],
			{
				"ok": self.close,
				"cancel": self.close,

			}, -1)

def main(session,**kwargs):
    try:
     	session.open(GreekMenuscrn)
    except:
        print "[Greek NetRadio] Pluginexecution failed"

def autostart(reason,**kwargs):
    if reason == 0:
        print "[Greek NetRadio] no autostart"

def Plugins(**kwargs):
    return PluginDescriptor(
        name="Greek Net Radio",
        where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU],
        description=_("Listen to your greek music"),
        icon="greekradio.png",
        fnc = main
        )			
