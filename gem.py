#!/usr/bin/python -t
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtCore import QLocale, QTranslator, QString, QLibraryInfo, QSettings
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QApplication, QMainWindow
from PyQt4.QtSql import QSqlDatabase

from gemUI import Ui_gem
from mail import MailUI
from absence import AbsenceUI
from intervenant import IntervenantUI
from config import ConfigUI, Config

version = "0.1.0"

class GestionAbsences(QMainWindow):
    def __init__(self, parent=None):
        super(GestionAbsences, self).__init__(parent)
        settings = QSettings()
        self.restoreGeometry(settings.value("mainWindowGeometry").toByteArray())

        self.createWidgets()
        self.conf = Config.getInstance()
        self.__connectSlots()

        self.restoreState(settings.value("mainWindowState").toByteArray())

    def __connectSlots(self):
        u"""Connecte les signaux de l'ui principale"""
        self.mailTab.majBdd.connect(self.absenceTab.miseAJour)
        self.absenceTab.majBdd.connect(self.mailTab.miseAJour)
        self.intervenantTab.majBdd.connect(self.mailTab.miseAJour)
        self.intervenantTab.majBdd.connect(self.absenceTab.miseAJour)
        self.configTab.majDuree.connect(self.mailTab.miseAJour)

        self.mailTab.notification.connect(self.__ui.statusbar.showMessage)

    def createWidgets(self):
        self.__ui = Ui_gem()
        self.__ui.setupUi(self)
        self.__ajouteOnglets(self.__ui.tabWidget)

    def __ajouteOnglets(self, tabWidget):
        u"""Construit et attache les onglets au tab widget"""
        self.mailTab = MailUI(self)
        tabWidget.addTab(self.mailTab, "Emails")
        self.absenceTab = AbsenceUI(self)
        tabWidget.addTab(self.absenceTab, "Absences")
        self.intervenantTab = IntervenantUI(self)
        tabWidget.addTab(self.intervenantTab, "Intervenants")
        self.configTab = ConfigUI(self)
        tabWidget.addTab(self.configTab, "Configuration")

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue("mainWindowGeometry", self.saveGeometry())
        settings.setValue("mainWindowState", self.saveState())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("nicolas.carrier")
    QCoreApplication.setApplicationVersion(version)
    QCoreApplication.setApplicationName("gem")

    locale = QLocale.system().name()
    translator = QTranslator()
    translator.load(QString("qt_") + locale,
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
    del ui
    sys.exit(ret)
