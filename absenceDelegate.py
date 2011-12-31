from PyQt4.QtCore import QDate
from PyQt4.QtCore import QString
from PyQt4.QtCore import QSize
from PyQt4.QtCore import Qt

from PyQt4.QtGui import QDateEdit
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QFontMetrics
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QPalette
from PyQt4.QtGui import QStyle

from PyQt4.QtSql import QSqlRelationalDelegate

class AbsenceDelegate(QSqlRelationalDelegate):
	def __init__(self, parent, dateColumn, mailEnvoyeColumn, regulariseeColumn):
		super(AbsenceDelegate, self).__init__(parent)
		self.__dateColumn = dateColumn
		self.__mailEnvoyeColumn = mailEnvoyeColumn
		self.__regulariseeColumn = regulariseeColumn

	def createEditor(self, parent, option, index):
		if not index.isValid():
			return QSqlRelationalDelegate.createEditor(self, parent,
					option, index)

		if index.column() == self.__dateColumn:
			return QDateEdit(QDate.currentDate(), parent)
		elif index.column() == self.__mailEnvoyeColumn or index.column() == self.__regulariseeColumn:
			return QCheckBox("", parent)

		return QSqlRelationalDelegate.createEditor(self, parent,
				option, index)


	def setEditorData(self, editor, index):

		if index.isValid() and index.column() == self.__dateColumn:
			value = index.model().data(index, Qt.EditRole).toDate()
			editor.setCalendarPopup(True)
			editor.setDate(value)
		elif index.isValid() and index.column() == self.__mailEnvoyeColumn:
			value = index.model().data(index, Qt.EditRole).toBool()
			editor.setChecked(value)
		elif index.isValid() and index.column() == self.__regulariseeColumn:
			value = index.model().data(index, Qt.EditRole).toBool()
			editor.setChecked(value)
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
			value = index.model().data(index, Qt.DisplayRole).toDate()
			value = value.toString(Qt.SystemLocaleLongDate)
			s = QString(value)
			fm = QFontMetrics(QApplication.font())

			return QSize(fm.width(s) + 5, size.width())
		else:
			return size

	def paint(self, painter, option, index):
		painter.save()
		if index.isValid() and index.column() == self.__dateColumn:
			value = index.model().data(index, Qt.DisplayRole).toDate()
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
#		elif index.isValid() and index.column() == self.__mailEnvoyeColumn:
#			painter = QStylePainter()
#			painter.drawControl(QStyle.CE_CheckBox, option)
#		elif index.isValid() and index.column() == self.__regulariseeColumn:
#			QApplication.style().drawControl(QStyle.CE_CheckBox,
#					option, painter)
		else:
			QSqlRelationalDelegate.paint(self, painter, option,
					index)

		painter.restore()
