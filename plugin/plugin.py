from . import _
from Components.ActionMap import ActionMap
from Components.config import config, ConfigSubsection, ConfigSubList, ConfigNumber, ConfigText, configfile
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from enigma import eServiceReference
import xml.dom.minidom


url_sc = resolveFilename(SCOPE_PLUGINS, "Extensions/GreekNetRadio/flex.sh")

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
            <ePixmap pixmap="buttons/key_yellow.png" position="e/2,e-40" size="40,40" alphatest="blend"/>
            <ePixmap pixmap="buttons/key_blue.png" position="3*e/4,e-40" size="40,40" alphatest="blend"/>
            <widget source="key_red" render="Label" position="40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
            <widget source="key_green" render="Label" position="e/4+40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
            <widget source="key_yellow" render="Label" position="e/2+40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
            <widget source="key_blue" render="Label" position="3*e/4+40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.setTitle(_("Internet radio"))

        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText(_("Select"))
        self["key_yellow"] = StaticText(_("Update stations"))
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
            "yellow": self.update,
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

    def update(self):
        def updateCb(answer):
            if answer is True:
                self.session.open(Console, _("Updating stations..."), ["%s stations" % url_sc])

        msg = _("Do you really want to update the stations list?")
        self.session.openWithCallback(updateCb, MessageBox, msg, MessageBox.TYPE_YESNO)

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
            <ePixmap pixmap="buttons/key_yellow.png" position="e/2,e-40" size="40,40" alphatest="blend"/>
            <ePixmap pixmap="buttons/key_blue.png" position="3*e/4,e-40" size="40,40" alphatest="blend"/>
            <widget source="key_red" render="Label" position="40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
            <widget source="key_green" render="Label" position="e/4+40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
            <widget source="key_yellow" render="Label" position="e/2+40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
            <widget source="key_blue" render="Label" position="3*e/4+40,e-40" size="e/4-40,40" font="Regular;20" valign="center"/>
        </screen>"""

    def __init__(self, session, tag=""):
        Screen.__init__(self, session)
        self.setTitle(_("Internet radio"))
        self.skinName = ["GreekNetRadioCategory", "GreekNetRadio"]

        self.currentService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onClose.append(self.__onClose)

        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText("")
        self["key_yellow"] = StaticText("")
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
            "yellow": self.yellow,
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
        station = self["menu"].getCurrent() or None
        if station is not None:
            self.play(station[0], station[1])

    def play(self, name, url):
        try:
            self.session.nav.stopService()
            self.session.nav.playService(eServiceReference(4097, 0, url))
            self["key_yellow"].setText(_("Stop"))
        except:
            pass

    def yellow(self):
        current = self.session.nav.getCurrentlyPlayingServiceReference()
        if current != self.currentService: # only stop internet radio
            try:
                self.session.nav.stopService()
                self["key_yellow"].setText("")
            except:
                pass

    def blue(self):
        station = self["menu"].getCurrent() or None
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

    def __onClose(self):
        current = self.session.nav.getCurrentlyPlayingServiceReference()
        if not current or current != self.currentService:
            self.session.nav.playService(self.currentService)


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


def main(session, **kwargs):
    try:
        session.open(GreekNetRadio)
    except:
        print "[Greek net radio] Plugin execution failed"


def autostart(reason, **kwargs):
    if reason == 0:
        print "[Greek net radio] no autostart"


def Plugins(**kwargs):
    return PluginDescriptor(
        name=_("Internet radio"),
        where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU],
        description=_("Listen to your favourite radio stations"),
        icon="greekradio.png",
        fnc=main
    )
