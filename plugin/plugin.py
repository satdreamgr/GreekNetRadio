from . import _
from Components.ActionMap import ActionMap
from Components.config import config, ConfigSubsection, ConfigSubList, ConfigNumber, ConfigText, configfile
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from enigma import eServiceReference, iPlayableService, iServiceInformation
import xml.dom.minidom


config.plugins.Cradio = ConfigSubsection()
config.plugins.Cradio.stations = ConfigSubList()
config.plugins.Cradio.stations_count = ConfigNumber(default=0)


def initProfileConfig():
    s = ConfigSubsection()
    s.name = ConfigText(default="")
    s.code = ConfigText(default="")
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


class GreekNetRadio(Screen):

    skin = """
        <screen position="center,center" size="3*e/4,3*e/4" title="Internet radio">
            <widget name="menu" position="0,10" size="e,e-60" itemHeight="40" font="Body" textOffset="10,0" scrollbarMode="showOnDemand"/>
            <ePixmap pixmap="buttons/key_red.png" position="0,e-40" size="40,40" alphatest="blend"/>
            <ePixmap pixmap="buttons/key_green.png" position="e/4,e-40" size="40,40" alphatest="blend"/>
            <ePixmap pixmap="buttons/key_blue.png" position="3*e/4,e-40" size="40,40" alphatest="blend"/>
            <widget source="key_red" render="Label" position="40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
            <widget source="key_green" render="Label" position="e/4+40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
            <widget source="key_blue" render="Label" position="3*e/4+40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.setTitle(_("Internet radio"))

        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText(_("Select"))
        self["key_blue"] = StaticText(_("About"))

        menu = []
        menu.append((_("Favourite stations"), "favourites"))
        menu.append((_("Greek FM stations"), "greekfm"))
        menu.append((_("Greek web stations"), "greekweb"))
        menu.append((_("International stations"), "international"))
        self["menu"] = MenuList(menu)

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
        {
            "cancel": self.close,
            "red": self.close,
            "ok": self.go,
            "green": self.go,
            "blue": self.about,
        }, -1)

    def go(self):
        choice = self["menu"].getCurrent() and self["menu"].getCurrent()[1] or ""

        if choice == "favourites":
            self.session.open(FavouriteStations)
        elif choice == "greekfm":
            self.session.open(GreekFmStations)
        elif choice == "greekweb":
            self.session.open(GreekWebStations)
        elif choice == "international":
            self.session.open(InternationalStations)

    def about(self):
        msg = _("Internet radio plugin by SatDreamGR")
        msg += "\n\n"
        msg += _("For information or questions please refer to the www.satdreamgr.com forum.")
        self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)


class GreekNetRadioCategory(Screen):

    skin = """
        <screen position="center,center" size="3*e/4,3*e/4" title="Internet radio">
            <widget name="menu" position="0,10" size="e,e-60" itemHeight="40" font="Body" textOffset="10,0" scrollbarMode="showOnDemand"/>
            <ePixmap pixmap="buttons/key_red.png" position="0,e-40" size="40,40" alphatest="blend"/>
            <ePixmap pixmap="buttons/key_green.png" position="e/4,e-40" size="40,40" alphatest="blend"/>
            <ePixmap pixmap="buttons/key_blue.png" position="3*e/4,e-40" size="40,40" alphatest="blend"/>
            <widget source="key_red" render="Label" position="40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
            <widget source="key_green" render="Label" position="e/4+40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
            <widget source="key_blue" render="Label" position="3*e/4+40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
        </screen>"""

    def __init__(self, session, tag=""):
        Screen.__init__(self, session)
        self.setTitle(_("Internet radio"))
        self.skinName = ["GreekNetRadioCategory", "GreekNetRadio"]

        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText("")
        self["key_blue"] = StaticText("")

        self.tag = tag
        self.stationsList = []
        self.setStationsList()
        self["menu"] = MenuList(self.stationsList)

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
        {
            "cancel": self.close,
            "red": self.close,
            "ok": self.go,
            "green": self.go,
            "blue": self.blue,
        }, -2)

    def setStationsList(self):
        path = resolveFilename(SCOPE_PLUGINS, "Extensions/GreekNetRadio/%s" % self.tag)
        try:
            xmlList = xml.dom.minidom.parse(path)
            for stations in xmlList.getElementsByTagName(self.tag):
                for station in stations.getElementsByTagName("station"):
                    name = station.getAttribute("name").encode("utf8")
                    url = str(station.getElementsByTagName("url")[0].childNodes[0].data)
                    self.stationsList.append((name, url))
            if len(self.stationsList) != 0:
                self.stationsList.sort()
                self["key_green"].setText(_("Play"))
                self["key_blue"].setText(_("Add to favourites"))
        except:
            pass

    def go(self):
        station = self["menu"].getCurrent()
        if station is not None:
            self.session.open(GreekNetRadioPlayer, station[0], station[1])

    def blue(self):
        station = self["menu"].getCurrent()
        if station is not None:
            try:
                current = initProfileConfig()
                current.name.value = station[0]
                current.code.value = station[0] + "," + station[1] # for compatibility with previous version
                current.save()
                config.plugins.Cradio.stations_count.value += 1
                config.plugins.Cradio.stations_count.save()
                config.plugins.Cradio.save()
                configfile.save()

                msg = _("Station successfully added to favourites")
                self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, 5)
            except:
                pass


class FavouriteStations(GreekNetRadioCategory):

    def __init__(self, session):
        GreekNetRadioCategory.__init__(self, session)
        self.setTitle(_("Favourite stations"))

    def setStationsList(self): # load favourites from config file
        try:
            self.stationsList = []
            count = config.plugins.Cradio.stations_count.value
            for i in range(0, count):
                #name = config.plugins.Cradio.stations[i].name.value
                code = config.plugins.Cradio.stations[i].code.value.split(",")
                name = code[0]
                url = code[1]
                self.stationsList.append((name, url))
            if len(self.stationsList) != 0:
                self["key_green"].setText(_("Play"))
                self["key_blue"].setText(_("Delete"))
        except:
            pass

    def blue(self): # override parent's method
        index = self["menu"].getSelectedIndex()
        try:
            del config.plugins.Cradio.stations[index]
            config.plugins.Cradio.stations.save()
            config.plugins.Cradio.stations_count.value -= 1
            config.plugins.Cradio.stations_count.save()
            config.plugins.Cradio.save()
            configfile.save()

            # update "menu" with new stations list
            self.setStationsList()
            self["menu"].setList(self.stationsList)

            if len(self.stationsList) == 0:
                self["key_blue"].setText("")

            msg = _("Station successfully deleted from favourites")
            self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, 5)
        except:
            pass


class GreekFmStations(GreekNetRadioCategory):

    def __init__(self, session):
        GreekNetRadioCategory.__init__(self, session, "fmstations")
        self.setTitle(_("Greek FM stations"))


class GreekWebStations(GreekNetRadioCategory):

    def __init__(self, session):
        GreekNetRadioCategory.__init__(self, session, "webstations")
        self.setTitle(_("Greek web stations"))


class InternationalStations(GreekNetRadioCategory):

    def __init__(self, session):
        GreekNetRadioCategory.__init__(self, session, "interstations")
        self.setTitle(_("International stations"))


class GreekNetRadioPlayer(Screen):

    skin = """
        <screen name="GreekNetRadioPlayer" flags="wfNoBorder" position="center,0" size="e,160" title="Internet radio player" backgroundColor="#FF000000">
            <widget source="session.CurrentService" render="Label" position="e/16,30" size="e/16,50" font="Body" valign="center" transparent="1">
                <convert type="ServicePosition">Position</convert>
            </widget>
            <widget name="name" position="e/8,30" size="e/2,50" font="Body" valign="center" transparent="1"/>
            <widget name="info" position="e/16,80" size="e/2,50" font="Body" valign="center" transparent="1"/>
        </screen>"""

    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self["name"] = Label(name)
        self["info"] = Label("")

        self["actions"] = ActionMap(["OkCancelActions"],
        {
            "ok": self.close,
            "cancel": self.close,
        }, -2)

        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
            iPlayableService.evUpdatedInfo: self.__evUpdatedInfo
        })

        self.onClose.append(self.__onClose)
        self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.session.nav.stopService()
        self.session.nav.playService(eServiceReference(4097, 0, url))

    def __onClose(self):
        self.session.nav.stopService()
        self.session.nav.playService(self.oldService)

    def __evUpdatedInfo(self):
        currPlay = self.session.nav.getCurrentService()
        if currPlay is not None:
            self["info"].setText(currPlay.info().getInfoString(iServiceInformation.sTagTitle))


def main(session, **kwargs):
    session.open(GreekNetRadio)


def Plugins(**kwargs):
    return PluginDescriptor(
        name=_("Internet radio"),
        where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU],
        description=_("Listen to your favourite radio stations"),
        icon="greekradio.png",
        fnc=main
    )
