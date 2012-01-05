#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QWidget

from configUI import Ui_config


class ConfigUI(QWidget):
    """Classe chargée de l'interface de configuration de l'application"""
    def __init__(self, parent=None):
        super(ConfigUI, self).__init__(parent)
        self.__conf = Config.getInstance()
        self.createWidgets()

    def createWidgets(self):
        self.ui = Ui_config()
        self.ui.setupUi(self)
        self.ui.leEmail.setText(self.__conf["email"])
        self.ui.leEmail.setProperty("name", "email")
        self.ui.leServeur.setText(self.__conf["serveur"])
        self.ui.leServeur.setProperty("name", "serveur")
        self.ui.sbDuree.setValue(int(self.__conf["duree"]))
        self.ui.sbDuree.setProperty("name", "duree")

        self.connect(self.ui.leEmail, SIGNAL("textChanged(QString)"),
            self.valueChanged)
        self.connect(self.ui.leServeur, SIGNAL("textChanged(QString)"),
            self.valueChanged)
        self.connect(self.ui.sbDuree, SIGNAL("valueChanged(QString)"),
            self.valueChanged)

    def valueChanged(self, value):
        self.__conf[str(self.sender().property("name").toString())] = str(value)

    def __del__(self):
        self.__conf.close()


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
            s = l.split("#")[0].split("=")
            self.__config[s[0].strip()] = s[1].strip()
        f.close()

    @staticmethod
    def getInstance():
        if Config._instance == None:
            Config._instance = Config()

        return Config._instance

    def keys(self):
        return self.__config.keys()

    def __getitem__(self, key):
        return self.__config[key]

    def __setitem__(self, key, value):
        self.__config[key] = value

    def close(self):
        """Enregistre les options dans le fichier de configuration"""
        f = open(self._path, "w")
        keys = self.__config.keys()
        for k in keys:
            f.write(k + "=" + self[k] + "\n")
        f.close()

if __name__ == "__main__":
    """Main de test"""
    c = Config.getInstance()
    keys = c.keys()
    for k in keys:
        print k + " = " + c[k]

    c["test"] = "tirlibibi"

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

