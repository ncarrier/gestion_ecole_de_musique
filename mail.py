#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["MailUI"]

u"""Module d'envoi d'emails

Implémente une __ui pour la saisie d'emails ainsi que les mécanismes pour l'envoi
effectif

TODO : supporter d'autres fournisseurs d'adresse mail que gmail

"""

from socket import gaierror
from email.MIMEText import MIMEText
from smtplib import SMTP_SSL, SMTPAuthenticationError

from PyQt4.QtCore import pyqtSignal, SIGNAL, QTimer, QThread, Qt, QDate
from PyQt4.QtGui import QWidget, QMessageBox, QLineEdit, QInputDialog
from PyQt4.QtSql import QSqlQuery

from config import Config
from mailUI import Ui_mail


class MailUI(QWidget):
    u"""Classe chargée de l'interface d'envoi d'emails"""

# signaux
    u"""Signal envoyé quand la base a été modifiée"""
    majBdd = pyqtSignal()

    def __init__(self, parent=None):
        super(MailUI, self).__init__(parent)
        self.__conf = Config.getInstance()
        self.__ms = MailSender(self)
        self.__createWidgets()

    def __createWidgets(self):
        u"""Créée les widgets de l'interface graphique"""
        self.__ui = Ui_mail()
        self.__ui.setupUi(self)

        #Connection des signaux
        self.connect(self.__ui.cbAbsence, SIGNAL("currentIndexChanged(int)"),
            self.__majUI)
        self.connect(self.__ms, SIGNAL("sentSignal(int)"), self.__resulatEnvoi)
        self.connect(self.__ui.pbEnvoyer, SIGNAL("clicked()"), self.__envoyer)
        self.connect(self, SIGNAL("majBdd()"), self.miseAJour)

    def __majUI(self, index):
        u"""Rafraîchit le contenu de l'__ui quand l'absence sélectionée change"""
        date = self.__absences[index]["date"].toString(Qt.SystemLocaleLongDate)
        sujet = "Absence du " + date

        self.__ui.leSujet.setText(sujet)
        self.__ui.teCorps.setText(u"""Bonjour,\n"""
        u"Pourrais-tu me dire rapidement quand tu comptes rattraper tes " +
        u"cours du " + date + u", car cette absence date déjà de plus de " +
        u"""deux semaines.
Merci,
""" + self.__conf["signature"])
        self.__ui.pbEnvoyer.setText(u"Envoyer à <" +
            self.__absences[index]["adresse"] + ">")

    def miseAJour(self):
        u"""Liste les absences pouvant donner lieu à un email de rappel"""
        self.__ui.cbAbsence.clear()

        # Vérification des mails à envoyer
        req = QSqlQuery()
        date = QDate.currentDate()
        date = date.addDays(-int(self.__conf["duree"]))
        date = date.toString(Qt.ISODate)

        sql = "SELECT COUNT(*) FROM absence "
        sql += "WHERE mail_envoye='false' "
        sql += "AND regularisee='false' "
        sql += "AND jour <= '" + date + "' "
        if req.exec_(sql):
            req.next()
            nbMails = int(req.record().value(0).toString())
        else:
            # TODO log
            print "SQL error"
            return
        label = str(nbMails) + " absence"
        if nbMails == 0:
            label += " :"
            self.__ui.lAbsence.setText(label)
            self.__ui.leSujet.setText("")
            self.__ui.teCorps.setText("")
            self.__activerUi(False)
            self.__ui.pbEnvoyer.setText("Envoyer")
            return
        else:
            self.__activerUi(True)

        if nbMails > 1:
            label += "s"
        label += " :"
        self.__ui.lAbsence.setText(label)

        sql = "SELECT absence.id, jour, nom, email "
        sql += "FROM absence "
        sql += "JOIN intervenant "
        sql += "ON absence.id_intervenant=intervenant.id "
        sql += "WHERE mail_envoye='false' "
        sql += "AND regularisee='false' "
        sql += "AND jour <= '" + date + "' "
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
                self.__ui.cbAbsence.addItem(item)

    def __resulatEnvoi(self, errCode):
        u"""Slot notifié quand l'envoi du mail est fini

        errCode indique le succès, ou l'échec (avec la raison) de l'envoi du
        mail

        """
        if errCode == MailSender.MAIL_ERROR_NONE:
            # Mail envoyé, mise à jour de la base
            index = self.__ui.cbAbsence.currentIndex()

            sql = "UPDATE absence "
            sql += "SET mail_envoye='true' "
            sql += "WHERE id=" + str(self.__absences[index]["id"])
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
            QMessageBox.critical(self, "Erreur de connection",
                u"Impossible de contacter le serveur.<br />" +
                u"Veuillez vérifier la connexion à internet, <br />" +
                u"ainsi que l'adresse du serveur de messagerie.")
        elif errCode == MailSender.MAIL_ERROR_AUTHENTICATION:
            QMessageBox.critical(self, "Erreur d'authentification",
                "Indentifiants incorrects.<br />(login " + self.__conf["email"]
                + ")")
        else:  # MailSender.MAIL_ERROR_OTHER:
            QMessageBox.critical(self, "Erreur inconnue",
                "Une erreur inconnue s'est produite.<br />(login '"
                + self.__conf["email"] + "')")
            # TODO logger l'erreur réelle à la levée de l'exception

        self.refresh()

    def __activerUi(self, actif):
        """Active/désactive les contrôles de l'onglet d'écriture d'emails"""
        self.__ui.cbAbsence.setEnabled(actif)
        self.__ui.pbEnvoyer.setEnabled(actif)
        self.__ui.leSujet.setEnabled(actif)
        self.__ui.teCorps.setEnabled(actif)

    def __envoyer(self):
        """Envoie l'email"""
        index = self.__ui.cbAbsence.currentIndex()
        dest = str(self.__absences[index]["adresse"])
        sujet = str(self.__ui.leSujet.text().toUtf8())
        corps = self.__ui.teCorps.toPlainText().__str__()
        result = QInputDialog.getText(self, "Mot de passe",
                "Veuillez saisir le mot de passe<br /> " +
                "de votre compte de messagerie",
                QLineEdit.Password)
        password = str(result[0])
        if result[1]:
            self.__activerUi(False)
            self.__ms.envoiMail(dest, sujet, corps, password)


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
    sentSignal = pyqtSignal(int)

    def __init__(self, parent):
        super(MailSender, self).__init__(parent)
        self.__conf = Config.getInstance()
        self.__timer = QTimer()

    def envoiMail(self, dest, sujet, corps, password, timeout=10):
        u"""Envoit un mail

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
        u"""Exécuté à l'expiration du timer d'envoi de mail"""
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

    ui = MailUI()
    ui.show()
    ret = app.exec_()
    sys.exit(ret)
