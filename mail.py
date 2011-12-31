# -*- coding: utf-8 -*-
import smtplib
from email.MIMEText import MIMEText
from config import Config

class MailSender():
    def __init__(self):
        self.__conf = Config.getInstance()

    def envoiMail(self, dest, sujet, corps, password):
        """Envoit un mail selon les paramètres du fichier de
        configuration, en précisant le destinataire, le mot de passe,
        le sujet et le texte"""

        self.__email = MIMEText(corps, 'plain', 'utf-8')
        self.__email['From'] = self.__conf["email"]
        self.__email['To'] = dest
        self.__email['Subject'] = sujet

        server = smtplib.SMTP_SSL(self.__conf["serveur"])
        server.login(self.__email['From'], password)
        server.sendmail(self.__email['From'], self.__email['To'],
                self.__email.as_string())
        server.close()
