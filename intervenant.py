#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["IntervenantUI"]

from PyQt4.QtCore import pyqtSignal, Qt, QString, SLOT, pyqtSlot, QEvent
from PyQt4.QtGui import QWidget, QMessageBox, QMenu, QKeySequence
from PyQt4.QtSql import QSqlTableModel

from tableUI import Ui_table


class IntervenantUI(QWidget):
    """Classe chargée de l'interface de gestion des intervenants"""

# signaux
    u"""Signal envoyé quand la base a été modifiée"""
    majBdd = pyqtSignal()

    def __init__(self, parent=None):
        super(IntervenantUI, self).__init__(parent)
        self.__createWidgets()
        self.__ui.tv.installEventFilter(self)

    def __createWidgets(self):
        u"""Créée les widgets de l'interface graphique"""
        self.__ui = Ui_table()
        self.__ui.setupUi(self)

        self.__modele = QSqlTableModel(self)
        self.__modele.setTable("intervenant")
        self.__modele.setHeaderData(1, Qt.Horizontal, "Nom")
        self.__modele.setHeaderData(2, Qt.Horizontal, u"Téléphone")
        self.__modele.setHeaderData(3, Qt.Horizontal, "Email")
        self.__modele.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.__modele.select()

        self.__ui.tv.setModel(self.__modele)
        self.__ui.tv.setColumnHidden(0, True)
        self.__ui.tv.sortByColumn(1, Qt.AscendingOrder)
        self.__ui.tv.resizeColumnsToContents()

        # Connexions
        self.__ui.pbNouveau.clicked.connect(self.__nouveau)
        self.__ui.pbSupprimer.clicked.connect(self.__supprimer)
        self.__modele.dataChanged.connect(self.__emitMajBdd)
        self.__modele.rowsInserted.connect(self.__emitMajBdd)
        self.__modele.rowsRemoved.connect(self.__emitMajBdd)

        self.__ui.tv.customContextMenuRequested.connect(self.__menu)

    def __menu(self, pos):
        u"""Slot d'apparition du menu contextuel"""
        menu = QMenu()
        menu.addAction(QString("Supprimer"), self, SLOT("__supprimer()"),
           QKeySequence.Delete)
        menu.addAction(QString("Nouveau"), self, SLOT("__nouveau()"),
           QKeySequence.New)
        menu.exec_(self.__ui.tv.mapToGlobal(pos))

    def __emitMajBdd(self):
        u"""Informe les observers que la BDD a été modifiée"""
        self.majBdd.emit()

    def keyPressEvent(self, event):
        u"""Filtre les appuis de touches pour la création et la suppression"""
        if event.type() == QEvent.KeyPress:
            if event.matches(QKeySequence.New):
                self.__nouveau()
            elif event.key() == Qt.Key_Delete:
                self.__supprimer()

# slots
    @pyqtSlot()
    def __supprimer(self):
        """Supprime un intervenant de la liste, après confirmation"""
        index = self.__ui.tv.currentIndex()
        row = index.row()
        if -1 == index:
            QMessageBox.information(self,
                u"Cliquer sur l'intervenant à supprimer",
                u"Veuiller cliquer sur un intervenant avant de cliquer sur " +
                u"supprimer")
        else:
            supprimer = QMessageBox.question(self, "Confirmer la suppression",
                u"Êtes-vous sûr de vouloir supprimer l'intervenant " +
                index.sibling(row, 1).data().toString() + " ? ",
                QMessageBox.Yes | QMessageBox.No)
            if supprimer == QMessageBox.Yes:
                self.__modele.removeRow(row)

    @pyqtSlot()
    def __nouveau(self):
        u"""Crée un nouvel intervenant vide"""
        self.__modele.insertRow(0)

    def miseAJour(self):
        u"""Écrit les données en base et relit les données"""
        self.__modele.submitAll()
        self.__modele.select()

if __name__ == "__main__":
    u"""Main de test"""
    import sys
    from PyQt4.QtGui import QApplication
    from PyQt4.QtCore import QLibraryInfo, QLocale, QTranslator
    from PyQt4.QtSql import QSqlDatabase

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

    ui = IntervenantUI()
    ui.show()
    ret = app.exec_()
    sys.exit(ret)
