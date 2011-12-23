from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

class DateDelegate(QSqlRelationalDelegate):
	def __init__(self, parent, dateColumn):
		super(DateDelegate, self).__init__(parent)
		self.__dateColumn = dateColumn

	def createEditor(self, parent, option, index):
		if index.isValid() and index.column() == self.__dateColumn:
			return QDateEdit(QDate.currentDate(), parent)
		else:
			return QSqlRelationalDelegate.createEditor(self, parent,
					option, index)
	
	def setEditorData(self, editor, index):
		value = index.model().data(index, Qt.EditRole).toDate()

		if index.isValid() and index.column() == self.__dateColumn:
			editor.setCalendarPopup(True)
			editor.setDate(value)
		else:
			QSqlRelationalDelegate.setEditorData(self, editor, index)

	def setModelData(self, editor, model, index):
		if index.isValid() and index.column() == self.__dateColumn:
			date = editor.date().toString("yyyy-MM-dd")
			model.setData(index, date, Qt.EditRole)
		else:
			QSqlRelationalDelegate.setModelData(self, editor, model,
					index)

	def updateEditorGeometry(self, editor, option, index):
		if index.isValid() and index.column() == self.__dateColumn:
			editor.setGeometry(option.rect)
		else:
			QSqlRelationalDelegate.updateEditorGeometry(self, editor,
					option, index)
	def sizeHint(self, option, index):
		size = QSqlRelationalDelegate.sizeHint(self, option, index)
		if index.isValid() and index.column() == self.__dateColumn:
			value = index.model().data(index, Qt.EditRole).toDate()
			value = value.toString(Qt.SystemLocaleLongDate)
			s = QString(value)
			fm = QFontMetrics(QApplication.font())
			# Ce qui suit ne marche pas
			#(t, l, r, d) = QLineEdit("tutu").getTextMargins()
			#print t
			#print l
			#print r
			#print d

			return QSize(fm.width(s) + 5, size.width())
		else:
			return size

	def paint(self, painter, option, index):
		painter.save()
		if index.isValid() and index.column() == self.__dateColumn:
			value = index.model().data(index, Qt.EditRole).toDate()
			value = value.toString(Qt.SystemLocaleLongDate)
			align = Qt.AlignHCenter | Qt.AlignVCenter
			if option.state and QStyle.State_Active:
				if option.state & QStyle.State_Selected:
					palette = QPalette.HighlightedText
				else:
					palette = QPalette.WindowText
			else:
				palette = QPalette.WindowText

			QApplication.style().drawItemText(painter, option.rect,
					align, option.palette, True, value,
					palette)


		else:
			QSqlRelationalDelegate.paint(self, painter, option,
					index)
	
		painter.restore()
