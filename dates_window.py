# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dates_window.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dates_window(object):
    def setupUi(self, dates_window):
        dates_window.setObjectName("dates_window")
        dates_window.resize(251, 314)
        self.buttonBox = QtWidgets.QDialogButtonBox(dates_window)
        self.buttonBox.setGeometry(QtCore.QRect(40, 260, 191, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.calendarWidget = QtWidgets.QCalendarWidget(dates_window)
        self.calendarWidget.setGeometry(QtCore.QRect(10, 10, 224, 232))
        self.calendarWidget.setObjectName("calendarWidget")

        self.retranslateUi(dates_window)
        self.buttonBox.accepted.connect(dates_window.accept)
        self.buttonBox.rejected.connect(dates_window.reject)
        QtCore.QMetaObject.connectSlotsByName(dates_window)

    def retranslateUi(self, dates_window):
        _translate = QtCore.QCoreApplication.translate
        dates_window.setWindowTitle(_translate("dates_window", "Check dates"))
        self.calendarWidget.setAccessibleName(_translate("dates_window", "cal_diag"))

