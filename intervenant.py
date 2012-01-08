#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["IntervenantUI"]

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QWidget

from tableUI import Ui_table


class IntervenantUI(QWidget):
    """Classe chargée de l'interface de gestion des intervenants"""
    def __init__(self, parent=None):
        super(IntervenantUI, self).__init__(parent)
        self.__createWidgets()

    def __createWidgets(self):
        """Créée les widgets de l'interface graphique"""
        self.ui = Ui_table()
        self.ui.setupUi(self)


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
