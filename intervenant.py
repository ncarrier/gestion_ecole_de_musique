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
        self.ui = Ui_table()
        self.ui.setupUi(self)
        # Gros bazard à refactorer
        self.modelIntervenant = QSqlTableModel(self)
        self.modelIntervenant.setTable("intervenant")

        self.modelIntervenant.setHeaderData(1, Qt.Horizontal, "Nom")
        self.modelIntervenant.setHeaderData(2, Qt.Horizontal, u"Téléphone")
        self.modelIntervenant.setHeaderData(3, Qt.Horizontal, "Email")
        self.modelIntervenant.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.modelIntervenant.select()

        self.ui.tv.setModel(self.modelIntervenant)
        self.ui.tv.setColumnHidden(0, True)
        self.ui.tv.sortByColumn(1, Qt.AscendingOrder)
        self.ui.tv.resizeColumnsToContents()

        self.connect(self.ui.pbNouveau, SIGNAL("clicked()"),
            self.nouveauIntervenant)
        self.connect(self.ui.pbSupprimer, SIGNAL("clicked()"),
            self.supprimerIntervenant)

        self.connect(self.modelIntervenant,
            SIGNAL("dataChanged(QModelIndex, QModelIndex)"), self.emitMajBdd)

    def emitMajBdd(self):
        u"""Informe les observers que la BDD a été modifiée"""
        self.majBdd.emit()

    def supprimerIntervenant(self):
        """Supprime un intervenant de la liste, après confirmation"""
        index = self.ui.tv.currentIndex()
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

    def nouveauIntervenant(self):
        """Crée un nouvel intervenant vide"""
        self.modelIntervenant.insertRow(0)

    def miseAJour(self):
        self.modelIntervenant.submitAll()
        self.modelIntervenant.select()

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
