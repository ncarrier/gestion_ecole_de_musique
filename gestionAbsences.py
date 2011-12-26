#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from gestionAbsencesUI import Ui_gestionAbsences
from mail import MailComposer
from date import DateDelegate

class GestionAbsences(QTabWidget):
	def __init__(self, parent=None):
		super(GestionAbsences, self).__init__(parent)
		screenIndex = 0
		monEcran = QDesktopWidget()
		monEcran.screenGeometry(screenIndex).width()
		monEcran.screenGeometry(screenIndex).height()
		self.createWidgets()
		self.verifierAbsences()

	def createWidgets(self):
		self.ui = Ui_gestionAbsences()
		self.ui.setupUi(self)

		self.modelIntervenant = QSqlTableModel(self)
		self.modelIntervenant.setTable("intervenant")

		self.modelIntervenant.setHeaderData(1, Qt.Horizontal, "Nom")
		self.modelIntervenant.setHeaderData(2, Qt.Horizontal,
				u"Téléphone")
		self.modelIntervenant.setHeaderData(3, Qt.Horizontal, "Email")
		self.modelIntervenant.select()

		self.ui.tvIntervenants.setModel(self.modelIntervenant)
		self.ui.tvIntervenants.setColumnHidden(0, True)
		self.ui.tvIntervenants.sortByColumn(1, Qt.AscendingOrder)
		self.ui.tvIntervenants.resizeColumnsToContents()

		self.connect(self.ui.nouveauIntervenant, SIGNAL("clicked()"),
				self.nouveauIntervenant)
		self.connect(self.ui.supprimerIntervenant, SIGNAL("clicked()"),
				self.supprimerIntervenant)
		self.connect(self.ui.tvIntervenants.selectionModel(),
				SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
				self.selectCurrentIntervenant)

		self.modelAbsence = QSqlRelationalTableModel(self)
		self.modelAbsence.setTable("absence")
		self.modelAbsence.setRelation(2, QSqlRelation("intervenant",
			"id", "nom"))
		self.modelAbsence.setRelation(3, QSqlRelation("booleen", "id",
			"libelle"))
		self.modelAbsence.setRelation(4, QSqlRelation("booleen", "id",
			"libelle"))

		self.modelAbsence.setHeaderData(1, Qt.Horizontal, "Jour")
		self.modelAbsence.setHeaderData(2, Qt.Horizontal, "Intervenant")
		self.modelAbsence.setHeaderData(3, Qt.Horizontal, u"Régularisée")
		self.modelAbsence.setHeaderData(4, Qt.Horizontal, u"Email envoyé")
		self.modelAbsence.select()

		self.ui.tvAbsences.setModel(self.modelAbsence)
		self.ui.tvAbsences.setColumnHidden(0, True)
		self.ui.tvAbsences.setItemDelegate(DateDelegate(self, 1))
		self.ui.tvAbsences.resizeColumnsToContents()

		self.connect(self.ui.nouveauAbsence, SIGNAL("clicked()"), self.nouveauAbsence)
		self.connect(self.ui.supprimerAbsence, SIGNAL("clicked()"), self.supprimerAbsence)
		self.connect(self.ui.tvAbsences.selectionModel(),
				SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
				self.selectCurrentAbsence)

		self.connect(self.ui.cbAbsence, SIGNAL("currentIndexChanged(int)"), self.updateMailComposer)

	def supprimerAbsence(self):
		index = self.ui.tvAbsences.currentIndex().row()
		if -1 == index:
			QMessageBox.information(self,
					u"Cliquer sur la ligne à supprimer",
					u"Veuiller cliquer sur l'une des cases" +
					u"de l'absence à supprimer avant " +
					u"de cliquer sur le bouton supprimer")
		else:
			supprimer = QMessageBox.question(self, "Confirmer la suppression",
					u"Êtes-vous sûr de vouloir supprimer " +
					"l'absence " + str(index),
					QMessageBox.Yes | QMessageBox.No);
			if supprimer == QMessageBox.Yes:
				self.modelAbsence.removeRows(index, 1)

	def supprimerIntervenant(self):
		index = self.ui.tvIntervenants.currentIndex().row()
		if -1 == index:
			QMessageBox.information(self,
					u"Cliquer sur la ligne à supprimer",
					u"Veuiller cliquer sur l'une des cases" +
					u"de l'intervenant à supprimer avant " +
					u"de cliquer sur le bouton supprimer")
		else:
			supprimer = QMessageBox.question(self, "Confirmer la suppression",
					u"Êtes-vous sûr de vouloir supprimer l'interv" +
					"enant " + str(index), QMessageBox.Yes |
					QMessageBox.No);
			if supprimer == QMessageBox.Yes:
				self.modelIntervenant.removeRows(index, 1)

	def nouveauAbsence(self):
		self.modelAbsence.insertRows(0, 1)

	def nouveauIntervenant(self):
		self.modelIntervenant.insertRows(0, 1)

	def selectCurrentIntervenant(self, selected, deselected):
		"""Sélectionne la ligne correspondant à l'intervenant sur
		lequel on vient de cliquer"""
		row = self.ui.tvIntervenants.currentIndex().row()
		if row != -1:
			self.ui.tvIntervenants.selectRow(row)

	def selectCurrentAbsence(self, selected, deselected):
		"""Sélectionne la ligne correspondant à l'absence sur
		laquelle on vient de cliquer"""
		row = self.ui.tvAbsences.currentIndex().row()
		if row != -1:
			self.ui.tvAbsences.selectRow(row)

	def closeEvent(self, event):
		self.modelIntervenant.submitAll()
		self.modelAbsence.submitAll()

		event.accept()

	def verifierAbsences(self):
		# Vérification des mails à envoyer
		req = QSqlQuery()
		date = QDate.currentDate()
		date = date.addMonths(-1)
		date = date.toString(Qt.ISODate)

		sql = "SELECT COUNT(*) FROM absence "
		sql += "WHERE mail_envoye=0 AND regularisee=0 AND jour <= '" + date + "' "
		if req.exec_(sql):
			req.next()
			nbMails = int(req.record().value(0).toString())
		else:
			print "SQL error"
			return
		label = str(nbMails) + " absence"
		if nbMails == 0:
			label += " :"
			self.ui.lAbsence.setText(label)
			self.ui.cbAbsence.setEnabled(False)
			self.ui.pbEnvoyer.setEnabled(False)
			self.ui.leSujet.setEnabled(False)
			self.ui.teCorps.setEnabled(False)
			return
		if nbMails > 1:
			label += "s"
		label += " :"
		self.ui.lAbsence.setText(label)

		sql = "SELECT jour, nom, email FROM absence "
		sql += "JOIN intervenant ON absence.id_intervenant=intervenant.id "
		sql += "WHERE mail_envoye=0 AND regularisee=0 AND jour <= '" + date + "' "
		if not req.exec_(sql):
			print req.lastError().text()
			print req.lastQuery()
			print "Erreur de requête"
		else:
			self.__absences = []
			while (req.next()):
				absence = {}
				rec = req.record()
				absence = {}
				absence["date"] = QDate.fromString(rec.value(0).toString(),
						Qt.ISODate)
				absence["nom"] = rec.value(1).toString()
				absence["adresse"] = rec.value(2).toString()
				self.__absences.append(absence)
				item = absence["nom"] + " le "
				item += absence["date"].toString(Qt.SystemLocaleLongDate)
				self.ui.cbAbsence.addItem(item)

	def updateMailComposer(self, index):
		date = self.__absences[index]["date"].toString(Qt.SystemLocaleLongDate)
		sujet = "Absence du " + date

		self.ui.leSujet.setText(sujet)
		self.ui.teCorps.setText(u"""Bonjour,
Vous avez été absent le """ + date + u""" et à ce jour, il semble que vous ne l'ayez ni rattrapé ni justifiée.

Cordialement,
Aurore jedrzejak""")


if __name__ == "__main__":
	app = QApplication(sys.argv)

	# Configuration de l'envoi des mails
	ms = MailComposer("private/config")

	# Configuration de la base de données
	db = QSqlDatabase.addDatabase("QSQLITE")
	db.setDatabaseName('private/gestionAbsences.db')
	db.open()

	# Création de l'ui principale et boucle principale
	ui = GestionAbsences()
	ui.setGeometry(QRect(100, 20, 700, 400))
	ui.show()
	ret = app.exec_()

	sys.exit(ret)
