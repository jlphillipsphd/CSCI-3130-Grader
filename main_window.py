# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.setEnabled(True)
        mainWindow.resize(857, 584)
        mainWindow.setAccessibleName("")
        self.centralwidget = QtWidgets.QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.input_file_location = BetterLineEdit(self.centralwidget)
        self.input_file_location.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.input_file_location.setText("")
        self.input_file_location.setObjectName("input_file_location")
        self.horizontalLayout_12.addWidget(self.input_file_location)
        self.filename_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.filename_lineEdit.setMaximumSize(QtCore.QSize(90, 16777215))
        self.filename_lineEdit.setReadOnly(True)
        self.filename_lineEdit.setObjectName("filename_lineEdit")
        self.horizontalLayout_12.addWidget(self.filename_lineEdit)
        self.but_file_open = QtWidgets.QPushButton(self.centralwidget)
        self.but_file_open.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.but_file_open.setObjectName("but_file_open")
        self.horizontalLayout_12.addWidget(self.but_file_open)
        self.but_begin = QtWidgets.QPushButton(self.centralwidget)
        self.but_begin.setEnabled(False)
        self.but_begin.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.but_begin.setCheckable(False)
        self.but_begin.setAutoDefault(False)
        self.but_begin.setDefault(False)
        self.but_begin.setFlat(False)
        self.but_begin.setObjectName("but_begin")
        self.horizontalLayout_12.addWidget(self.but_begin)
        self.verticalLayout_7.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setSpacing(6)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_from = QtWidgets.QLabel(self.centralwidget)
        self.label_from.setObjectName("label_from")
        self.horizontalLayout.addWidget(self.label_from)
        self.dateTimeEdit_from = QtWidgets.QDateTimeEdit(self.centralwidget)
        self.dateTimeEdit_from.setEnabled(True)
        self.dateTimeEdit_from.setWrapping(False)
        self.dateTimeEdit_from.setReadOnly(True)
        self.dateTimeEdit_from.setAccelerated(False)
        self.dateTimeEdit_from.setCalendarPopup(True)
        self.dateTimeEdit_from.setObjectName("dateTimeEdit_from")
        self.horizontalLayout.addWidget(self.dateTimeEdit_from)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_submitted = QtWidgets.QLabel(self.centralwidget)
        self.label_submitted.setObjectName("label_submitted")
        self.horizontalLayout_2.addWidget(self.label_submitted)
        self.dateTimeEdit_submitted = QtWidgets.QDateTimeEdit(self.centralwidget)
        self.dateTimeEdit_submitted.setEnabled(True)
        self.dateTimeEdit_submitted.setWrapping(False)
        self.dateTimeEdit_submitted.setFrame(True)
        self.dateTimeEdit_submitted.setReadOnly(True)
        self.dateTimeEdit_submitted.setKeyboardTracking(False)
        self.dateTimeEdit_submitted.setCalendarPopup(True)
        self.dateTimeEdit_submitted.setObjectName("dateTimeEdit_submitted")
        self.horizontalLayout_2.addWidget(self.dateTimeEdit_submitted)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_to = QtWidgets.QLabel(self.centralwidget)
        self.label_to.setObjectName("label_to")
        self.horizontalLayout_3.addWidget(self.label_to)
        self.dateTimeEdit_to = QtWidgets.QDateTimeEdit(self.centralwidget)
        self.dateTimeEdit_to.setEnabled(True)
        self.dateTimeEdit_to.setReadOnly(True)
        self.dateTimeEdit_to.setCalendarPopup(True)
        self.dateTimeEdit_to.setObjectName("dateTimeEdit_to")
        self.horizontalLayout_3.addWidget(self.dateTimeEdit_to)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_7.addLayout(self.verticalLayout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.input_current_id = QtWidgets.QLineEdit(self.centralwidget)
        self.input_current_id.setMaximumSize(QtCore.QSize(60, 40))
        self.input_current_id.setObjectName("input_current_id")
        self.horizontalLayout_8.addWidget(self.input_current_id)
        self.label_current_id = QtWidgets.QLabel(self.centralwidget)
        self.label_current_id.setObjectName("label_current_id")
        self.horizontalLayout_8.addWidget(self.label_current_id)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.input_attempt = QtWidgets.QLineEdit(self.centralwidget)
        self.input_attempt.setMaximumSize(QtCore.QSize(40, 40))
        self.input_attempt.setObjectName("input_attempt")
        self.horizontalLayout_9.addWidget(self.input_attempt)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem)
        self.label_attempt = QtWidgets.QLabel(self.centralwidget)
        self.label_attempt.setObjectName("label_attempt")
        self.horizontalLayout_9.addWidget(self.label_attempt)
        self.verticalLayout_3.addLayout(self.horizontalLayout_9)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_3.addItem(spacerItem1)
        self.horizontalLayout_7.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.input_max_pos_grade = QtWidgets.QLineEdit(self.centralwidget)
        self.input_max_pos_grade.setEnabled(False)
        self.input_max_pos_grade.setMaximumSize(QtCore.QSize(40, 40))
        self.input_max_pos_grade.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.input_max_pos_grade.setText("")
        self.input_max_pos_grade.setObjectName("input_max_pos_grade")
        self.horizontalLayout_6.addWidget(self.input_max_pos_grade)
        self.label_max_pos = QtWidgets.QLabel(self.centralwidget)
        self.label_max_pos.setEnabled(True)
        self.label_max_pos.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label_max_pos.setObjectName("label_max_pos")
        self.horizontalLayout_6.addWidget(self.label_max_pos)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.input_subtract = QtWidgets.QLineEdit(self.centralwidget)
        self.input_subtract.setEnabled(False)
        self.input_subtract.setMaximumSize(QtCore.QSize(40, 40))
        self.input_subtract.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.input_subtract.setObjectName("input_subtract")
        self.horizontalLayout_4.addWidget(self.input_subtract)
        self.label_subtr = QtWidgets.QLabel(self.centralwidget)
        self.label_subtr.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label_subtr.setObjectName("label_subtr")
        self.horizontalLayout_4.addWidget(self.label_subtr)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.input_final_grade = QtWidgets.QLineEdit(self.centralwidget)
        self.input_final_grade.setEnabled(True)
        self.input_final_grade.setMaximumSize(QtCore.QSize(40, 40))
        self.input_final_grade.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.input_final_grade.setText("")
        self.input_final_grade.setObjectName("input_final_grade")
        self.horizontalLayout_5.addWidget(self.input_final_grade)
        self.label_final = QtWidgets.QLabel(self.centralwidget)
        self.label_final.setEnabled(True)
        self.label_final.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label_final.setObjectName("label_final")
        self.horizontalLayout_5.addWidget(self.label_final)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_7.addLayout(self.verticalLayout_2)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.but_regrade = QtWidgets.QPushButton(self.centralwidget)
        self.but_regrade.setEnabled(False)
        self.but_regrade.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.but_regrade.setObjectName("but_regrade")
        self.verticalLayout_4.addWidget(self.but_regrade)
        self.checkB_input_pin_status = QtWidgets.QCheckBox(self.centralwidget)
        self.checkB_input_pin_status.setEnabled(False)
        self.checkB_input_pin_status.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.checkB_input_pin_status.setObjectName("checkB_input_pin_status")
        self.verticalLayout_4.addWidget(self.checkB_input_pin_status)
        self.checkB_output_pin_status = QtWidgets.QCheckBox(self.centralwidget)
        self.checkB_output_pin_status.setEnabled(False)
        self.checkB_output_pin_status.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.checkB_output_pin_status.setObjectName("checkB_output_pin_status")
        self.verticalLayout_4.addWidget(self.checkB_output_pin_status)
        self.horizontalLayout_7.addLayout(self.verticalLayout_4)
        self.verticalLayout_7.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setSpacing(65)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.but_prev = QtWidgets.QPushButton(self.centralwidget)
        self.but_prev.setEnabled(False)
        self.but_prev.setMinimumSize(QtCore.QSize(60, 30))
        self.but_prev.setMaximumSize(QtCore.QSize(200, 16777215))
        self.but_prev.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.but_prev.setObjectName("but_prev")
        self.horizontalLayout_10.addWidget(self.but_prev)
        self.checkB_wrong = QtWidgets.QCheckBox(self.centralwidget)
        self.checkB_wrong.setEnabled(False)
        self.checkB_wrong.setMinimumSize(QtCore.QSize(75, 20))
        self.checkB_wrong.setMaximumSize(QtCore.QSize(75, 16777215))
        self.checkB_wrong.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.checkB_wrong.setObjectName("checkB_wrong")
        self.horizontalLayout_10.addWidget(self.checkB_wrong)
        self.but_reset = QtWidgets.QPushButton(self.centralwidget)
        self.but_reset.setMinimumSize(QtCore.QSize(60, 20))
        self.but_reset.setMaximumSize(QtCore.QSize(90, 16777215))
        self.but_reset.setObjectName("but_reset")
        self.horizontalLayout_10.addWidget(self.but_reset)
        self.but_next = QtWidgets.QPushButton(self.centralwidget)
        self.but_next.setEnabled(False)
        self.but_next.setMinimumSize(QtCore.QSize(60, 30))
        self.but_next.setMaximumSize(QtCore.QSize(200, 16777215))
        self.but_next.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.but_next.setObjectName("but_next")
        self.horizontalLayout_10.addWidget(self.but_next)
        self.verticalLayout_7.addLayout(self.horizontalLayout_10)
        self.popular_answers = QtWidgets.QComboBox(self.centralwidget)
        self.popular_answers.setEnabled(False)
        self.popular_answers.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.popular_answers.setEditable(False)
        self.popular_answers.setCurrentText("")
        self.popular_answers.setObjectName("popular_answers")
        self.popular_answers.addItem("")
        self.popular_answers.setItemText(0, "")
        self.verticalLayout_7.addWidget(self.popular_answers)
        self.tabs_for_log_and_resp = QtWidgets.QTabWidget(self.centralwidget)
        self.tabs_for_log_and_resp.setEnabled(True)
        self.tabs_for_log_and_resp.setMinimumSize(QtCore.QSize(770, 30))
        self.tabs_for_log_and_resp.setMaximumSize(QtCore.QSize(20000, 3700))
        self.tabs_for_log_and_resp.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.tabs_for_log_and_resp.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabs_for_log_and_resp.setObjectName("tabs_for_log_and_resp")
        self.response_tab = QtWidgets.QWidget()
        self.response_tab.setMinimumSize(QtCore.QSize(0, 180))
        self.response_tab.setMaximumSize(QtCore.QSize(16777215, 300))
        self.response_tab.setObjectName("response_tab")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.response_tab)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.splitter = QtWidgets.QSplitter(self.response_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.input_response_browser = QtWidgets.QPlainTextEdit(self.splitter)
        self.input_response_browser.setEnabled(True)
        self.input_response_browser.setMinimumSize(QtCore.QSize(0, 30))
        self.input_response_browser.setReadOnly(True)
        self.input_response_browser.setObjectName("input_response_browser")
        self.input_response_browser_user = BetterPlainTextEdit(self.splitter)
        self.input_response_browser_user.setEnabled(False)
        self.input_response_browser_user.setMinimumSize(QtCore.QSize(0, 30))
        self.input_response_browser_user.setObjectName("input_response_browser_user")
        self.verticalLayout_9.addWidget(self.splitter)
        self.tabs_for_log_and_resp.addTab(self.response_tab, "")
        self.tab_prev_resp = QtWidgets.QWidget()
        self.tab_prev_resp.setObjectName("tab_prev_resp")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tab_prev_resp)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.input_prev_response = QtWidgets.QPlainTextEdit(self.tab_prev_resp)
        self.input_prev_response.setEnabled(False)
        self.input_prev_response.setObjectName("input_prev_response")
        self.verticalLayout_5.addWidget(self.input_prev_response)
        self.tabs_for_log_and_resp.addTab(self.tab_prev_resp, "")
        self.tab_message_to_all = QtWidgets.QWidget()
        self.tab_message_to_all.setObjectName("tab_message_to_all")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.tab_message_to_all)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.input_message_to_all = QtWidgets.QPlainTextEdit(self.tab_message_to_all)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_message_to_all.sizePolicy().hasHeightForWidth())
        self.input_message_to_all.setSizePolicy(sizePolicy)
        self.input_message_to_all.setObjectName("input_message_to_all")
        self.verticalLayout_8.addWidget(self.input_message_to_all)
        self.tabs_for_log_and_resp.addTab(self.tab_message_to_all, "")
        self.log_tab = QtWidgets.QWidget()
        self.log_tab.setObjectName("log_tab")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.log_tab)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.input_log_browser = QtWidgets.QTextBrowser(self.log_tab)
        self.input_log_browser.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.input_log_browser.setObjectName("input_log_browser")
        self.verticalLayout_6.addWidget(self.input_log_browser)
        self.tabs_for_log_and_resp.addTab(self.log_tab, "")
        self.verticalLayout_7.addWidget(self.tabs_for_log_and_resp)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.but_save_response = QtWidgets.QPushButton(self.centralwidget)
        self.but_save_response.setEnabled(True)
        self.but_save_response.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.but_save_response.setObjectName("but_save_response")
        self.horizontalLayout_11.addWidget(self.but_save_response)
        self.check_autosave = QtWidgets.QCheckBox(self.centralwidget)
        self.check_autosave.setObjectName("check_autosave")
        self.horizontalLayout_11.addWidget(self.check_autosave)
        self.set_style_checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.set_style_checkbox.setObjectName("set_style_checkbox")
        self.horizontalLayout_11.addWidget(self.set_style_checkbox)
        self.toolButton = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton.setEnabled(False)
        self.toolButton.setObjectName("toolButton")
        self.horizontalLayout_11.addWidget(self.toolButton)
        self.but_save_all = QtWidgets.QPushButton(self.centralwidget)
        self.but_save_all.setEnabled(True)
        self.but_save_all.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.but_save_all.setObjectName("but_save_all")
        self.horizontalLayout_11.addWidget(self.but_save_all)
        self.new_window_but = QtWidgets.QPushButton(self.centralwidget)
        self.new_window_but.setObjectName("new_window_but")
        self.horizontalLayout_11.addWidget(self.new_window_but)
        self.but_create_report = QtWidgets.QPushButton(self.centralwidget)
        self.but_create_report.setEnabled(False)
        self.but_create_report.setObjectName("but_create_report")
        self.horizontalLayout_11.addWidget(self.but_create_report)
        self.verticalLayout_7.addLayout(self.horizontalLayout_11)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(True)
        self.progressBar.setAutoFillBackground(False)
        self.progressBar.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_7.addWidget(self.progressBar)
        mainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(mainWindow)
        self.tabs_for_log_and_resp.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "CSCI3130 grader"))
        self.input_file_location.setPlaceholderText(_translate("mainWindow", "Double click for path selection or paste|type path here"))
        self.but_file_open.setText(_translate("mainWindow", "Open"))
        self.but_begin.setText(_translate("mainWindow", "Begin"))
        self.label_from.setText(_translate("mainWindow", "From"))
        self.label_submitted.setText(_translate("mainWindow", "Submitted"))
        self.label_to.setText(_translate("mainWindow", "To"))
        self.label_current_id.setText(_translate("mainWindow", "current id"))
        self.label_attempt.setText(_translate("mainWindow", "attempt"))
        self.label_max_pos.setText(_translate("mainWindow", "lab max grade"))
        self.label_subtr.setText(_translate("mainWindow", "subtract"))
        self.label_final.setText(_translate("mainWindow", "final grade"))
        self.but_regrade.setText(_translate("mainWindow", "GRADE"))
        self.checkB_input_pin_status.setText(_translate("mainWindow", "Input direction"))
        self.checkB_output_pin_status.setText(_translate("mainWindow", "Output direction"))
        self.but_prev.setText(_translate("mainWindow", "prev"))
        self.checkB_wrong.setText(_translate("mainWindow", "WRONG"))
        self.but_reset.setText(_translate("mainWindow", "Reset"))
        self.but_next.setText(_translate("mainWindow", "next"))
        self.input_response_browser.setPlaceholderText(_translate("mainWindow", "Auto answer"))
        self.input_response_browser_user.setPlaceholderText(_translate("mainWindow", "User comment"))
        self.tabs_for_log_and_resp.setTabText(self.tabs_for_log_and_resp.indexOf(self.response_tab), _translate("mainWindow", "Response"))
        self.tabs_for_log_and_resp.setTabText(self.tabs_for_log_and_resp.indexOf(self.tab_prev_resp), _translate("mainWindow", "Previous Response"))
        self.tabs_for_log_and_resp.setTabText(self.tabs_for_log_and_resp.indexOf(self.tab_message_to_all), _translate("mainWindow", "Message to all"))
        self.tabs_for_log_and_resp.setTabText(self.tabs_for_log_and_resp.indexOf(self.log_tab), _translate("mainWindow", "Log"))
        self.but_save_response.setText(_translate("mainWindow", "save responce"))
        self.check_autosave.setText(_translate("mainWindow", "autosave"))
        self.set_style_checkbox.setText(_translate("mainWindow", "style"))
        self.toolButton.setText(_translate("mainWindow", "Settings"))
        self.but_save_all.setText(_translate("mainWindow", "save all"))
        self.new_window_but.setText(_translate("mainWindow", "Create due dates"))
        self.but_create_report.setText(_translate("mainWindow", "Create reports"))
        self.progressBar.setFormat(_translate("mainWindow", "%v/%m (%p%)"))

from qt_class_improvements import BetterLineEdit, BetterPlainTextEdit
