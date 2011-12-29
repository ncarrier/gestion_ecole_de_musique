#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from gestionAbsencesUI import Ui_gestionAbsences
from mail import MailSender
from date import DateDelegate
from config import Config
from smtplib import SMTPAuthenticationError
from socket import gaierror

class GestionAbsences(QTabWidget):
	def __init__(self, parent=None):
		super(GestionAbsences, self).__init__(parent)
		screenIndex = 0
		monEcran = QDesktopWidget()
		monEcran.screenGeometry(screenIndex).width()
		monEcran.screenGeometry(screenIndex).height()
		self.createWidgets()
		self.verifierAbsences()
		self.__ms = MailSender()
		self.__conf = Config.getInstance()

	def createWidgets(self):
		self.ui = Ui_gestionAbsences()
		self.ui.setupUi(self)

		self.modelIntervenant = QSqlTableModel(self)
		self.modelIntervenant.setTable("intervenant")

		self.modelIntervenant.setHeaderData(1, Qt.Horizontal, "Nom")
		self.modelIntervenant.setHeaderData(2, Qt.Horizontal,
				u"Téléphone")
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
		self.modelAbsence.setEditStrategy(QSqlTableModel.OnFieldChange)
		self.modelAbsence.select()

		self.ui.tvAbsences.setModel(self.modelAbsence)
		self.ui.tvAbsences.setColumnHidden(0, True)
		self.ui.tvAbsences.setItemDelegate(DateDelegate(self, 1))
		self.ui.tvAbsences.resizeColumnsToContents()

		self.connect(self.ui.nouveauAbsence, SIGNAL("clicked()"), self.nouveauAbsence)
		self.connect(self.ui.supprimerAbsence, SIGNAL("clicked()"), self.supprimerAbsence)

		self.connect(self.ui.cbAbsence, SIGNAL("currentIndexChanged(int)"), self.updateMailComposer)
		self.connect(self.modelIntervenant,
				SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
				self.refresh)
		self.connect(self.modelAbsence,
				SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
				self.refresh)
		self.connect(self.ui.pbEnvoyer, SIGNAL("clicked()"),
				self.envoyerMail)
		self.connect(self.ui.pbEnvoyer, SIGNAL("clicked()"),
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
			supprimer = QMessageBox.question(self, "Confirmer la suppression",
					u"Supprimer l'absence de " +
					index.sibling(row, 2).data().toString() +
					" du " +
					index.sibling(row, 1).data().toDate().toString(Qt.SystemLocaleLongDate) +
					" ?",
					QMessageBox.Yes | QMessageBox.No);
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
					QMessageBox.Yes | QMessageBox.No);
			if supprimer == QMessageBox.Yes:
				self.modelIntervenant.removeRows(row, 1)

	def nouveauAbsence(self):
		self.modelAbsence.insertRow(0)
		index = self.modelAbsence.index(0, 3)
		self.modelAbsence.setData(index, "0")
		index = self.modelAbsence.index(0, 4)
		self.modelAbsence.setData(index, "0")


	def nouveauIntervenant(self):
		self.modelIntervenant.insertRow(0)

	def verifierAbsences(self):
		self.ui.cbAbsence.clear()

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
			self.ui.leSujet.setText("")
			self.ui.teCorps.setText("")
			self.ui.cbAbsence.setEnabled(False)
			self.ui.pbEnvoyer.setEnabled(False)
			self.ui.leSujet.setEnabled(False)
			self.ui.teCorps.setEnabled(False)
			return
		else:
			self.ui.cbAbsence.setEnabled(True)
			self.ui.pbEnvoyer.setEnabled(True)
			self.ui.leSujet.setEnabled(True)
			self.ui.teCorps.setEnabled(True)

		if nbMails > 1:
			label += "s"
		label += " :"
		self.ui.lAbsence.setText(label)

		sql = "SELECT absence.id, jour, nom, email FROM absence "
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
				absence["id"] = int(rec.value(0).toString())
				absence["date"] = QDate.fromString(rec.value(1).toString(),
						Qt.ISODate)
				absence["nom"] = rec.value(2).toString()
				absence["adresse"] = rec.value(3).toString()
				self.__absences.append(absence)
				item = absence["nom"] + " le "
				item += absence["date"].toString(Qt.SystemLocaleLongDate)
				self.ui.cbAbsence.addItem(item)

	def updateMailComposer(self, index):
		date = self.__absences[index]["date"].toString(Qt.SystemLocaleLongDate)
		sujet = "Absence du " + date

		self.ui.leSujet.setText(sujet)
		self.ui.teCorps.setText(u"""Bonjour,
Vous avez été absent le """ + date + u""" et à ce jour, il semble que vous n'ayez ni rattrapé ni justifié cette absence.

Cordialement,
Aurore JEDRZEJAK""")

	def refresh(self, tl = None, br = None):
		self.modelIntervenant.submitAll()
		self.modelAbsence.submitAll()

		self.modelIntervenant.select()
		self.modelAbsence.select()
		self.verifierAbsences()

	def envoyerMail(self):
		index = self.ui.cbAbsence.currentIndex()
		dest = str(self.__absences[index]["adresse"])
		sujet = str(self.ui.leSujet.text())
		corps = self.ui.teCorps.toPlainText().__str__()
		result = QInputDialog.getText(self, "Mot de passe",
				"Veuillez saisir le mot de passe<br /> " +
				"de votre compte de messagerie",
				QLineEdit.Password)
		password = str(result[0])
		if result[1]:
			try:
				self.__ms.envoiMail(dest, sujet, corps,
						password)
				# Mise à jour de la base
				sql = "UPDATE absence "
				sql += "SET mail_envoye=1 "
				sql += "WHERE id=" + str(self.__absences[index]["id"])
				req = QSqlQuery()
				if not req.exec_(sql):
					print "SQL error"
					print req.lastError().text()
					print req.lastQuery()
				else:
					self.refresh()
			except SMTPAuthenticationError:
				QMessageBox.critical(self,
						"Erreur d'authentification",
						"Login et mot de passe " +
						"incorrects.<br />(login "
						+ self.__conf["email"] + ")")
			except gaierror:
				QMessageBox.critical(self,
						"Erreur de connection",
						"Impossible de contacter le " +
						"serveur.<br/>Veuillez " +
						u"vérifier la connexion à " +
						"internet.")

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

	sys.exit(ret)
