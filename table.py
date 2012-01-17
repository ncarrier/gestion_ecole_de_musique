# -*- coding: utf-8 -*-
'''
Created on 16 janv. 2012

@author: nicolas
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["TableUI"]

from PySide.QtCore import Signal, Qt, SLOT, Slot, QEvent
from PySide.QtGui import QWidget, QMessageBox, QMenu, QKeySequence

from tableUI import Ui_table


class TableUI(QWidget):
    """Classe chargée de l'affichage d'une table de bdd"""

# signaux
    u"""Signal envoyé quand la base a été modifiée"""
    majBdd = Signal()
    u"""Signal envoyé pour notifier d'un événement"""
    notification = Signal(str, int)
    u"""Durée de vie des messages de notification"""
    DUREE_MESSAGE = 10000

    def __init__(self, parent=None):
        super(TableUI, self).__init__(parent)
        self.__createWidgets()
        self._ui.tv.installEventFilter(self)

    def __createWidgets(self):
        u"""Créée les widgets de l'interface graphique"""
        self._ui = Ui_table()
        self._ui.setupUi(self)

        self.setupModel()
        self._ui.tv.setColumnHidden(0, True)
        self._ui.tv.sortByColumn(1, Qt.AscendingOrder)
        self._ui.tv.resizeColumnsToContents()

        # Connexions
        self._ui.pbNouveau.clicked.connect(self.nouveau)
        self._ui.pbSupprimer.clicked.connect(self.supprimer)
        self._ui.tv.customContextMenuRequested.connect(self.__menu)
        self._modele.dataChanged.connect(self.emitMajBdd)
        self._modele.rowsInserted.connect(self.emitMajBdd)
        self._modele.rowsRemoved.connect(self.emitMajBdd)


    def __menu(self, pos):
        u"""Slot d'apparition du menu contextuel"""
        menu = QMenu()
        menu.addAction("Supprimer", self, SLOT("supprimer()"),
           QKeySequence.Delete)
        menu.addAction("Nouveau", self, SLOT("nouveau()"), QKeySequence.New)
        menu.exec_(self._ui.tv.mapToGlobal(pos))

    def emitMajBdd(self):
        u"""Informe les observers que la BDD a été modifiée"""
        self.majBdd.emit()

    def keyPressEvent(self, event):
        u"""Filtre les appuis de touches pour la création et la suppression"""
        if event.type() == QEvent.KeyPress:
            if event.matches(QKeySequence.New):
                self.nouveau()
            elif event.key() == Qt.Key_Delete:
                self.supprimer()

# méthodes à redéfinir
    def setupModel(self):
        u"""Définit et configure le modèle sous-jacent à la table"""
        pass

    def msgValidationNouveau(self):
        u"""Message d'erreur quand on veut créer deux items de suite"""
        return u"Valider l'item avant d'en recréer un"

    def preparationNouveau(self):
        u"""Insère des données par défaut dans un item tout juste créé"""
        pass

    def msgErrSuppression(self):
        u"Message d'erreur de suppression quand aucun item n'est sélectionné"
        return u"Veuiller cliquer sur un item avant de cliquer sur supprimer"

    def titreErrSuppression(self):
        u"Titre du message d'erreur quand aucun item n'est sélectionné"
        return u"Cliquer sur l'item à supprimer"

    def msgSuppression(self, index):
        u"Message de confirmation de suppression d'un item"
        return u"Voulez-vous supprimer l'item à la ligne " + str(index.row()) + " ?"

    def preSupprVerification(self, index):
        u"""Vérification à effectuer avant d'autoriser à supprimer un item
        
        Renvoit False si la suppression est interdite
        
        """
        return True
# \\ méthodes à redéfinir

# slots
    @Slot()
    def supprimer(self):
        u"""Supprime un item de la liste, après confirmation"""
        index = self._ui.tv.currentIndex()
        if not self.preSupprVerification(index):
            return
        row = index.row()
        if -1 == row:
            QMessageBox.information(self, self.titreErrSuppression(),
                self.msgErrSuppression())
        else:
            supprimer = QMessageBox.question(self, "Confirmer la suppression",
                self.msgSuppression(index), QMessageBox.Yes | QMessageBox.No)
            if supprimer == QMessageBox.Yes:
                self._modele.removeRow(row)

    @Slot()
    def nouveau(self):
        u"""Crée une nouvelle absence vide"""
        if self._modele.index(0, 0).data() != 0:
            self._modele.insertRow(0)
            self.preparationNouveau()
        else:
            self.notification.emit(self.msgValidationNouveau(),
                TableUI.DUREE_MESSAGE)

    def miseAJour(self):
        u"""Écrit les données en base et relit les données"""
        self._modele.submitAll()
        self._modele.select()
