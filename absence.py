#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["AbsenceUI"]

from PySide.QtCore import Qt, QDate
from PySide.QtSql import QSqlTableModel, QSqlRelationalTableModel, QSqlRelation

from table import TableUI
from specializeddelegate import SpecializedDelegate

class AbsenceSqlRelationalTableModel(QSqlRelationalTableModel):
    def data(self, index, role):
        if (role == Qt.TextAlignmentRole):
            return Qt.AlignCenter
        return QSqlRelationalTableModel.data(self, index, role)


class AbsenceUI(TableUI):
    """Classe chargée de l'interface de gestion des absences"""

    def setupModel(self):
        self._modele = AbsenceSqlRelationalTableModel(self)
        self._modele.setTable("absence")
        self._modele.setRelation(2, QSqlRelation("intervenant", "id", "nom"))
        self._modele.setHeaderData(1, Qt.Horizontal, "Jour")
        self._modele.setHeaderData(2, Qt.Horizontal, "Intervenant")
        self._modele.setHeaderData(3, Qt.Horizontal, u"Régularisée")
        self._modele.setHeaderData(4, Qt.Horizontal, u"Dernier mail")
        self._modele.setHeaderData(5, Qt.Horizontal, u"Emails envoyés")
        self._modele.setEditStrategy(QSqlTableModel.OnFieldChange)
        self._modele.select()

        self._ui.tv.setModel(self._modele)
        self._ui.tv.setItemDelegate(SpecializedDelegate(self,
            [1, 4], # Champs dates
            [3], # Champs booléens
            [5], # Champs nombres
#            []
            [4]     # Champs en lecture seule
        ))

    def msgValidationNouveau(self):
        u"""Message d'erreur quand on veut créer deux items de suite"""
        return u"Valider l'absence avant d'en recréer une"

    def preparationNouveau(self):
        u"""Insère des données par défaut dans un item tout juste créé"""
        index = self._modele.index(0, 3)
        self._modele.setData(index, "non")
        index = self._modele.index(0, 5)
        self._modele.setData(index, "0")

    def titreErrSuppression(self):
        return u"Cliquer sur l'absence à supprimer"

    def msgErrSuppression(self):
        return u"""Veuiller cliquer sur une absence avant de cliquer sur \
supprimer"""

    def msgSuppression(self, index):
        row = index.row()
        nom = index.sibling(row, 2).data()
        date = QDate.fromString(index.sibling(row, 1).data(), Qt.ISODate)
        return u"Supprimer l'absence de " + nom + " du " + date.toString(Qt.SystemLocaleLongDate) + " ?"

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
