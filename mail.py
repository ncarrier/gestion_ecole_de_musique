#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["MailUI"]

u"""Module d'envoi d'emails

Implémente une _ui pour la saisie d'emails ainsi que les mécanismes pour
l'envoi effectif

TODO : supporter d'autres fournisseurs d'adresse mail que gmail

"""

print_sql = False

from socket import gaierror
from email.MIMEText import MIMEText
from smtplib import SMTP, SMTPAuthenticationError, SMTPServerDisconnected#, SMTP_SSL

from PySide.QtCore import Signal, QThread, Qt, QDate
from PySide.QtGui import QWidget, QMessageBox, QLineEdit, QInputDialog
from PySide.QtSql import QSqlQuery

from config import Config
from mailUI import Ui_mail
from nombres import nombre


class MailSQL():
    """Classe chargée de préparer les requêtes pour l'interface de mails"""
    @staticmethod
    def construitRequeteComptage(duree):
        u"""Construit la requête pour compter le nombre des absences

        duree : chaîne contenant la durée de rappel

        """

        duree = str(duree)
        sql = """
          SELECT COUNT(*)
          FROM absence
          WHERE regularisee = 'non'
          AND ((
              dernier_mail IS NULL
              AND jour < date('now', '-""" + duree + """ days')
            )
            OR dernier_mail < date('now', '-""" + duree + """ days')
          )
        """
        if print_sql:
            print sql,
        return sql

    @staticmethod
    def construitRequeteListe(duree):
        u"""Construit la requête pour lister les des absences

        duree : chaîne contenant la durée de rappel

        """

        duree = str(duree)
        sql = """
          SELECT absence.id, jour, nom, email, mails_envoyes
          FROM absence
          JOIN intervenant
          ON absence.id_intervenant = intervenant.id
          WHERE regularisee = 'non'
          AND ((
              dernier_mail IS NULL
              AND jour < date('now', '-""" + duree + """ days')
            )
            OR dernier_mail < date('now', '-""" + duree + """ days')
          )
        """
        if print_sql:
            print sql,
        return sql

    @staticmethod
    def mailEnvoye(id_absence):
        u"""Construit la requête pour enregistrer l'envoi d'un mail

        duree : chaîne contenant l'id de l'absence à modifier

        """

        id_absence = str(id_absence)
        sql = """
          UPDATE absence
          SET mails_envoyes = mails_envoyes + 1, dernier_mail = date('now')
          WHERE id=""" + id_absence
        if print_sql:
            print sql,
        return sql


class MailUI(QWidget):
    u"""Classe chargée de l'interface d'envoi d'emails"""

