#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["IntervenantUI"]

from PySide.QtCore import Qt
from PySide.QtSql import QSqlTableModel

from table import TableUI


class IntervenantUI(TableUI):
    """Classe chargée de l'interface de gestion des intervenants"""

    def setupModel(self):
        u"""Définit et configure le modèle sous-jacent à la table"""
        self._modele = QSqlTableModel(self)
        self._modele.setTable("intervenant")
        self._modele.setHeaderData(1, Qt.Horizontal, "Nom")
        self._modele.setHeaderData(2, Qt.Horizontal, u"Téléphone")
        self._modele.setHeaderData(3, Qt.Horizontal, "Email")
        self._modele.setEditStrategy(QSqlTableModel.OnFieldChange)
        self._modele.select()

        self._ui.tv.setModel(self._modele)

    def msgValidationNouveau(self):
        u"""Message d'erreur quand on veut créer deux items de suite"""
        return u"Valider l'intervenant avant d'en recréer un nouveau"

    def titreErrSuppression(self):
        return u"Cliquer sur l'intervenant à supprimer"

    def msgErrSuppression(self):
        return u"""Veuiller cliquer sur un intervenant avant de cliquer sur \
supprimer"""

    def msgSuppression(self, index):
        return u"Êtes-vous sûr de vouloir supprimer l'intervenant " + index.sibling(index.row(), 1).data() + " ? "

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

    ui = IntervenantUI()
    ui.show()
    ret = app.exec_()
    sys.exit(ret)
