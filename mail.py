# -*- coding: utf-8 -*-

import smtplib
from email.MIMEText import MIMEText

class MailSender():
	def __init__(self, config):
		"""Constructeur, lit les paramètres d'envoi de mails depuis le
		fichier de configuration"""
		f = open(config)
		lines = f.readlines()
		for l in lines:
			s = l.split("=")
			if s[0] == "email":
				self.__mailSource = s[1].rstrip()
			elif s[0] == "serveur":
				self.__serveur = s[1].replace("\n", "")
		f.close()

	def envoiMail(self, dest, password, subject, text):
		"""Envoit un mail selon les paramètres du fichier de
		configuration, en précisant le destinataire, le mot de passe,
		le sujet et le texte"""
		email = MIMEText(text)
		email['From'] = self.__mailSource
		email['To'] = dest
		email['Subject'] = subject

		server = smtplib.SMTP_SSL(self.__serveur)
		server.login(email['From'], password)
		server.sendmail(email['From'], email['To'], email.as_string())
		server.close()
