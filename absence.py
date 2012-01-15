#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["AbsenceUI"]

from PySide.QtCore import Signal, Qt, SLOT, Slot, QEvent, QDate
from PySide.QtGui import QWidget, QMessageBox, QMenu, QKeySequence
from PySide.QtSql import QSqlTableModel, QSqlRelationalTableModel, QSqlRelation

from tableUI import Ui_table
from specializeddelegate import SpecializedDelegate

class AbsenceSqlRelationalTableModel(QSqlRelationalTableModel):
    def data(self, index, role):
        if (role == Qt.TextAlignmentRole):
            return Qt.AlignCenter
        return QSqlRelationalTableModel.data(self, index, role)


class AbsenceUI(QWidget):
    """Classe chargée de l'interface de gestion des absences"""

# signaux
    u"""Signal envoyé quand la base a été modifiée"""
    majBdd = Signal()

    def __init__(self, parent=None):
        super(AbsenceUI, self).__init__(parent)
        self.__createWidgets()
        self.__ui.tv.installEventFilter(self)

    def __createWidgets(self):
        u"""Créée les widgets de l'interface graphique"""
        self.__ui = Ui_table()
        self.__ui.setupUi(self)

        self.__modele = AbsenceSqlRelationalTableModel(self)
        self.__modele.setTable("absence")
        self.__modele.setRelation(2, QSqlRelation("intervenant", "id", "nom"))
        self.__modele.setHeaderData(1, Qt.Horizontal, "Jour")
        self.__modele.setHeaderData(2, Qt.Horizontal, "Intervenant")
        self.__modele.setHeaderData(3, Qt.Horizontal, u"Régularisée")
        self.__modele.setHeaderData(4, Qt.Horizontal, u"Dernier mail")
        self.__modele.setHeaderData(5, Qt.Horizontal, u"Emails envoyés")
        self.__modele.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.__modele.select()

        self.__ui.tv.setModel(self.__modele)
        self.__ui.tv.setColumnHidden(0, True)
        self.__ui.tv.setItemDelegate(SpecializedDelegate(self,
            [1, 4], # Champs dates
            [3], # Champs booléens
            [5], # Champs nombres
            #[]
            [4]     # Champs en lecture seule
        ))
        self.__ui.tv.sortByColumn(1, Qt.AscendingOrder)
        self.__ui.tv.resizeColumnsToContents()

        # Connexions
        self.__ui.pbNouveau.clicked.connect(self.nouveau)
        self.__ui.pbSupprimer.clicked.connect(self.supprimer)
        self.__modele.dataChanged.connect(self.__emitMajBdd)
        self.__modele.rowsInserted.connect(self.__emitMajBdd)
        self.__modele.rowsRemoved.connect(self.__emitMajBdd)

        self.__ui.tv.customContextMenuRequested.connect(self.__menu)

    def __menu(self, pos):
        u"""Slot d'apparition du menu contextuel"""
        menu = QMenu()
        menu.addAction("Supprimer", self, SLOT("supprimer()"),
           QKeySequence.Delete)
        menu.addAction("Nouveau", self, SLOT("nouveau()"),
           QKeySequence.New)
        menu.exec_(self.__ui.tv.mapToGlobal(pos))

    def __emitMajBdd(self):
        u"""Informe les observers que la BDD a été modifiée"""
        self.majBdd.emit()

    def keyPressEvent(self, event):
        u"""Filtre les appuis de touches pour la création et la suppression"""
        if event.type() == QEvent.KeyPress:
            if event.matches(QKeySequence.New):
                self.nouveau()
            elif event.key() == Qt.Key_Delete:
                self.supprimer()

# slots
    @Slot()
    def supprimer(self):
        u"""Supprime une absence de la liste, après confirmation"""
        index = self.__ui.tv.currentIndex()
        row = index.row()
        if -1 == index:
            QMessageBox.information(self,
                u"Cliquer sur l'absence à supprimer",
                u"Veuiller cliquer sur une absence avant de cliquer sur " +
                u"supprimer")
        else:
            nom = index.sibling(row, 2).data()
            date = QDate.fromString(index.sibling(row, 1).data(), Qt.ISODate)
            supprimer = QMessageBox.question(self, "Confirmer la suppression",
                u"Supprimer l'absence de " + nom + " du " +
                date.toString(Qt.SystemLocaleLongDate) + " ?",
                QMessageBox.Yes | QMessageBox.No)
            if supprimer == QMessageBox.Yes:
                self.__modele.removeRow(row)

    @Slot()
    def nouveau(self):
        u"""Crée une nouvelle absence vide"""
        self.__modele.insertRow(0)
        index = self.__modele.index(0, 3)
        self.__modele.setData(index, "non")
        index = self.__modele.index(0, 5)
        self.__modele.setData(index, "0")

    def miseAJour(self):
        u"""Écrit les données en base et relit les données"""
        self.__modele.submitAll()
        self.__modele.select()

if __name__ == "__main__":
    u"""Main de test"""
    import sys
    from PySide.QtGui import QApplication
    from PySide.QtCore import QLibraryInfo, QLocale, QTranslator
    from PySide.QtSql import QSqlDatabase

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

    ui = AbsenceUI()
    ui.show()
    ret = app.exec_()
    sys.exit(ret)
