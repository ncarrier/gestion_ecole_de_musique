#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gestionAbsencesUI import Ui_gestionAbsences

class GestionAbsences(QTabWidget):
	def __init__(self, parent=None):
		super(GestionAbsences, self).__init__(parent)
		self.createWidgets()

	def createWidgets(self):
		self.ui = Ui_gestionAbsences()
		self.ui.setupUi(self)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	ui = GestionAbsences()
	ui.show()
	sys.exit(app.exec_())
