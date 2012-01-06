#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["EmailUI"]

u"""Module d'envoi d'emails

Implémente une ui pour la saisie d'emails ainsi que les mécanismes pour l'envoi
effectif

TODO : supporter d'autres fournisseurs d'adresse mail que gmail

"""

from socket import gaierror
from email.MIMEText import MIMEText
from smtplib import SMTP_SSL, SMTPAuthenticationError

from PyQt4.QtCore import pyqtSignal, SIGNAL, QTimer, QThread
from PyQt4.QtGui import QWidget

from config import Config
from emailUI import Ui_email


class EmailUI(QWidget):
    """Classe chargée de l'interface d'envoi d'emails"""
    def __init__(self, parent=None):
        super(EmailUI, self).__init__(parent)
        self.__conf = Config.getInstance()
        self.createWidgets()

    def createWidgets(self):
        self.ui = Ui_email()
        self.ui.setupUi(self)
#        self.ui.leEmail.setText(self.__conf["email"])
#        self.ui.leEmail.setProperty("name", "email")
#        self.ui.leServeur.setText(self.__conf["serveur"])
#        self.ui.leServeur.setProperty("name", "serveur")
#        self.ui.sbDuree.setValue(int(self.__conf["duree"]))
#        self.ui.sbDuree.setProperty("name", "duree")
#
#        self.connect(self.ui.leEmail, SIGNAL("textChanged(QString)"),
#            self.valueChanged)
#        self.connect(self.ui.leServeur, SIGNAL("textChanged(QString)"),
#            self.valueChanged)
#        self.connect(self.ui.sbDuree, SIGNAL("valueChanged(QString)"),
#            self.valueChanged)

#    def valueChanged(self, value):
#        self.__conf[str(self.sender().property("name").toString())] = str(value)

class MailSender(QThread):
# constantes
    MAIL_ERROR_NONE = 0
    MAIL_ERROR_TIMEOUT = 1
    MAIL_ERROR_AUTHENTICATION = 2
    MAIL_ERROR_CONNECTION = 3
    MAIL_ERROR_OTHER = 4

# signaux
    """Signal envoyé à la fin de l'envoi du mail, avec un code d'erreur"""
    sentSignal = pyqtSignal(int)

    def __init__(self, parent):
        super(MailSender, self).__init__(parent)
        self.__conf = Config.getInstance()
        self.__timer = QTimer()

    def envoiMail(self, dest, sujet, corps, password, timeout=10):
        """Envoit un mail

        Envoit un mail selon les paramètres du fichier de configuration, en
        précisant le destinataire, le sujet, le corps du mail et le mot de
        passe, puis envoit un signal sentSignal quand l'envoi du mail est fini,
        avec un code d'erreur. L'envoi échoue à expiration d'un __timer de 10s
        dont la durée peut être modifiée.

        """
        self.__timer.setSingleShot(True)

        self.__email = MIMEText(corps, 'plain', 'utf-8')
        self.__email['From'] = self.__conf["email"]
        self.__email['To'] = dest
        self.__email['Subject'] = sujet
        self.__password = password

        self.start()
        self.__timer.start(timeout * 1000)
        self.connect(self.__timer, SIGNAL("timeout()"), self.timeout)

    def run(self):
        u"""Surchage de la méthode QThread.run()

        Envoit l'email et notifie les erreurs

        """
        try:
            server = SMTP_SSL(self.__conf["serveur"])
            server.login(self.__email['From'], self.__password)
            server.sendmail(self.__email['From'], self.__email['To'],
                self.__email.as_string())
            server.close()
            self.sentSignal.emit(MailSender.MAIL_ERROR_NONE)
        except SMTPAuthenticationError:
            self.sentSignal.emit(MailSender.MAIL_ERROR_AUTHENTICATION)
        except gaierror:
            self.sentSignal.emit(MailSender.MAIL_ERROR_CONNECTION)
        except:
            self.sentSignal.emit(MailSender.MAIL_ERROR_OTHER)
        self.__timer.stop()

# slots
    def timeout(self):
        u"""Exécuté à l'expiration du __timer"""
        self.sentSignal.emit(MailSender.MAIL_ERROR_TIMEOUT)
        self.terminate()


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

    ui = EmailUI()
    ui.show()
    ret = app.exec_()
    sys.exit(ret)
