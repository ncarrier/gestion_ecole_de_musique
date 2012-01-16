#!/usr/bin/python -t
# -*- coding: utf-8 -*-

import sys

from PySide.QtCore import QLocale, QTranslator, QLibraryInfo, QIODevice, QFile
from PySide.QtGui import QApplication, QMainWindow, QMessageBox
from PySide.QtSql import QSqlDatabase

from gemUI import Ui_gem
from mail import MailUI
from absence import AbsenceUI
from intervenant import IntervenantUI
from config import ConfigUI, Config


class GestionAbsences(QMainWindow):
    def __init__(self, parent=None):
        super(GestionAbsences, self).__init__(parent)
        self.__conf = Config.getInstance()

        self.createWidgets()
        self.restoreGeometry(self.__conf["mainWindowGeometry"])
        self.restoreState(self.__conf["mainWindowState"])
        self.__connectSlots()
        self.__verifieConfig()

    def __verifieConfig(self):
        u"""Vérifie que la configuration est valide

        Donne le focus à l'onglet de configuration sinon

        """
        if (not self.__conf["signature"] or
            not self.__conf["email"] or
            not self.__conf["duree"] or
            not self.__conf["serveur"]):
            QMessageBox.information(self, u"Première configuration",
                    u"""Il semble que ce soit la première fois que vous lancez
gem, veuillez vérifier que la configuration est correcte""")
            self.__ui.tabWidget.setCurrentIndex(3)

    def __connectSlots(self):
        u"""Connecte les signaux de l'ui principale"""
        self.mailTab.majBdd.connect(self.absenceTab.miseAJour)
        self.absenceTab.majBdd.connect(self.mailTab.miseAJour)
        self.intervenantTab.majBdd.connect(self.mailTab.miseAJour)
        self.intervenantTab.majBdd.connect(self.absenceTab.miseAJour)
        self.__configTab.majDuree.connect(self.mailTab.miseAJour)

        self.mailTab.notification.connect(self.__ui.statusbar.showMessage)
        self.absenceTab.notification.connect(self.__ui.statusbar.showMessage)

    def createWidgets(self):
        self.__ui = Ui_gem()
        self.__ui.setupUi(self)
        self.__ajouteOnglets(self.__ui.tabWidget)

    def __ajouteOnglets(self, tabWidget):
        u"""Construit et attache les onglets au tab widget"""
        # l'onglet config doit être créé avant les autres
        self.__configTab = ConfigUI(self)
        self.mailTab = MailUI(self)
        self.absenceTab = AbsenceUI(self)
        self.intervenantTab = IntervenantUI(self)
        tabWidget.addTab(self.mailTab, "Emails")
        tabWidget.addTab(self.absenceTab, "Absences")
        tabWidget.addTab(self.intervenantTab, "Intervenants")
        tabWidget.addTab(self.__configTab, "Configuration")

    def closeEvent(self, event):
        self.__conf["mainWindowGeometry"] = self.saveGeometry()
        self.__conf["mainWindowState"] = self.saveState()


if __name__ == "__main__":
    ret = 0
    log = QFile("log")
    log.open(QIODevice.WriteOnly)
    try:
        app = QApplication(sys.argv)

        locale = QLocale.system().name()
        translator = QTranslator()
        translator.load("qt_" + locale,
            QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        app.installTranslator(translator)

        # Configuration de la base de données
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('private/gem.db')
        db.open()

        # Création de l'__ui principale et boucle principale
        ui = GestionAbsences()
        ui.show()
        ret = app.exec_()
    except Exception, e:
        log.write(str(e))
        log.close()
    sys.exit(ret)