# signaux
    u"""Signal envoyé quand la base a été modifiée"""
    majBdd = Signal()
    u"""Signal envoyé pour notifier d'un événement"""
    notification = Signal(str, int)
    u"""Durée de vie des messages de notification"""
    DUREE_MESSAGE = 10000

    def __init__(self, parent=None):
        super(MailUI, self).__init__(parent)
        self.__conf = Config.getInstance()
        self.__ms = MailSender(self)
        self.__createWidgets()
        self.miseAJour()

    def __createWidgets(self):
        u"""Créée les widgets de l'interface graphique"""
        self._ui = Ui_mail()
        self._ui.setupUi(self)
        self.__connectSlots()

    def __connectSlots(self):
        u"""Connecte les signaux des contrôles et de mise à jour"""
        self._ui.cbAbsence.currentIndexChanged.connect(self.__majUI)
        self.__ms.sentSignal.connect(self.__resulatEnvoi)
        self._ui.pbEnvoyer.clicked.connect(self.__envoyer)
        self.majBdd.connect(self.miseAJour)

    def __majUI(self, item):
        u"""Rafraîchit le contenu de l'ui quand l'absence sélectionnée change"""
        idx = self._ui.cbAbsence.currentIndex()
        date = self.__absences[idx]["date"].toString(Qt.SystemLocaleLongDate)
        sujet = "Absence du " + date

        self._ui.leSujet.setText(sujet)
        self._ui.teCorps.setText(u"""Bonjour,\n"""
            u"Pourrais-tu me dire rapidement quand tu comptes rattraper tes " +
            "cours du " + date + u", car cette absence date déjà de plus de " +
            nombre[int(self.__conf["duree"])] + u""" jours.
Merci,
""" + self.__conf["signature"])
        self._ui.pbEnvoyer.setText(u"Envoyer à <" +
            self.__absences[idx]["adresse"] + ">")

    def miseAJour(self):
        u"""Liste les absences pouvant donner lieu à un email de rappel"""
        self._ui.cbAbsence.clear()

        # Vérification des mails à envoyer
        req = QSqlQuery()
        sql = MailSQL.construitRequeteComptage(self.__conf["duree"])
        if req.exec_(sql):
            req.next()
            nbMails = req.record().value(0)
        else:
            # TODO log
            print req.lastError().text()
            print req.lastQuery()
            print "Erreur de requête"
            return
        label = str(nbMails) + " absence"
        if nbMails == 0:
            label += " :"
            self._ui.lAbsence.setText(label)
            self._ui.leSujet.setText("")
            self._ui.teCorps.setText("")
            self.__activerUi(False)
            self._ui.pbEnvoyer.setText("Envoyer")
            return
        else:
            self.__activerUi(True)

        if nbMails > 1:
            label += "s"
        label += " :"
        self._ui.lAbsence.setText(label)

        sql = MailSQL.construitRequeteListe(self.__conf["duree"])
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
                absence["id"] = rec.value(0)
                absence["date"] = QDate.fromString(rec.value(1), Qt.ISODate)
                absence["nom"] = rec.value(2)
                absence["adresse"] = rec.value(3)
                self.__absences.append(absence)
                item = absence["nom"] + " le "
                item += absence["date"].toString(Qt.SystemLocaleLongDate)
                self._ui.cbAbsence.addItem(item)

    def __resulatEnvoi(self, errCode):
        u"""Slot notifié quand l'envoi du mail est fini

        errCode indique le succès, ou l'échec (avec la raison) de l'envoi du
        mail

        """
        if errCode == MailSender.MAIL_ERROR_NONE:
            # Mail envoyé, mise à jour de la base
            self.notification.emit(u"Email envoyé", MailUI.DUREE_MESSAGE)

            index = self._ui.cbAbsence.currentIndex()
            sql = MailSQL.mailEnvoye(str(self.__absences[index]["id"]))
            req = QSqlQuery()
            if not req.exec_(sql):
                QMessageBox.critical(self, u"Erreur de base de données",
                    u"Le mail a été envoyé mais impossible de <br />" +
                    u"l'enregistrer dans la base.")

                # TODO logger
                print "SQL error"
                print str(req.lastError().text().toUtf8())
                print req.lastQuery()
            else:
                self.majBdd.emit()

        elif (errCode == MailSender.MAIL_ERROR_TIMEOUT or
            errCode == MailSender.MAIL_ERROR_CONNECTION):
            message = u"Email non envoyé - "
            if errCode == MailSender.MAIL_ERROR_TIMEOUT:
                message += u"Durée dépassée"
            else:
                message += u"Erreur de connexion"
            self.notification.emit(message, MailUI.DUREE_MESSAGE)

            QMessageBox.critical(self, "Erreur de connection",
                u"Impossible de contacter le serveur.<br />" +
                u"Veuillez vérifier la connexion à internet, <br />" +
                u"ainsi que l'adresse du serveur de messagerie.")
        elif errCode == MailSender.MAIL_ERROR_AUTHENTICATION:
            message = u"Email non envoyé - Erreur d'authentification"
            self.notification.emit(message, MailUI.DUREE_MESSAGE)

            QMessageBox.critical(self, "Erreur d'authentification",
                "Indentifiants incorrects.<br />(login " + self.__conf["email"]
                + ")")
            del self.__password
        else:  # MailSender.MAIL_ERROR_OTHER:
            message = u"Email non envoyé - Erreur inconnue"
            self.notification.emit(message, MailUI.DUREE_MESSAGE)

            QMessageBox.critical(self, "Erreur inconnue",
                "Une erreur inconnue s'est produite.<br />(login '"
                + self.__conf["email"] + "')")
            # TODO logger l'erreur réelle à la levée de l'exception

        self.majBdd.emit()

    def __activerUi(self, actif):
        """Active/désactive les contrôles de l'onglet d'écriture d'emails"""
        self._ui.cbAbsence.setEnabled(actif)
        self._ui.pbEnvoyer.setEnabled(actif)
        self._ui.leSujet.setEnabled(actif)
        self._ui.teCorps.setEnabled(actif)

    def __envoyer(self):
        """Envoie l'email"""
        index = self._ui.cbAbsence.currentIndex()
        dest = self.__absences[index]["adresse"]
        sujet = self._ui.leSujet.text()
        corps = self._ui.teCorps.toPlainText()
        try:
            password = self.__password
        except AttributeError:
            result = QInputDialog.getText(self, "Mot de passe",
                    "Veuillez saisir le mot de passe<br /> " +
                    "de votre compte de messagerie", QLineEdit.Password)
            self.__password = str(result[0])
            password = self.__password
            if not result[1]:
                return

        self.__activerUi(False)
        self.notification.emit("Email en cours d'envoi", MailUI.DUREE_MESSAGE)
        self.__ms.envoiMail(dest, sujet, corps, password)

