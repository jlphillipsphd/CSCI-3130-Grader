# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manage_labs.ui'
#
# Created by: PyQt5 UI code generator 5.12.dev1812231618
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_manage_labs(object):
    def setupUi(self, manage_labs):
        manage_labs.setObjectName("manage_labs")
        manage_labs.resize(753, 90)
        manage_labs.setWindowFilePath("")
        self.verticalLayout = QtWidgets.QVBoxLayout(manage_labs)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labs_select_comboBox = QtWidgets.QComboBox(manage_labs)
        self.labs_select_comboBox.setEnabled(False)
        self.labs_select_comboBox.setObjectName("labs_select_comboBox")
        self.horizontalLayout.addWidget(self.labs_select_comboBox)
        self.sync_but = QtWidgets.QPushButton(manage_labs)
        self.sync_but.setObjectName("sync_but")
        self.horizontalLayout.addWidget(self.sync_but)
        self.import_but = QtWidgets.QPushButton(manage_labs)
        self.import_but.setEnabled(False)
        self.import_but.setObjectName("import_but")
        self.horizontalLayout.addWidget(self.import_but)
        self.create_due_dates_but = QtWidgets.QPushButton(manage_labs)
        self.create_due_dates_but.setEnabled(False)
        self.create_due_dates_but.setObjectName("create_due_dates_but")
        self.horizontalLayout.addWidget(self.create_due_dates_but)
        self.export_but = QtWidgets.QPushButton(manage_labs)
        self.export_but.setEnabled(False)
        self.export_but.setObjectName("export_but")
        self.horizontalLayout.addWidget(self.export_but)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.status_bar = QtWidgets.QLineEdit(manage_labs)
        self.status_bar.setObjectName("status_bar")
        self.verticalLayout.addWidget(self.status_bar)

        self.retranslateUi(manage_labs)
        QtCore.QMetaObject.connectSlotsByName(manage_labs)

    def retranslateUi(self, manage_labs):
        _translate = QtCore.QCoreApplication.translate
        manage_labs.setWindowTitle(_translate("manage_labs", "Manage labs"))
        self.sync_but.setText(_translate("manage_labs", "Sync to local storage"))
        self.import_but.setText(_translate("manage_labs", "import labs"))
        self.create_due_dates_but.setText(_translate("manage_labs", "Create due dates"))
        self.export_but.setText(_translate("manage_labs", "Export pdfs"))

