#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["ConfigUI", "Config"]

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QWidget

from configUI import Ui_config


class ConfigUI(QWidget):
# signaux
    u"""Signal envoyé quand la duree a été modifiée"""
    majDuree = pyqtSignal()

    """Classe chargée de l'interface de configuration de l'application"""
    def __init__(self, parent=None):
        super(ConfigUI, self).__init__(parent)
        self.__conf = Config.getInstance()
        self.__createWidgets()

    def __createWidgets(self):
        """Créée les widgets de l'interface graphique"""
        self.__ui = Ui_config()
        self.__ui.setupUi(self)
        self.__ui.leEmail.setText(self.__conf["email"])
        self.__ui.leEmail.setProperty("name", "email")
        self.__ui.leSignature.setText(self.__conf["signature"])
        self.__ui.leSignature.setProperty("name", "signature")
        self.__ui.sbDuree.setValue(int(self.__conf["duree"]))
        self.__ui.sbDuree.setProperty("name", "duree")
        self.__ui.leServeur.setText(self.__conf["serveur"])
        self.__ui.leServeur.setProperty("name", "serveur")

        self.__ui.leEmail.textChanged.connect(self.__valueChanged)
        self.__ui.leSignature.textChanged.connect(self.__valueChanged)
        self.__ui.sbDuree.valueChanged.connect(self.__valueChanged)
        self.__ui.leServeur.textChanged.connect(self.__valueChanged)

    def __valueChanged(self, value):
        """Enregistre la valeur modifiée, dans la propriété correspondante"""
        key = str(self.sender().property("name").toString())
        self.__conf[key] = str(value)
        if key == "duree" or key == "signature":
            self.majDuree.emit()

    def __del__(self):
        """Destructeur, écrit le fichier de configuration"""
        self.__conf.sauve()


class Config():
    """Classe chargée de la lecture/écriture/sauvegarde de la configuration"""
    _instance = None
    _path = "private/config"

    def __init__(self):
        assert self._instance == None
        Config._instance = self

        self.__config = {}
        f = open(Config._path, "r")
        lines = f.readlines()
        for l in lines:
            # Jette les commentaires
            l = l.split("#")[0]
            # Enlève les espaces aux extrémités
            l = l.strip('\t\v\r\n ')
            # Separate key and value
            s = l.split("=")
            if len(s) == 2:
                self.__config[s[0].strip()] = s[1].strip()
            else:
                print u"Ligne malformée (" + l + ")"
        f.close()

    @staticmethod
    def getInstance():
        if Config._instance == None:
            Config._instance = Config()

        return Config._instance

    def keys(self):
        return self.__config.keys()

    def __getitem__(self, key):
        """Méthode magique sous-jacent à l'opérateur [] en lecture"""
        if key in self.keys():
            return self.__config[key]
        else:
            return ""

    def __setitem__(self, key, value):
        """Méthode magique sous-jacent à l'opérateur [] en écriture"""
        self.__config[key] = value

    def __delitem__(self, key):
        """Méthode magique sous-jacent à l'opérateur del"""
        del self.__config[key]

    def sauve(self):
        """Enregistre les options dans le fichier de configuration"""
        f = open(self._path, "w")
        keys = self.__config.keys()
        for k in keys:
            if k != "password":
                f.write(k + "=" + self[k] + "\n")
        f.close()

if __name__ == "__main__":
    """Main de test"""
    import sys
    from PyQt4.QtGui import QApplication
    from PyQt4.QtCore import QLibraryInfo, QLocale, QTranslator, QString

    app = QApplication(sys.argv)

    locale = QLocale.system().name()
    translator = QTranslator()
    translator.load(QString("qt_") + locale,
        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)

    ui = ConfigUI()
    ui.show()
    ret = app.exec_()
    sys.exit(ret)