DEFAULT_TIMEOUT = 10

class MailSender(QThread):
    u"""Classe responsable de l'envoi d'emails"""

# constantes
    MAIL_ERROR_NONE = 0
    MAIL_ERROR_TIMEOUT = 1
    MAIL_ERROR_AUTHENTICATION = 2
    MAIL_ERROR_CONNECTION = 3
    MAIL_ERROR_OTHER = 4

# signaux
    u"""Signal envoyé à la fin de l'envoi du mail, avec un code d'erreur"""
    sentSignal = Signal(int)

    def __init__(self, parent):
        super(MailSender, self).__init__(parent)
        self.__conf = Config.getInstance()

    def envoiMail(self, dest, sujet, corps, password,
            timeout=DEFAULT_TIMEOUT):
        u"""Envoit un mail

        Envoit un mail selon les paramètres du fichier de configuration, en
        précisant le destinataire, le sujet, le corps du mail et le mot de
        passe, puis envoit un signal sentSignal quand l'envoi du mail est fini,
        avec un code d'erreur. L'envoi échoue à expiration d'un __timer de 10s
        dont la durée peut être modifiée.

        """
        self.__email = MIMEText(corps, 'plain', 'utf-8')
        self.__email['From'] = self.__conf["email"]
        self.__email['To'] = dest
        self.__email['Subject'] = sujet
        self.__password = password

        self.start()

    def run(self):
        u"""Surchage de la méthode QThread.run()

        Envoit l'email et notifie les erreurs

        """
        try:
            # Pour gmail, connexion smtp_ssl avec port par défaut
            # et pas de starttls
            server = SMTP(self.__conf["serveur"], 587, "localhost",
                DEFAULT_TIMEOUT)
            server.starttls()
            server.login(self.__email['From'], self.__password)
            server.sendmail(self.__email['From'], self.__email['To'],
                self.__email.as_string())
            server.close()
            self.sentSignal.emit(MailSender.MAIL_ERROR_NONE)
        except SMTPAuthenticationError:
            self.sentSignal.emit(MailSender.MAIL_ERROR_AUTHENTICATION)
        except gaierror:
            self.sentSignal.emit(MailSender.MAIL_ERROR_CONNECTION)
        except SMTPServerDisconnected:
            self.sentSignal.emit(MailSender.MAIL_ERROR_TIMEOUT)
        except Exception, e:
            print e
            self.sentSignal.emit(MailSender.MAIL_ERROR_OTHER)


if __name__ == "__main__":
    """Main de test"""
    import sys
    from PySide.QtGui import QApplication
    from PySide.QtCore import QLibraryInfo, QLocale, QTranslator
    from PySide.QtSql import QSqlDatabase

    app = QApplication(sys.argv)

    locale = QLocale.system().name()
    translator = QTranslator()
    translator.load("qt_" + locale,
        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)

    # Configuration de la base de données
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName('private/gem.db')
    db.open()

    ui = MailUI()
    ui.show()
    ret = app.exec_()
    sys.exit(ret)
