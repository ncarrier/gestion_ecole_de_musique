#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["IntervenantUI"]

from PyQt4.QtCore import pyqtSignal, SIGNAL, Qt
from PyQt4.QtGui import QWidget, QMessageBox
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

    def __createWidgets(self):
        """Créée les widgets de l'interface graphique"""
        self.__ui = Ui_table()
        self.__ui.setupUi(self)
        # Gros bazard à refactorer
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

        self.connect(self.__ui.pbNouveau, SIGNAL("clicked()"), self.__nouveau)
        self.connect(self.__ui.pbSupprimer, SIGNAL("clicked()"),
            self.__supprimer)

        self.connect(self.__modele,
            SIGNAL("dataChanged(QModelIndex, QModelIndex)"), self.__emitMajBdd)

    def __emitMajBdd(self):
        u"""Informe les observers que la BDD a été modifiée"""
        self.majBdd.emit()

    def __supprimer(self):
        """Supprime un intervenant de la liste, après confirmation"""
        index = self.__ui.tv.currentIndex()
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
                self.__modele.removeRows(row, 1)

    def __nouveau(self):
        """Crée un nouvel intervenant vide"""
        self.__modele.insertRow(0)

# slots
    def miseAJour(self):
        """Écrit les données en base et relit les données"""
        self.__modele.submitAll()
        self.__modele.select()

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

    ui = IntervenantUI()
    ui.show()
    ret = app.exec_()
    sys.exit(ret)
