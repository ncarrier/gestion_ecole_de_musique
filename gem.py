#!/usr/bin/python -t
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import QLocale, QTranslator, QString, QLibraryInfo, QRect

from PyQt4.QtGui import QApplication, QTabWidget, QDesktopWidget

from PyQt4.QtSql import QSqlDatabase

from gemUI import Ui_gestionAbsences
from mail import MailUI
from absence import AbsenceUI
from intervenant import IntervenantUI
from config import ConfigUI, Config


class GestionAbsences(QTabWidget):
    def __init__(self, parent=None):
        super(GestionAbsences, self).__init__(parent)
        screenIndex = 0
        monEcran = QDesktopWidget()
        monEcran.screenGeometry(screenIndex).width()
        monEcran.screenGeometry(screenIndex).height()
        self.createWidgets()
        self.conf = Config.getInstance()
        self.mailTab.miseAJour()

        self.mailTab.majBdd.connect(self.absenceTab.miseAJour)
        self.absenceTab.majBdd.connect(self.mailTab.miseAJour)
        self.intervenantTab.majBdd.connect(self.mailTab.miseAJour)
        self.intervenantTab.majBdd.connect(self.absenceTab.miseAJour)
        self.configTab.majDuree.connect(self.mailTab.miseAJour)

    def createWidgets(self):
        self.__ui = Ui_gestionAbsences()
        self.__ui.setupUi(self)

        # Ajout des onglets
        self.mailTab = MailUI(self)
        self.addTab(self.mailTab, "Emails")
        self.absenceTab = AbsenceUI(self)
        self.addTab(self.absenceTab, "Absences")
        self.intervenantTab = IntervenantUI(self)
        self.addTab(self.intervenantTab, "Intervenants")
        self.configTab = ConfigUI(self)
        self.addTab(self.configTab, "Configuration")


if __name__ == "__main__":
    app = QApplication(sys.argv)

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
    ui.setGeometry(QRect(100, 20, 700, 400))
    ui.show()
    ret = app.exec_()
    ui.conf.close()
    sys.exit(ret)
