#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["ConfigUI", "Config"]

from PySide.QtCore import Slot, Signal, QCoreApplication, QSettings
from PySide.QtGui import QWidget

from configUI import Ui_config

version = "0.1.0"
duree_defaut = "14"


class ConfigUI(QWidget):
# signaux
    u"""Signal envoyé quand la duree a été modifiée"""
    majDuree = Signal()
    CONFIG_TEXT = 0
    CONFIG_INT = 1
    CONFIG_BOOL = 2
    CONFIG_PWD = 3

    """Classe chargée de l'interface de configuration de l'application"""
    def __init__(self, parent=None):
        super(ConfigUI, self).__init__(parent)
        self.__conf = Config.getInstance()
        self.__createWidgets()

    def setMap(self):
        # mapping nom -> (contrôle, callback de setting)
        self.__map = {
            "signature": (# name
                self._ui.leSignature, # widget
                ConfigUI.CONFIG_TEXT
            ),
            "duree": (
                self._ui.sbDuree,
                ConfigUI.CONFIG_INT
            ),
            "email": (
                self._ui.leEmail,
                ConfigUI.CONFIG_TEXT
            ),
            "serveur": (
                self._ui.leServeur,
                ConfigUI.CONFIG_TEXT
            ),
            "port": (
                self._ui.sbPort,
                ConfigUI.CONFIG_INT
            ),
            "securite": (
                self._ui.cbSecurite,
                ConfigUI.CONFIG_TEXT
            ),
            "login": (
                self._ui.leLogin,
                ConfigUI.CONFIG_TEXT
            ),
            "password": (
                self._ui.lePassword,
                ConfigUI.CONFIG_TEXT
            ),
        }

    def __createWidgets(self):
        """Créée les widgets de l'interface graphique"""
        self._ui = Ui_config()
        self._ui.setupUi(self)
        self.setMap()
        self._ui.wMail.setVisible(False)

        for key in self.__map.keys():
            widget = self.__map[key][0]
            widget.setProperty("name", key)
            if self.__map[key][1] == ConfigUI.CONFIG_TEXT:
                widget.textChanged.connect(self.valueChanged)
                if not self.__conf[key]:
                    if not self.__map[key][2]:
                        self.__conf[key] = ""
                    else:
                        self.__conf[key] = self.__map[key][2]
                widget.setText(self.__conf[key])

            elif self.__map[key][1] == ConfigUI.CONFIG_INT:
                self.__map[key][0].valueChanged.connect(self.valueChanged)

        self._ui.leEmail.setText(self.__conf["email"])
        self._ui.leSignature.setText(self.__conf["signature"])

        if not self.__conf["duree"]:
            self.__conf["duree"] = duree_defaut
        self._ui.sbDuree.setValue(int(self.__conf["duree"]))
        self._ui.leServeur.setText(self.__conf["serveur"])

        self._ui.cbMail.stateChanged.connect(self._ui.wMail.setVisible)

    @Slot()
    def valueChanged(self, value):
        """Enregistre la valeur modifiée, dans la propriété correspondante"""
        key = self.sender().property("name")
        self.__conf[key] = value
        if key == "duree" or key == "signature":
            self.majDuree.emit()


class Config():
    """Classe chargée de la lecture/écriture/sauvegarde de la configuration"""
    _instance = None
    _path = "private/config"

    def __init__(self):
        assert self._instance == None
        Config._instance = self
        QCoreApplication.setOrganizationName("nicolas.carrier")
        QCoreApplication.setApplicationVersion(version)
        QCoreApplication.setApplicationName("gem")

        self.__settings = QSettings()

    @staticmethod
    def getInstance():
        if Config._instance == None:
            Config._instance = Config()

        return Config._instance

    def keys(self):
        return self.__settings.allKeys()

    def __getitem__(self, key):
        """Méthode magique sous-jacent à l'opérateur [] en lecture"""
        if key in self.keys():
            return self.__settings.value(key)
        else:
            return ""

    def __setitem__(self, key, value):
        """Méthode magique sous-jacent à l'opérateur [] en écriture"""
        self.__settings.setValue(key, value)

    def __delitem__(self, key):
        """Méthode magique sous-jacent à l'opérateur del"""
        self.__settings.remove(key)

if __name__ == "__main__":
    """Main de test"""
    import sys
    from PySide.QtGui import QApplication
    from PySide.QtCore import QLibraryInfo, QLocale, QTranslator

    app = QApplication(sys.argv)

    locale = QLocale.system().name()
    translator = QTranslator()
    translator.load("qt_" + locale,
        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)

    ui = ConfigUI()
    ui.show()
    ret = app.exec_()
    sys.exit(ret)
