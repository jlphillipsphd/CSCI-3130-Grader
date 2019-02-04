# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'simple_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.dev1812231618
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(328, 76)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("os_linux_1.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_main_question = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_main_question.sizePolicy().hasHeightForWidth())
        self.label_main_question.setSizePolicy(sizePolicy)
        self.label_main_question.setAlignment(QtCore.Qt.AlignCenter)
        self.label_main_question.setObjectName("label_main_question")
        self.verticalLayout.addWidget(self.label_main_question)
        self.buttonBox_simple_dial = QtWidgets.QDialogButtonBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox_simple_dial.sizePolicy().hasHeightForWidth())
        self.buttonBox_simple_dial.setSizePolicy(sizePolicy)
        self.buttonBox_simple_dial.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox_simple_dial.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox_simple_dial.setObjectName("buttonBox_simple_dial")
        self.verticalLayout.addWidget(self.buttonBox_simple_dial)

        self.retranslateUi(Dialog)
        self.buttonBox_simple_dial.accepted.connect(Dialog.accept)
        self.buttonBox_simple_dial.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Create database ?"))
        self.label_main_question.setText(_translate("Dialog", "Database will be created.  Confirm.."))

