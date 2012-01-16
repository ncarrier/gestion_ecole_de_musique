# -*- coding: utf-8 -*-
__all__ = ["SpecializedDelegate"]

from PySide.QtCore import QDate, QSize, Qt, QRect, QPoint

from PySide.QtGui import QDateEdit, QCheckBox, QFontMetrics, QApplication
from PySide.QtGui import QPalette, QStyle, QSpinBox, QStyleOptionButton

from PySide.QtSql import QSqlRelationalDelegate


class SpecializedDelegate(QSqlRelationalDelegate):
    u"""Delegate dont les colonnes peuvent être spécialisées

    Des listes sont fournies au constructeur selon le type de leur contenu,
    pour que la vue puisse fournir un éditeur adapté

    dates : Liste des champs dates
    booleens : Liste des champs oui / non
    numbers : Liste des nombres (entre 0 et 100)
    read_only : Liste des colonnes non mutables

    """

    def __init__(self, parent, dates, booleens, numbers, read_only):
        """Construit un SpecializedDelegate"""
        super(SpecializedDelegate, self).__init__(parent)
        self.__dates = dates
        self.__booleens = booleens
        self.__numbers = numbers
        self.__read_only = read_only

    def checkBoxRect(self, opt, editor):
        cb_option = QStyleOptionButton()
        style = QApplication.style()
        cb_rect = style.subElementRect(QStyle.SE_CheckBoxIndicator, cb_option,
            editor)
        cb_point = QPoint(opt.rect.x() + (opt.rect.width() - cb_rect.width()) / 2,
            opt.rect.y() + (opt.rect.height() - cb_rect.height()) / 2)
        return QRect(cb_point, cb_rect.size())

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
            r = self.checkBoxRect(option, editor)
            rect = option.rect
            rect.moveTo(r.x(), r.y())
            rect.setWidth(r.width())
            rect.setHeight(r.height())
            editor.setGeometry(rect)
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
            value = QDate.fromString(index.model().data(index, Qt.DisplayRole),
                 Qt.ISODate)
            editor.setCalendarPopup(True)
            editor.setDate(value)
        elif index.column() in self.__booleens:
            value = index.model().data(index, Qt.EditRole)
            if value == "oui":
                value = True
            else:
                value = False
            editor.setChecked(value)
        elif index.column() in self.__numbers:
            value = index.model().data(index, Qt.EditRole)
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
            value = QDate.fromString(index.model().data(index, Qt.DisplayRole),
                 Qt.ISODate)
            value = value.toString(Qt.SystemLocaleLongDate)
            fm = QFontMetrics(QApplication.font())

            return QSize(fm.width(value) + 5, size.height())
        else:
            return size

    def paint(self, painter, option, index):
        painter.save()
        if not index.isValid():
            QSqlRelationalDelegate.paint(self, painter, option, index)

        if index.column() in self.__dates:
            value = QDate.fromString(index.model().data(index, Qt.DisplayRole),
                 Qt.ISODate)
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
