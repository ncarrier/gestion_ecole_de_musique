#!/usr/bin/python -t
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import Qt, SIGNAL, QDate, QLocale, QTranslator, QString
from PyQt4.QtCore import QLibraryInfo, QRect

from PyQt4.QtGui import QApplication, QTabWidget, QDesktopWidget, QMessageBox
from PyQt4.QtGui import QInputDialog, QLineEdit, QAbstractItemView

from PyQt4.QtSql import QSqlTableModel, QSqlRelation, QSqlRelationalTableModel
from PyQt4.QtSql import QSqlQuery, QSqlDatabase

from gestionAbsencesUI import Ui_gestionAbsences
from mail import MailUI
from absencedelegate import AbsenceDelegate
from config import Config
from config import ConfigUI


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

        # La modification de données sur un onglet fait raffraîchir les autres
        # TODO à activer quand les tabs intervenant et absence auront ete
        # refactorés
#        self.connect(self.mailTab.majBdd, SIGNAL("majBdd(int)"),
#                     self.absenceTab.miseAJour)
#        self.connect(self.mailTab.majBdd, SIGNAL("majBdd(int)"),
#                     self.intervenantTab.miseAJour)
#        self.connect(self.absenceTab.majBdd, SIGNAL("majBdd(int)"),
#                     self.emailTab.miseAJour)
#        self.connect(self.absenceTab.majBdd, SIGNAL("majBdd(int)"),
#                     self.intervenantTab.miseAJour)
#        self.connect(self.intervenantTab.majBdd, SIGNAL("majBdd(int)"),
#                     self.emailTab.miseAJour)
#        self.connect(self.intervenantTab.majBdd, SIGNAL("majBdd(int)"),
#                     self.absenceTab.miseAJour)

    def createWidgets(self):
        self.ui = Ui_gestionAbsences()
        self.ui.setupUi(self)

        # Ajout des onglets
        self.mailTab = MailUI(self)
        self.addTab(self.mailTab, "Email")
        self.configTab = ConfigUI(self)
        self.addTab(self.configTab, "Configuration")

        # Gros bazard à refactorer
        self.modelIntervenant = QSqlTableModel(self)
        self.modelIntervenant.setTable("intervenant")

        self.modelIntervenant.setHeaderData(1, Qt.Horizontal, "Nom")
        self.modelIntervenant.setHeaderData(2, Qt.Horizontal, u"Téléphone")
        self.modelIntervenant.setHeaderData(3, Qt.Horizontal, "Email")
        self.modelIntervenant.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.modelIntervenant.select()

        self.ui.tvIntervenants.setModel(self.modelIntervenant)
        self.ui.tvIntervenants.setColumnHidden(0, True)
        self.ui.tvIntervenants.sortByColumn(1, Qt.AscendingOrder)
        self.ui.tvIntervenants.resizeColumnsToContents()

        self.connect(self.ui.nouveauIntervenant, SIGNAL("clicked()"),
            self.nouveauIntervenant)
        self.connect(self.ui.supprimerIntervenant, SIGNAL("clicked()"),
            self.supprimerIntervenant)

        self.modelAbsence = QSqlRelationalTableModel(self)
        self.modelAbsence.setTable("absence")
        self.modelAbsence.setRelation(2, QSqlRelation("intervenant", "id",
            "nom"))

        self.modelAbsence.setHeaderData(1, Qt.Horizontal, "Jour")
        self.modelAbsence.setHeaderData(2, Qt.Horizontal, "Intervenant")
        self.modelAbsence.setHeaderData(3, Qt.Horizontal, u"Régularisée")
        self.modelAbsence.setHeaderData(4, Qt.Horizontal, u"Email envoyé")
        self.modelAbsence.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.modelAbsence.select()

        self.ui.tvAbsences.setModel(self.modelAbsence)
        self.ui.tvAbsences.setColumnHidden(0, True)
        self.ui.tvAbsences.setItemDelegate(AbsenceDelegate(self, [1], [3, 4]))
        self.ui.tvAbsences.sortByColumn(1, Qt.AscendingOrder)
        self.ui.tvAbsences.resizeColumnsToContents()
        self.ui.tvAbsences.setEditTriggers(QAbstractItemView.AllEditTriggers)

        self.connect(self.ui.nouveauAbsence, SIGNAL("clicked()"),
            self.nouveauAbsence)
        self.connect(self.ui.supprimerAbsence, SIGNAL("clicked()"),
            self.supprimerAbsence)
        self.connect(self.modelIntervenant,
            SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
            self.refresh)
        self.connect(self.modelAbsence,
            SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
            self.refresh)

    def supprimerAbsence(self):
        index = self.ui.tvAbsences.currentIndex()
        row = index.row()
        if -1 == index:
            QMessageBox.information(self,
                    u"Cliquer sur l'absence à supprimer",
                    u"Veuiller cliquer sur l'une des cases" +
                    u"de l'absence à supprimer avant " +
                    u"de cliquer sur le bouton supprimer")
        else:
            date = index.sibling(row, 1).data().toDate()
            supprimer = QMessageBox.question(self, "Confirmer la suppression",
                u"Supprimer l'absence de " +
                index.sibling(row, 2).data().toString() + " du " +
                date.toString(Qt.SystemLocaleLongDate) +
                " ?", QMessageBox.Yes | QMessageBox.No)
            if supprimer == QMessageBox.Yes:
                self.modelAbsence.removeRows(row, 1)

    def supprimerIntervenant(self):
        index = self.ui.tvIntervenants.currentIndex()
        row = index.row()
        if -1 == index:
            QMessageBox.information(self,
                    u"Cliquer sur l'intervenant à supprimer",
                    u"Veuiller cliquer sur l'une des cases" +
                    u"de l'intervenant à supprimer avant " +
                    u"de cliquer sur le bouton supprimer")
        else:
            supprimer = QMessageBox.question(self, "Confirmer la suppression",
                    u"Êtes-vous sûr de vouloir supprimer " +
                    u"l'intervenant " +
                    index.sibling(row, 1).data().toString()
                    + " ? ",
                    QMessageBox.Yes | QMessageBox.No)
            if supprimer == QMessageBox.Yes:
                self.modelIntervenant.removeRows(row, 1)

    def nouveauAbsence(self):
        self.modelAbsence.insertRow(0)
        index = self.modelAbsence.index(0, 3)
        self.modelAbsence.setData(index, "false")
        index = self.modelAbsence.index(0, 4)
        self.modelAbsence.setData(index, "false")

    def nouveauIntervenant(self):
        self.modelIntervenant.insertRows(0)

    def refresh(self, tl=None, br=None):
        self.modelIntervenant.submitAll()
        self.modelAbsence.submitAll()

        self.modelIntervenant.select()
        self.modelAbsence.select()
        self.miseAJour()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    locale = QLocale.system().name()
    translator = QTranslator()
    translator.load(QString("qt_") + locale,
        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)

    # Configuration de la base de données
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName('private/gestionAbsences.db')
    db.open()

    # Création de l'ui principale et boucle principale
    ui = GestionAbsences()
    ui.setGeometry(QRect(100, 20, 700, 400))
    ui.show()
    ret = app.exec_()
    ui.conf.close()
    sys.exit(ret)
