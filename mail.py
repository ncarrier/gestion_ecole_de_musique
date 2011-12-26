# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from PyQt4.QtGui import *

import smtplib
from email.MIMEText import MIMEText
from mailUI import Ui_mailComposer
from config import Config

class MailComposer(QDialog):
	def __init__(self, data, parent=None):
		"""data est un dictionnaire qui contient :
		    * date : date
		    * nom : nom destinataire
		    * adresse : adresse destinataire
		"""
		super(MailComposer, self).__init__(parent)
		self.__data = data
		self.__conf = Config.getInstance("private/config")
		self.createWidgets()

	
	def createWidgets(self):
		d = self.__data
		self.ui = Ui_mailComposer()
		self.ui.setupUi(self)
		exp = "Expéditeur : " + self.__conf["email"]
		self.ui.lExpediteur.setText(exp)
		#dest = "Destinataire : " + d["nom"] + " <" + d["adresse"] + ">"

	def envoiMail(self, password):
		"""Envoit un mail selon les paramètres du fichier de
		configuration, en précisant le destinataire, le mot de passe,
		le sujet et le texte"""

		self.__email = MIMEText(self.ui.teEmail.text())
		self.__email['From'] = self.__conf["email"]
		self.__email['To'] = self.__data["adresse"]
		self.__email['Subject'] = "Absence du " + data["date"]

		server = smtplib.SMTP_SSL(self.__conf["serveur"])
		server.login(self.__email['From'], password)
		server.sendmail(self.__email['From'], self.__email['To'],
				self.__email.as_string())
		server.close()
