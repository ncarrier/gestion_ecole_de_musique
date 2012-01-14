# -*- coding: utf-8 -*-
__all__ = ["AbsenceDelegate"]

from PyQt4.QtCore import QDate, QString, QSize, Qt

from PyQt4.QtGui import QDateEdit, QCheckBox, QFontMetrics, QApplication
from PyQt4.QtGui import QPalette, QStyle, QSpinBox

from PyQt4.QtSql import QSqlRelationalDelegate


class AbsenceDelegate(QSqlRelationalDelegate):
    u"""Delegate dont les colonnes peuvent être spécialisées

    Des listes sont fournies au constructeur selon le type de leur contenu,
    pour que la vue puisse fournir un éditeur adapté

    """

    def __init__(self, parent, dates, booleens, numbers, read_only):
        """Construit un SpecializedDelegate"""
        super(AbsenceDelegate, self).__init__(parent)
        self.__dates = dates
        self.__booleens = booleens
        self.__numbers = numbers
        self.__read_only = read_only

    def createEditor(self, parent, option, index):
        if not index.isValid():
            return QSqlRelationalDelegate.createEditor(self, parent,
                    option, index)

        if index.column() in self.__read_only:
            return None
        elif index.column() in self.__dates:
            return QDateEdit(QDate.currentDate(), parent)
        elif index.column() in self.__booleens:
            editor = QCheckBox("", parent)
            editor.setAutoFillBackground(True)
            return editor
        elif index.column() in self.__numbers:
            editor = QSpinBox(parent)
            editor.setMinimum(0)
            editor.setMaximum(100)
            return editor
        return QSqlRelationalDelegate.createEditor(self, parent,
                option, index)

    def setEditorData(self, editor, index):
        if not index.isValid():
            QSqlRelationalDelegate.setEditorData(self, editor, index)
            return

        if index.column() in self.__dates:
            value = index.model().data(index, Qt.EditRole).toDate()
            editor.setCalendarPopup(True)
            editor.setDate(value)
        elif index.column() in self.__booleens:
            value = index.model().data(index, Qt.EditRole).toBool()
            editor.setChecked(value)
        elif index.column() in self.__numbers:
            value = index.model().data(index, Qt.EditRole).toInt()[0]
            spinBox = editor
            spinBox.setValue(value)
        else:
            QSqlRelationalDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if not index.isValid():
            QSqlRelationalDelegate.setModelData(self, editor, model, index)
            return

        if index.column() in self.__dates:
            date = editor.date().toString("yyyy-MM-dd")
            model.setData(index, date, Qt.EditRole)

        elif index.column() in self.__numbers:
            spinBox = editor
            spinBox.interpretText()
            value = spinBox.value()
            model.setData(index, value, Qt.EditRole)
        elif index.column() in self.__booleens:
            checkBox = editor
            if checkBox.isChecked():
                model.setData(index, "oui", Qt.EditRole)
            else:
                model.setData(index, "non", Qt.EditRole)
        else:
            QSqlRelationalDelegate.setModelData(self, editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        if not index.isValid():
            QSqlRelationalDelegate.updateEditorGeometry(self, editor, option,
                index)

        if index.column() in self.__dates or index.column() in self.__booleens:
            editor.setGeometry(option.rect)
        else:
            QSqlRelationalDelegate.updateEditorGeometry(self, editor, option,
                index)

    def sizeHint(self, option, index):
        size = QSqlRelationalDelegate.sizeHint(self, option, index)
        if index.isValid() and index.column() in self.__dates:
            value = index.model().data(index, Qt.DisplayRole).toDate()
            value = value.toString(Qt.SystemLocaleLongDate)
            s = QString(value)
            fm = QFontMetrics(QApplication.font())

            return QSize(fm.width(s) + 5, size.height())
        else:
            return size

    def paint(self, painter, option, index):
        painter.save()
        if not index.isValid():
            QSqlRelationalDelegate.paint(self, painter, option, index)

        if index.column() in self.__dates:
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

            QApplication.style().drawItemText(painter, option.rect, align,
                option.palette, True, value, palette)
        else:
            QSqlRelationalDelegate.paint(self, painter, option, index)

        painter.restore()
