#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import Counter
import xml.etree.ElementTree as Etree

import sys
import os
import subprocess
# import signal
from pathlib import Path
import numpy as np
import sqlite3 as lite
import zipfile

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QDateTime, QLocale
from PyQt5.QtWidgets import QFileDialog

from main_window import Ui_mainWindow
# from dates_window import Ui_dates_window
from create_dates_diag import Ui_Create_dates_dialog
from settings import Ui_Settings
from manage_labs import Ui_manage_labs
from db_init import *
from simple_dialog import Ui_Dialog

QLocale.setDefault(QLocale(QLocale.English))

MAIN_FILE_NAME = ''  # filename is selected automatically as most common. Change it only if it does not work.
MAIN_FILE_NAME_OVERRIDE = ''

styleData = """
/* https://stackoverflow.com/questions/22332106/python-qtgui-qprogressbar-color */
QProgressBar
{
    border: 1px solid grey;
    border-radius: 5px;
    text-align: center;
    font-weight: bold;
}
QProgressBar::chunk
{
    background-color: #d7801a;
    width: 2.15px;
    margin: 0.5px;
}
"""


def read_settings(db_name = 'settings.sqlite3' ):
    """
    Queries settings db and sets paths
    :return: path to logisim, path to current semester labs
    """
    import os.path

    if os.path.exists(db_name):
        with lite.connect(db_name) as con:
            cur = con.cursor()
            try:
                cur.execute('SELECT * FROM PATHS')
                result = cur.fetchone()
                for row in result:
                    print(row)
                logisim_path = result[0][0]
                working_dir = result[0][1]
                # since import is not implemented - ignore import path: import_path = result[0][2]
                return logisim_path, working_dir
            except Exception as e:
                print('Was not able to get results from settings DB: ', e)
    return None


class CircFile:
    # not used yet
    # class circ_type:
    #     def __init__(self, name):
    #         self.name = name
    #         self.input_pins = None
    #         self.output_pins = None
    #         self.input_pins = list()
    #         self.output_pins = list()

    class PinType:
        def __init__(self, name, iotype, facing):
            self.name = name
            self.type = iotype
            self.facing = facing

    def __init__(self, filename):
        self.filename = filename
        self.subtract = 0
        self.final_grade = 10
        self.__all_circuits = list()

    def __get_parsed_circuits(self):
        """

        :return:
        """
        tree = Etree.parse(self.filename)
        # self.log_update('Successfully openned ' + self.filename)
        root = tree.getroot()
        arr = list()
        for child in root:
            # print(child.tag)
            if child.tag == 'circuit':
                arr.append(child)
        self.__all_circuits = arr

    def get_parsed_pins(self):
        """

        :return:
        """
        self.__get_parsed_circuits()
        arr = self.__all_circuits
        all_pins = list()
        for elem in arr:
            pins = list()
            for child in elem.findall('comp'):
                if child.get('name') == 'Pin':
                    pins.append(child)
                    # print(child.tag, child.attrib)
            all_pins.append(pins)

        clean_data = list()
        if all_pins:
            for pins in all_pins:  # Although this looks like an error - it is not,
                # there is only one iteration. This code will be extended later
                # as I had in my older scripts to grade all PLDs.
                clean_data = list()
                for pin in pins:
                    name = '0'
                    io_type = '0'
                    facing = ''
                    for elem in list(pin):
                        if elem.get('name') in ['output', 'input', 'tristate']:
                            io_type = elem.get('name')
                        elif elem.get('name') == 'label':
                            name = elem.get('val')
                        elif elem.get('name') == 'facing':
                            facing = elem.get('val')
                    clean_data.append(self.PinType(name, io_type, facing))
        else:
            raise Exception('Error in pin parsing(all_pins)')

        output_pins = list()
        input_pins = list()
        other_pins = list()

        if clean_data:
            for pin in clean_data:
                if pin.type == 'output':
                    output_pins.append(pin)
                elif pin.type == 'input' or pin.type == 'tristate':
                    input_pins.append(pin)
                else:
                    other_pins.append(pin)
        else:
            raise Exception('Error in pin parsing(clean data)')

        return input_pins, output_pins, other_pins


class Grader:
    def __init__(self, working_directory):
        self.__from_date = 0
        self.to_date = 0
        self.attempt = 0
        self.timestamps = list()
        self.stud_ids = list()
        self.stud_id = ''
        self.submitted = 0
        self.input_correct = False
        self.output_correct = False
        self.lab_max_grade = 0
        self.subtract = 0
        self.__wrong_clicked = False
        self.final_grade = 0
        self.__possible_answers_dict = {}
        self.global_log = ''
        self.previous_responses = ''
        self.__message_to_all = ''
        self.__graded_idlist = list()
        self.file_list = list()
        self.resp_text = 'I did not find any errors. Good job!\n'
        self.user_comment = ''
        self.cur_idx = 0
        self.working_dir = working_directory
        self.input_suggestion = set('',)
        self.resp_len = 38
        self.logisim_pid = -1
        self.circ_file_name = MAIN_FILE_NAME
        self.lab_type = ''
        self.lab_num = 0
        self.time = 0
        self.circ_obj_ref = None
        self.tot_elem = 0
        self.lab_id = ''

    def open_dir(self):
        """
        Opens directory with labs for grading.
        :return: nothing.
        """
        # TODO check behaviour when directory is wrong.
        # if len(self.working_directory) < 3:
        #     wdir = './'
        # else:
        #     wdir = self.working_directory


        root, dirs, files = os.walk(self.working_dir).__next__()
        files.sort()
        # check_file = files[0]  # not used at this time
        if len(files) < 1:
            raise Exception("No due files ? Extra files in working directory ?")
        due_file = files[1] # TODO: change this to a better design.

        self.lab_type = self.working_dir.split('/')[-2].split('_')[0]
        self.lab_num = int(self.working_dir.split('/')[-2].split('_')[2])
        self.attempt = int(self.working_dir.split('/')[-2].split('_')[3])

        if self.lab_type == 'Closed':
            self.lab_id = 'CLA' + str(self.lab_num)
            # self.lab_max_grade = 10
        else:  # Open
            # self.lab_max_grade = 20
            self.lab_id = 'OLA' + str(self.lab_num)

        self.lab_max_grade = get_lab_max_value(self.lab_id)

        self.time = int(due_file[6:])

        dirs.sort()  # sort list of submitted labs
        if dirs[0] == 'Answers':
            dirs.pop(0)

        self.stud_ids = dirs
        self.stud_ids = list()
        self.timestamps = list()
        # directory_list = list()
        for name in dirs:
            self.file_list.append(os.path.join(root, name))
            temp_arr = name.split('-')
            self.stud_ids.append(temp_arr[0])
            self.timestamps.append(int(temp_arr[2]))

    def get_stud_id(self):
        """
        Just a simple getter.
        :return:
        """
        return self.stud_id

    def log_update(self, log_event):
        """
        Saves events into a string.
        Later this string is displayed in a separate tab.
        :param log_event: what happened.
        :return: nothing
        """
        self.global_log += self.stud_id + ': ' + str(log_event) + '\n'

    def get_parsed_pins(self):
        """
        High level function that obtains in|out pins and check their facing.
        :return: nothing.
        """
        try:
            input_pins, output_pins, other_pins = self.circ_obj_ref.get_parsed_pins()
            if other_pins:
                self.log_update('I was not able to recognize ' + str(len(other_pins)) + " pins.")
            self.input_correct = True
            self.output_correct = True
            if not self.check_pins_facing(pins=input_pins, corr_facing='east'):
                self.subtract += 1
                self.input_correct = False
            if not self.check_pins_facing(pins=output_pins, corr_facing='west'):
                self.subtract += 1
                self.output_correct = False
        except Exception as e:  # TODO check for FileNotFoundError and assign ZERO
            print(e)
            # self.log_update(sys.exc_info()[0])
            # print(sys.exc_info()[0])
            raise
        # self.log_update('Done checking: ' + self.filename)

    # noinspection PyMethodMayBeStatic
    def check_pins_facing(self, pins, corr_facing):
        """
        Low level pin facing checker.
        :param pins: structured list of pins.
        :param corr_facing: nothing to add.
        :return: True if facing is correct, False otherwise
        """
        for pin in pins:
            if pin.facing != corr_facing and pin.facing != '':
                return False
        return True

    def check_file(self):
        """
        Opens circ file, tryes to parse it and to generate grade according to the pin facing.
        This check is too simple and most likely will be updated later.
        :return: nothing
        """
        file = os.path.join(self.file_list[self.cur_idx], MAIN_FILE_NAME)

        circ_obj = CircFile(file)
        self.circ_obj_ref = circ_obj
        self.subtract = 0
        try:
            self.get_parsed_pins()

            self.log_update('Pins successfully parsed.')
            self.final_grade = self.lab_max_grade - self.subtract
            self.generate_response()
        except Exception as e:
            print(e)
            self.log_update(sys.exc_info()[0])

    def check_circ_exist(self):
        """
        Checks whether file exists with specified name.
        If not generates report which contains all submitted elements.
        :return: True is file exists, False otherwise
        """
        if not os.path.isfile(self.file_list[self.cur_idx] + '/' + self.circ_file_name):
            self.resp_text = 'File was not found'
            file_found = os.listdir(self.file_list[self.cur_idx])
            potential_files = list()
            for file in file_found:
                if file not in ['grade.txt', 'penalty.txt', 'responce.txt', 'tech_info.txt', ]:
                    potential_files.append(file)
            if potential_files:
                self.resp_text += '\nNext files|folders were found:\n'
            for file in potential_files:
                if os.path.isdir(self.file_list[self.cur_idx] + '/' + file):
                    self.resp_text += file + ' - directory.\n'
                else:
                    self.resp_text += file + ' - regular file.\n'
            self.resp_len = len(self.resp_text)
            self.final_grade = 0
            return False
        return True

    def read_resp(self):
        """
        Reads response generated by either import scripts or by grader.
        Usually is stored in response.txt. Later may be transferred into DB.
        :return: nothing.
        """
        self.submitted = self.timestamps[self.cur_idx]
        try:
            with open(os.path.join(self.file_list[self.cur_idx], 'responce.txt'), 'r') as resp_file:
                a = resp_file.readlines()
                self.resp_text = ''.join(a)
                self.resp_len = len(self.resp_text)
        except Exception as e:
            print(e)
            self.log_update(sys.exc_info()[0])

        try:
            with open(os.path.join(self.file_list[self.cur_idx], 'grade.txt'), 'r') as grade_file:
                self.final_grade = int(grade_file.readline())
        except Exception as e:
            print(e)
            self.log_update(sys.exc_info()[0])

        # self.read_prev_resp()

    def read_prev_resp(self):
        """
        In case we are working with resubmission,
        this function will try to get previous responses.
        :return: nothing.
        """
        if self.attempt > 1:
            self.previous_responses = ''  # TODO find same name in folder name
            prev_att = int(self.working_dir[-2:-1])
            for i in range(prev_att-1, 0, -1):
                prev_working_dir = self.working_dir[:-2] + str(i) + '/'
                for file in os.listdir(prev_working_dir):
                    if file.__contains__(self.stud_id):
                        # print(file)
                        try:
                            with open(prev_working_dir + file + '/responce.txt', 'r') as resp_file:
                                self.previous_responses += str(i) + 'th submission :\n\t' \
                                                           + '\n'.join(resp_file.readlines())
                        except Exception as e:
                            print('Error in read prev responce: ', e)

    def next_circ(self):
        """
        Opens next circuit
        :return: current index
        """
        self.cur_idx += 1
        # self.check_file(self.cur_idx)
        self.user_comment = ''
        if self.check_circ_exist():
            self.read_resp()
        self.stud_id = self.stud_ids[self.cur_idx]
        try:
            self.read_prev_resp()
        except Exception as e:
            print('Error during attempt to read prev resp when opening next circuit: ', e)
            # TODO add handler
        return self.cur_idx

    def prev_circ(self):
        """
        Opens previous circuit
        :return: current index
        """
        self.cur_idx -= 1
        # self.check_file(self.cur_idx)
        self.user_comment = ''
        if self.check_circ_exist():
            self.read_resp()
        self.stud_id = self.stud_ids[self.cur_idx]
        try:
            self.read_prev_resp()
        except Exception as e:
            print('Error during attempt to read prev resp when opening prev circuit: ', e)
            # TODO add handler
        return self.cur_idx

    def check_wrong(self):
        """
        Funciton bound to 'Wrong' button(checkbox). Marks lab as 'wrong'.
        :return: nothing
        """
        self.final_grade = 0
        self.resp_text = 'Your lab was marked as wrong. You should fix errors listed below and resubmit it.'
        self.resp_len = len(self.resp_text)

    def save_grade(self):
        """
        Function bound to 'Save grade' button. Saves grade into 'grade.txt' file
        :return: nothing.
        """
        file = os.path.join(self.file_list[self.cur_idx], 'grade.txt')
        with open(file, 'w') as grade_file:
            grade_file.write(str(self.final_grade))
        self.log_update('Grade saved')

    def save_responce(self):
        """
        Function bound to 'Save responce' button.
        Saves current (auto and manual) responce into 'responce.txt'.
        :return: nothing.
        """
        file = os.path.join(self.file_list[self.cur_idx], 'responce.txt')
        with open(file, 'w') as resp_file:
            resp_file.write(self.resp_text)
            if self.user_comment:
                resp_file.write('\nAdditional comment: ' + self.user_comment + '\n')
        self.log_update('Responce saved')

    def save_all(self):
        """
        Function bound to 'Save all' button.
        Saves both grade and response by calling appropriate functions.
        :return: nothing.
        """
        self.save_grade()
        self.save_responce()

    def generate_response(self):
        """
        Regenerates the responce.
        :return: nothing.
        """
        self.resp_text = ''
        self.user_comment = ''
        if self.input_correct and self.output_correct:
            self.resp_text = 'I did not find any errors. Good job!'
        else:
            if not self.input_correct:
                self.resp_text += 'Your input pins have wrong orientation.\n'

            if not self.output_correct:
                self.resp_text += 'Your output pins have wrong orientation.\n'
        self.resp_len = len(self.resp_text)

    def add_to_common_answers(self, typed):
        """
        Function bound to FocusOut input handler.
        Adds whatever is typed into popular answers.
        :param typed: Text from input field
        :return: nothing.
        """
        self.input_suggestion.add(typed)


class UiMainWindow1(Ui_mainWindow):
    """

    """

    def __init__(self):
        Ui_mainWindow.__init__(self)
        self.grader_ref = None
        self.cal_window = None
        self.working_dir = None



    def disable_fields(self):
        """
        disables UI elements. Usually followed by 'enable_fields'
        :return: nothing
        """
        self.checkB_input_pin_status.setDisabled(True)
        self.checkB_output_pin_status.setDisabled(True)
        # self.input_response_browser.setDisabled(True)
        self.checkB_wrong.setDisabled(True)

        # self.input_subtract.setDisabled(True)
        self.but_regrade.setDisabled(True)
        self.popular_answers.setDisabled(True)
        self.input_final_grade.setDisabled(True)
        self.checkB_wrong.setChecked(False)
        self.input_current_id.setText('')

    def enable_fields(self):
        """
        enables UI elements. Usually follows 'disable_fields'
        :return: nothing
        """
        self.checkB_input_pin_status.setEnabled(True)
        self.checkB_output_pin_status.setEnabled(True)
        # self.input_response_browser.setEnabled(True)
        self.checkB_wrong.setEnabled(True)
        self.input_final_grade.setEnabled(True)

        # self.input_subtract.setEnabled(True)
        # self.but_regrade.setEnabled(True)
        self.popular_answers.setEnabled(True)

    def load_dir(self):
        """
        Resets UI when directory to grade is loaded.
        :return:
        """
        # activate elements
        self.but_begin.setDisabled(True)
        self.but_begin.repaint()
        self.progressBar.setEnabled(True)

        self.disable_fields()

        self.grader_ref.tot_elem = len(self.grader_ref.file_list)
        if self.grader_ref.tot_elem > 1:
            self.but_next.setEnabled(True)

        self.progressBar.setMaximum(self.grader_ref.tot_elem)
        self.progressBar.setValue(0)

        # self.grader_ref.check_file(0)
        # self.grader_ref.stud_id = self.grader_ref.stud_ids[self.grader_ref.cur_idx]
        self.grader_ref.cur_idx = -1
        self.next_circ()
        # self.grader_ref.read_resp()
        # self.grader_ref.read_prev_resp()
        # self.show_stat()
        # self.check_file()
        # self.input_current_id.setPlainText(self.grader_ref.get_stud_id())

        self.enable_fields()
        self.input_response_browser_user.setEnabled(True)
        self.but_regrade.setText('GRADE')
        self.but_save_all.setEnabled(True)
        self.but_save_response.setEnabled(True)
        self.check_autosave.setEnabled(True)

    def my_open_file(self):
        """
        Creates Grader instance and stores it in local reference
        Determines filename by selecting filename used by majority of students.
        Displays selected filename in UI element, so grader can see it.
        :return:
        """
        working_dir = self.input_file_location.text()

        try:
            my_grader = Grader(working_dir)
            my_grader.open_dir()
            self.grader_ref = my_grader

            self.input_max_pos_grade.setText(str(my_grader.lab_max_grade))
            my_grader.to_date = QDateTime.fromSecsSinceEpoch(my_grader.time)
            self.input_attempt.setText(str(my_grader.attempt))
            self.dateTimeEdit_to.setDateTime(my_grader.to_date)
            self.grader_ref.add_to_common_answers('')  # helps to remove all text in user comment section

            global MAIN_FILE_NAME, MAIN_FILE_NAME_OVERRIDE

            MAIN_FILE_NAME = get_lab_filename(my_grader.lab_id)[0]
            if not MAIN_FILE_NAME:
                # Old way, I was determining filename as the most common submitted file.
                if not MAIN_FILE_NAME_OVERRIDE:
                    a = []
                    for root, dirs, files in os.walk(working_dir):
                        for file in files:
                            if file.endswith(".circ"):
                                a.append(file)
                    a = np.array(a)

                    MAIN_FILE_NAME = Counter(a.flat).most_common(1)[0][0]
                else:
                    MAIN_FILE_NAME = MAIN_FILE_NAME_OVERRIDE
                # Now I can just read it from DB

            self.grader_ref.circ_file_name = MAIN_FILE_NAME
            self.filename_lineEdit.setText(MAIN_FILE_NAME.split('.')[0])

            self.but_create_report.setEnabled(True)
            self.but_begin.setEnabled(True)
        except Exception as e:  # TODO add log error
            print('Error in open_file : ', e)
            print(sys.exc_info()[0])

    def show_stat(self):
        """
        Displays current and old responses.
        Resets many UI elements for a next student.
        :return:
        """
        self.input_prev_response.setPlainText(self.grader_ref.previous_responses)
        if not Path(self.grader_ref.file_list[self.grader_ref.cur_idx]+'/'+self.grader_ref.circ_file_name).is_file():
            self.kill_logisim()
            self.grader_ref.final_grade = 0
            self.input_response_browser.setPlainText('File does not exist.')
            self.grader_ref.final_grade = 0
        else:
            if self.but_regrade.text() == '&GRADE' or self.but_regrade.text() == 'GRADE':
                try:
                    self.run_logisim()
                except Exception as e:
                    print('Error in run_logisim: ', e)
                    print(sys.exc_info()[0])

        self.input_current_id.setText(self.grader_ref.get_stud_id())
        self.dateTimeEdit_submitted.setDateTime(QDateTime.fromSecsSinceEpoch(self.grader_ref.submitted))
        self.input_subtract.setText('')
        self.input_final_grade.setText(str(self.grader_ref.final_grade))
        self.input_log_browser.setText(self.grader_ref.global_log)
        self.input_response_browser.setPlainText(self.grader_ref.resp_text)
        self.input_response_browser_user.clear()
        self.checkB_input_pin_status.setChecked(False)
        self.checkB_output_pin_status.setChecked(False)
        self.popular_answers.setCurrentIndex(-1)

    def check_file(self):
        """
        Sets UI elements related to autonomous pin check to states
        set by lab checker.
        Not useful anymore.
        :return: nothing.
        """
        self.input_subtract.setText(str(self.grader_ref.subtract))
        self.input_final_grade.setText(str(self.grader_ref.final_grade))

        self.input_log_browser.setText(self.grader_ref.global_log)
        # self.input_log_browser.append(self.grader_ref.global_log)

        if self.grader_ref.input_correct:
            self.checkB_input_pin_status.setChecked(True)
        if self.grader_ref.output_correct:
            self.checkB_output_pin_status.setChecked(True)

        # self.but_save_response.setDisabled(True)
        # self.but_save_all.setDisabled(True)

        # self.but_edit_done.setDisabled(True)
        try:
            # self.grader_ref.generate_response()  #TODO this overwrites File not found.
            self.input_response_browser.setPlainText(self.grader_ref.resp_text)
            # self.but_edit_done.setEnabled(True)
            # self.but_save_response.setEnabled(True)
            # self.but_save_all.setEnabled(True)
        except Exception as e:
            print('Error in generate response:', e)

    def next_circ(self):
        """
        Function bound to 'Next' button.
        Saves prev response and grade if 'autosave' is on.
        Opens next file
        Checks whether next file exists and sets UI appropriately.
        :return:
        """
        self.disable_fields()
        self.but_regrade.setText('GRADE')
        if self.check_autosave.isChecked():
            self.save_all()
        next_idx = self.grader_ref.next_circ()
        # self.check_file()
        self.show_stat()
        if next_idx >= self.grader_ref.tot_elem-1:
            self.but_next.setDisabled(True)
        if next_idx == 1:
            self.but_prev.setEnabled(True)

        self.progressBar.setValue(next_idx)
        self.enable_fields()

    def prev_circ(self):
        """
        Function bound to 'Prev' button.
        Saves prev response and grade if 'autosave' is on.
        Opens prev file
        Checks whether prev file exists and sets UI appropriately.
        :return:
        """
        self.disable_fields()
        self.but_regrade.setText('GRADE')
        next_idx = self.grader_ref.prev_circ()
        # self.check_file()
        self.show_stat()
        if next_idx <= self.grader_ref.tot_elem-1:
            self.but_next.setEnabled(True)
        if next_idx == 0:
            self.but_prev.setDisabled(True)

        self.progressBar.setValue(next_idx)
        self.enable_fields()

    def check_wrong(self):
        """
        Function bound to 'WRONG' button.
        Marks lab as wrong.
        :return: nothing
        """
        if self.checkB_wrong.isEnabled():
            self.grader_ref.check_wrong()
            self.input_final_grade.setText(str(self.grader_ref.final_grade))
            self.grader_ref.log_update('Lab was marked as wrong manually. Zero was assigned to final grade.')
            self.input_response_browser.setPlainText(self.grader_ref.resp_text)
            self.checkB_wrong.setDisabled(True)

    def regrade(self):
        """
        Resets lab values.
        :return:
        """
        self.disable_fields()
        self.but_regrade.setText('regrade')
        self.show_stat()
        self.grader_ref.check_file()
        if self.grader_ref.check_circ_exist():
            self.check_file()
        self.input_response_browser.setPlainText(self.grader_ref.resp_text)
        self.enable_fields()

    def reset_grade_resp(self):
        """
        Resets grade values.
        :return:
        """
        self.disable_fields()
        self.show_stat()
        self.grader_ref.check_file()
        if self.grader_ref.check_circ_exist():
            self.input_response_browser.setPlainText('I did not find any errors. Good job!')
            self.grader_ref.final_grade = self.grader_ref.lab_max_grade
            self.input_final_grade.setText(str(self.grader_ref.final_grade))
        self.enable_fields()

    def update_popular_answers(self):
        """
        In case length of the internal set structure changed, refills UI drop down list
        with new  values.
        :return:
        """
        if len(self.popular_answers) != len(self.grader_ref.input_suggestion):
            self.popular_answers.clear()
            self.popular_answers.addItems(self.grader_ref.input_suggestion)
            # for item in self.grader_ref.input_suggestion:

    def save_grade(self):
        """
        Function bound to 'Save grade' button.
        Calls function that saves current grade.
        :return:
        """
        self.grader_ref.save_grade()

    def save_response(self):
        """
        Function bound to 'Save response' button.
        Calls functions that save current commment.
        :return:
        """
        self.grader_ref.resp_text = self.input_response_browser.toPlainText()
        self.grader_ref.user_comment = self.input_response_browser_user.toPlainText()
        self.grader_ref.save_responce()

    def save_all(self):
        """
        Function bound to 'Save all' button.
        Simply calls other 'save' functions.
        :return:
        """
        self.grader_ref.save_grade()
        self.save_response()
        save_grade_and_report(self.grader_ref.get_stud_id, self.grader_ref.lab_num, self.grader_ref.lab_type,
                              self.grader_ref.attempt, self.grader_ref.final_grade, self.grader_ref.resp_text)
        # self.grader_ref.save_responce()

    def track_final_grade(self):
        """
        Saves manual grade changes into log.
        :return:
        """
        grade = self.input_final_grade.text()
        self.grader_ref.log_update('Manual grade change from : ' + str(self.grader_ref.final_grade))
        self.input_log_browser.setText(self.grader_ref.global_log)
        self.grader_ref.final_grade = int(grade)
        self.grader_ref.log_update('Manual grade change to: ' + str(grade))
        self.input_log_browser.setText(self.grader_ref.global_log)

    def setupUi(self, main_window):
        """
        Adds extra functionality to the UI generated by Qt Designer
        and converted to the python file.
        :return: nohting
        """
        super().setupUi(main_window)

        self.bind_functions()
        self.sync_params_to_settings()

        from pathlib import Path
        settings_location = str(Path(os.path.expandvars(os.path.expanduser('./settings.sqlite3'))).absolute())
        if os.path.isfile(settings_location):
            paths, local = settings_db_read_settings()
            if len(os.walk(get_full_path(paths, local) + "/server_sync/").__next__()[1]) > 0:
                if not self.manage_labs_but.isEnabled():
                    self.manage_labs_but.setEnabled(True)
                if not self.but_file_open.isEnabled():
                    self.but_file_open.setEnabled(True)
                    self.input_file_location.setEnabled(True)


    def sync_params_to_settings(self):
        """
        Once returned from settings tab - updates grading path
        :return: Nothing
        """
        paths, local = settings_db_read_settings()
        working_dir = ''
        if paths and len(paths) == 4:
            self.logisim_path = paths[0]
            if len(paths[1]) > 0:
                working_dir = paths[1]
            else:
                working_dir = './'
        if local and len(local) >= 4:
            self.grader_name = local[0]
            working_dir += str(local[1])
            working_dir += '_' + local[2] + '/'
            self.set_style_checkbox.setChecked(bool(local[3]))

        if len(working_dir) > 0:
            self.input_file_location.setText(os.path.expanduser(working_dir))


    def bind_functions(self):
        """
        All bindings happen here.
        :return: nothing.
        """
        self.but_file_open.clicked.connect(self.my_open_file)
        self.but_begin.clicked.connect(self.load_dir)
        self.but_next.clicked.connect(self.next_circ)
        self.but_prev.clicked.connect(self.prev_circ)
        self.checkB_wrong.clicked.connect(self.check_wrong)
        #  self.but_regrade.clicked.connect(self.regrade)
        self.but_save_all.clicked.connect(self.save_all)
        self.but_save_response.clicked.connect(self.save_response)
        self.input_final_grade.textEdited.connect(self.track_final_grade)
        #  self.but_edit_done.clicked.connect(self.resp_edit_done)
        #  self.popular_answers.activated.connect(self.select_saved_answer)
        # self.but_create_report.setEnabled(True)  # Debug
        self.but_create_report.clicked.connect(self.generate_reports)
        # self.new_window_but.clicked.connect(self.open_dates_dialog)
        #  self.input_response_browser_user.focusInEvent(self, self.memorize_user_comment)
        #  self.custom_but_test.right_clicked[int].connect(self.dummy_d)
        self.input_file_location.dclicked.connect(self.open_file_diag)
        self.input_response_browser_user.focus_lost.connect(self.memorize_user_comment)
        self.popular_answers.currentIndexChanged.connect(self.update_user_comment_from_popular_answers)
        self.set_style_checkbox.stateChanged.connect(self.change_win_style)
        self.but_reset.clicked.connect(self.reset_grade_resp)
        self.settings_but.clicked.connect(self.open_settings_dialog)
        self.manage_labs_but.clicked.connect(self.open_manage_labs_diag)
        # self.sync_but.clicked.connect(self.sync_files)



    def change_win_style(self):
        """
        Adds nice style to the progress bar.
        style is defined above as global var.
        :return: nothing.
        """
        if self.set_style_checkbox.isChecked():
            self.progressBar.setStyleSheet(styleData)
        else:
            self.progressBar.setStyleSheet('')

    # noinspection PyMethodMayBeStatic
    def dummy_d_1(self):
        print('dummy_1 activated')

    def update_user_comment_from_popular_answers(self):
        """
        Updates user answer with selected popular answer.
        :return: nothing.
        """
        if self.popular_answers.hasFocus():
            self.input_response_browser_user.setPlainText(self.popular_answers.currentText())

    def open_file_diag(self):
        """
        Function bound to the doubleclick even handler of input field.
        Creates file dialog to select correct lab directory.
        :return: nothing.
        """
        obtained_dir = QFileDialog.getExistingDirectory(caption='Select where to create due files',
                                                        directory=self.input_file_location.text())
        if len(obtained_dir) > 1:
            self.input_file_location.setText(obtained_dir+'/')

    def memorize_user_comment(self):
        """
        If comment is already in popular answers - selects it,
        otherwise adds it to the popular answers.
        :return: nothing.
        """
        typed = self.input_response_browser_user.toPlainText()
        if hasattr(self, 'grader_ref') and typed:
            try:
                index = self.popular_answers.findText(self.input_response_browser_user.toPlainText(),
                                                      QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.popular_answers.setCurrentIndex(index)
                else:
                    self.grader_ref.add_to_common_answers(typed)
                    self.update_popular_answers()
                    index = self.popular_answers.findText(self.input_response_browser_user.toPlainText(),
                                                          QtCore.Qt.MatchFixedString)
                    try:
                        self.popular_answers.setCurrentIndex(index)
                    except Exception as e:
                        print('Failed to select proper index: ', e)
                        raise
            except Exception as e:
                print('failed to add popular answer: ', e)

    def kill_logisim(self):
        """
        Just kills logisim process by saved pid.
        :return: nothing.
        """
        try:
            self.grader_ref.logisim_pid.kill()
        except Exception as e:
            print("was not able to kill : ", e)

    def run_logisim(self):
        """
        Opens logisim in a separate process.
        Path is hardcoded, but will be changed once I have 'settings' window
        and|or database.
        :return: nothing.
        """

        command = 'java -jar ' + self.logisim_path + 'logisim-generic-2.7.1.jar '
        command_with_file = command + os.path.join(self.grader_ref.file_list[self.grader_ref.cur_idx], MAIN_FILE_NAME)
        #  if self.grader_ref.logisim_pid.pid > 0:
        self.kill_logisim()
        self.grader_ref.logisim_pid = subprocess.Popen(command_with_file, shell=True)

    def generate_reports(self):
        """
        Function bound to 'Create reports' button.
        Calls generate_answers procedure from generate.py
        :return: nothing.
        """
        self.but_create_report.setDisabled(True)
        self.but_create_report.setText('Generating..')
        self.but_create_report.repaint()
        from generate import generate_answers
        # (resubmit_num, dir_name, lab_type, lab_num)
        if hasattr(self, 'grader_ref'):
            loc_settings = settings_db_read_settings()[1]
            generate_answers(self.grader_ref.attempt, self.grader_ref.working_dir,
                             self.grader_ref.lab_type, self.grader_ref.lab_num,
                             loc_settings[1], loc_settings[2], self.grader_name)
            self.but_create_report.setEnabled(True)
            self.but_create_report.setText('Create reports')



    # def open_dates_dialog(self):
    #     """
    #     Function bound to 'Create due dates' button.
    #     Creates new window, saves selected dates into files, but calling 'due_date_creator'
    #     :return: nothing.
    #     """
    #     self.new_window_but.setDisabled(True)
    #     self.cal_window = QtWidgets.QDialog()
    #     dui = Ui_Create_dates_dialog1()
    #     dui.setupUi(self.cal_window)
    #     # self.cal_window.finished.connect(self.check_new_win_result)
    #     self.cal_window.show()
    #     accepted = self.cal_window.exec_()
    #     if accepted:
    #         due_dates = list()
    #         due_dates.append(dui.init_subm_date_time.dateTime().toTime_t())
    #         due_dates.append(dui.first_subm_date_time.dateTime().toTime_t())
    #         due_dates.append(dui.second_subm_date_time.dateTime().toTime_t())
    #         due_dates.append(dui.third_subm_date_time.dateTime().toTime_t())
    #         due_location = dui.lab_path.text()
    #         self.due_date_creator(due_location, due_dates)
    #     self.new_window_but.setEnabled(True)

    def open_settings_dialog(self):
        """
        Function bound to 'Open settings button'
        Creates new window to edit settings stored in the settings database.
        :return: nothing.
        """
        self.settings_but.setDisabled(True)
        self.settings_but.repaint()
        self.settings_window = QtWidgets.QDialog()
        dui = Ui_Create_settings_dialog()
        dui.setupUi(self.settings_window)

        self.centralwidget.setDisabled(True)
        self.centralwidget.repaint()

        self.settings_window.show()
        self.settings_window.exec_()

        self.sync_params_to_settings()
        self.centralwidget.setEnabled(True)

        self.settings_but.setEnabled(True)

        if not self.manage_labs_but.isEnabled():
            from pathlib import Path
            settings_location = str(Path(os.path.expandvars(os.path.expanduser('./settings.sqlite3'))).absolute())
            if os.path.isfile(settings_location):
                self.manage_labs_but.setEnabled(True)


    def open_manage_labs_diag(self):
        """
        Function bound to 'Open mangage labs button'
        Creates new window to mangage labs(import, export).
        :return: nothing
        """
        self.manage_labs_but.setDisabled(True)
        self.manage_labs_but.repaint()
        self.centralwidget.setDisabled(True)
        self.centralwidget.repaint()
        self.manage_labs_window = QtWidgets.QDialog()
        dui = Ui_manage_labs1()
        dui.setupUi(self.manage_labs_window)

        self.manage_labs_window.show()
        self.manage_labs_window.exec_()

        self.centralwidget.setEnabled(True)
        self.manage_labs_but.setEnabled(True)

        if not self.but_file_open.isEnabled():
            paths, local = settings_db_read_settings()
            # if there are some labs in server sync directory:
            if len(os.walk(get_full_path(paths, local) + "/server_sync/").__next__()[1]) > 0:
                self.but_file_open.setEnabled(True)
                self.input_file_location.setEnabled(True)


class Ui_Create_settings_dialog(Ui_Settings):
    """
    Creates window that provides user with convenient way of changing settings that are stored in sqlite3 db.
    """

    def bind_functions(self):
        """
        Place where all the bindings happen.
        :return: nothing.
        """
        self.buttonBox.button(self.buttonBox.Reset).clicked.connect(self.update_user_input_with_paths)
        self.buttonBox.button(self.buttonBox.RestoreDefaults).clicked.connect(self.set_default_user_input_with_paths)
        self.buttonBox.button(self.buttonBox.Apply).clicked.connect(self.create_or_update_settings_db)
        self.buttonBox.button(self.buttonBox.Ok).clicked.connect(self.create_or_update_settings_db)

        # TODO: make 'personal' events and update only fields that have been changed
        self.input_logisim_path.textChanged.connect(self.set_apply_restet_active)
        self.input_local_stor.textChanged.connect(self.set_apply_restet_active)
        self.input_rem_stor.textChanged.connect(self.set_apply_restet_active)
        self.input_grader_name.textChanged.connect(self.set_apply_restet_active)
        self.spin_year.valueChanged.connect(self.set_apply_restet_active)
        self.semester_comboBox.currentIndexChanged.connect(self.set_apply_restet_active)
        self.style_checkBox.stateChanged.connect(self.set_apply_restet_active)
        self.sync_command.textChanged.connect(self.set_apply_restet_active)
        self.input_grades_db.textChanged.connect(self.set_apply_restet_active)

    def setupUi(self, Settings):
        """
        Sets initial parameters for all needed fields
        :return: Nothing
        """
        super().setupUi(Settings)
        self.buttonBox.button(self.buttonBox.Reset).setDisabled(True)
        self.buttonBox.button(self.buttonBox.Apply).setDisabled(True)
        self.bind_functions()
        self.update_user_input_with_paths()

    def update_user_input_with_paths(self):
        """
        Reads settings parameters from DB and sets appropriate fields with obtained values
        Warning: dependa on a number of settings obtained from read_settings_data
        :return: Nothing
        """
        paths, local = self.read_settings_data()
        if paths and len(paths) >= 4:
            self.input_logisim_path.setText(paths[0])
            self.input_local_stor.setText(paths[1])
            self.input_rem_stor.setText(paths[2])
            self.input_grades_db.setText(paths[3])
            self.groupBox_user.setEnabled(True)

        if local and len(local) >= 4:
            self.input_grader_name.setText(local[0])
            self.spin_year.setValue(local[1])
            self.semester_comboBox.setCurrentIndex(int(local[2]))
            self.style_checkBox.setChecked(bool(local[3]))
            self.sync_command.setText(local[4])

        if (paths and len(paths) >= 4 ) and (local and len(local) >= 4):
            self.spin_year.setEnabled(True)
            self.semester_comboBox.setEnabled(True)
            self.style_checkBox.setEnabled(True)
            self.input_grader_name.setEnabled(True)
            self.sync_command.setEnabled(True)
        # if (local and len(local) > 5) or len(paths):
        #         print('Obtained more settings than expected. Please check Ui_Create_settings_dialog.')

        self.buttonBox.button(self.buttonBox.Reset).setDisabled(True)
        self.buttonBox.button(self.buttonBox.Apply).setDisabled(True)

    def set_default_user_input_with_paths(self):
        """
        Sets predefined values to the most important fields.
        Additionally enables Apply and Reset buttons
        :return:
        """
        self.input_logisim_path.setText("~/Downloads/")
        self.input_local_stor.setText("~/Documents/3130_labs/")
        self.input_grades_db.setText("~/Documents/3130_labs/grades.sqlite3")
        self.input_rem_stor.setText("")  # impossible to predict
        self.groupBox_user.setEnabled(True)
        self.buttonBox.button(self.buttonBox.Reset).setEnabled(True)
        self.buttonBox.button(self.buttonBox.Apply).setEnabled(True)

    def read_settings_data(self):
        """
        reads settings from settings DB by calling function supplied by db_init.py
        :return: None for error, list of fields for success
        """
        self.buttonBox.button(self.buttonBox.Reset).setEnabled(True)
        return settings_db_read_settings()

    def create_or_update_settings_db(self):
        """
        Checks if settings DB file exists.
        If NO - attempts to create one (depends on user's choice)
        If YES - reads paramenters with function supplied by db_init.py
        In future it will contain checks for grades.db
        :return:
        """
        from pathlib import Path
        settings_location = str(Path(os.path.expandvars(os.path.expanduser('./settings.sqlite3'))).absolute())
        if not os.path.isfile(settings_location):
            if self.open_simple_dialog("Do you want to create settings database ?"):
                if not settings_db_create(force=True):
                    raise Exception('Was not able to create SETTINGS db.')
        if len(self.input_local_stor.text()) > 0:
            if self.input_local_stor.text()[-1] != '/':
                self.input_local_stor.setText(self.input_local_stor.text() + '/')
        if len(self.input_rem_stor.text()) > 0:
            if self.input_rem_stor.text()[-1] != '/':
                self.input_rem_stor.setText(self.input_rem_stor.text() + '/')
        if len(self.input_logisim_path.text()) > 0:
            if self.input_logisim_path.text()[-1] != '/':
                self.input_logisim_path.setText(self.input_logisim_path.text() + '/')


        paths = (self.input_logisim_path.text(), self.input_local_stor.text(), self.input_rem_stor.text(),
                 self.input_grades_db.text())
        if os.path.isfile(settings_location):
            local = (self.input_grader_name.text(), int(self.spin_year.text()),
                    self.semester_comboBox.currentIndex(), self.style_checkBox.checkState(), self.sync_command.text())
            if len(self.input_local_stor.text()) > 0:
                local_stor = str(Path(os.path.expanduser(os.path.expandvars(self.input_local_stor.text()))).absolute())
                if local_stor[-1] != '/':
                    local_stor += '/'
                if not os.path.isdir(local_stor):
                    os.mkdir(local_stor)
                local_grading_path = local_stor + self.spin_year.text() + '_' +\
                                     str(self.semester_comboBox.currentIndex())
                if not os.path.isdir(local_grading_path):
                    os.mkdir(local_grading_path)
            update_settings(paths, local)


        grades_location = str(Path(os.path.expandvars(os.path.expanduser(self.input_grades_db.text()))).absolute())
        if len(self.input_grades_db.text()) > 1 and not os.path.isfile(grades_location):
            if self.open_simple_dialog("Do you want to create GRADES database ?"):
                print('Before grades creation.')
                if not grades_db_create(grades_location, force=True):
                    raise Exception('Was not able to create GRADES db.')

        if os.path.isfile(settings_location) and os.path.isfile(grades_location):
            self.buttonBox.button(self.buttonBox.Apply).setDisabled(True)
            self.buttonBox.button(self.buttonBox.Apply).repaint()
            self.buttonBox.button(self.buttonBox.Reset).setDisabled(True)
            self.buttonBox.button(self.buttonBox.Reset).repaint()
            if not self.groupBox_user.isEnabled():
                self.groupBox_user.setEnabled(True)
            if not self.input_logisim_path.isEnabled():
                self.input_logisim_path.setEnabled(True)
                self.label_logisim_path.setEnabled(True)
            if not self.input_local_stor.isEnabled():
                self.input_local_stor.setEnabled(True)
                self.label_local_stor.setEnabled(True)
            if not self.input_rem_stor.isEnabled():
                self.input_rem_stor.setEnabled(True)
                self.label_rem_stor.setEnabled(True)
            if not self.spin_year.isEnabled():
                self.spin_year.setEnabled(True)
            if not self.semester_comboBox.isEnabled():
                self.semester_comboBox.setEnabled(True)
            if not self.style_checkBox.isEnabled():
                self.style_checkBox.setEnabled(True)
            if not self.input_grader_name.isEnabled():
                self.input_grader_name.setEnabled(True)
            if not self.sync_command.isEnabled():
                self.sync_command.setEnabled(True)

        # if len(self.input_local_stor.text()) > 1:
        #     full_path = Path(self.input_local_stor.text()).absolute()
        #     if not os.path.exists(full_path) or not os.path.isdir(full_path):
        #         os.makedirs(full_path)



    def set_apply_restet_active(self):
        """
        Enables reset and apply buttons
        :return: Nothing
        """
        self.buttonBox.button(self.buttonBox.Reset).setEnabled(True)
        self.buttonBox.button(self.buttonBox.Apply).setEnabled(True)

    def __dummy(self):
        print('dummy exec')

    def open_simple_dialog(self, phrase):
        """
        Creates simple Ok|Cancel dialog and returns user's choice
        :param phrase: Phrase to ask the user
        :return: True for Ok, False otherwise
        """
        self.simple_diag = QtWidgets.QDialog()
        dui = SimpleDialog()
        dui.setupUi(self.simple_diag, phrase)

        self.buttonBox.setDisabled(True)
        self.buttonBox.repaint()

        self.simple_diag.setWindowTitle('Settings confirmation')
        self.simple_diag.show()

        result = self.simple_diag.exec_()

        self.buttonBox.setEnabled(True)

        return result


class SimpleDialog(Ui_Dialog):
    """
    Wrapper class for very simple Ok|Cancel dialog
    """
    def setupUi(self, Dialog, phrase):
        """
        :param phrase: Phrase to display
        :return: Nothing
        """
        super().setupUi(Dialog)
        self.label_main_question.setText(phrase)


class Ui_manage_labs1(Ui_manage_labs):
    srv_sync_path = None
    selected_path = None
    selected_lab_name = None
    zip_files_len = None

    def bind_functions(self):
        self.labs_select_comboBox.currentIndexChanged.connect(self.update_status_bar)
        self.import_but.clicked.connect(self.import_lab)
        self.create_due_dates_but.clicked.connect(self.open_dates_dialog)
        # self.sync_but.clicked.connect(lambda i: self.sync_but.setDisabled(True))
        self.sync_but.clicked.connect(self.sync_files)
        self.export_but.clicked.connect(self.export_pdfs)

    def setupUi(self, manage_labs):
        super().setupUi(manage_labs)
        self.bind_functions()
        self.set_local_vars()

        try:
            self.scan_for_labs()
            if self.labs_select_comboBox.count() > 0:
                self.labs_select_comboBox.setEnabled(True)
                self.import_but.setEnabled(True)
                self.create_due_dates_but.setEnabled(True)
                self.export_but.setEnabled(True)
        except Exception as e:
            print('Error in manage labs. Probably your grading path was not set properly: ', e)


    def set_local_vars(self):
        pass

    def update_status_bar(self, force=False):
        # no need to scan files in background, but only when user selects it intentionally, or if it is first run
        if self.labs_select_comboBox.hasFocus() or force:
            self.selected_lab_name = self.labs_select_comboBox.currentText()
            self.selected_path = self.srv_sync_path + self.selected_lab_name + '/'
            zip_pdf_files = [f for f in os.listdir(self.selected_path) if '.zip' in f or '.pdf' in f]

            self.pdf_files_len = len([f for f in zip_pdf_files if f.split('.')[1] == 'pdf'])
            self.zip_files_len = len([f for f in zip_pdf_files if f.split('.')[1] == 'zip'])

            self.status_bar.setText("Contains " + str(self.zip_files_len) + ' zip files and ' + str(self.pdf_files_len) + ' pdf files.')

            if self.zip_files_len > 0 and not self.create_due_dates_but.isEnabled():
                self.export_but.setEnabled(True)
                self.import_but.setEnabled(True)
                self.labs_select_comboBox.setEnabled(True)

            # good_zip_files_size = len([f for f in zip_files if os.isfile(os.path.join(selected_path, f))])

    def sync_files(self):
        self.sync_but.setDisabled(True)
        self.sync_but.setText('Synchronizing...')
        self.sync_but.repaint()
        self.status_bar.setText("Synchronizing...")
        self.status_bar.repaint()
        sync_files()
        self.status_bar.setText("Done.")
        self.sync_but.setText('Sync to local storage')
        self.sync_but.setEnabled(True)

        sync_success = True  # there are no tools to check it at this point.
        if sync_success and not self.labs_select_comboBox.isEnabled():
            self.labs_select_comboBox.setEnabled(True)
            self.create_due_dates_but.setEnabled(True)
            self.scan_for_labs()
            #  TODO: There should be additional checks to enable import and export, but I do not have enough time to implement them.
            self.import_but.setEnabled(True)
            self.export_but.setEnabled(True)

    def scan_for_labs(self):
        """
        Scans local repository for labs to import into grading path
        Offers creation of the due date for particular lab.
        :return: Nothing
        """
        paths, local = settings_db_read_settings()
        # self.local_path = paths[1] + str(local[1]) + '_' + str(local[2]) + '/'
        self.main_lab_path = get_full_path(paths, local)
        self.srv_sync_path = self.main_lab_path + "/server_sync/"
        dirs = os.walk(self.srv_sync_path).__next__()[1]
        if len(dirs) > 0:
            self.labs_select_comboBox.addItems(sorted(dirs))
            self.labs_select_comboBox.setCurrentIndex(0)
            self.labs_select_comboBox.setFocus(True)
            self.update_status_bar(force=True)


    def import_lab(self):
        if self.selected_path:
            self.import_but.setDisabled(True)
            self.import_but.setText('Importing..')
            self.import_but.repaint()
            from datetime import datetime
            due_file = self.check_for_due_dates(self.selected_path)
            if len(due_file) < 4:
                self.status_bar.setText('Create due dates !')
                self.import_but.setEnabled(True)
                return False
            else:
                from shutil import copy2 as cp2
                zip_files = [f for f in os.listdir(self.selected_path) if 'zip' in f]
                real_zip_files_rev = sorted([f for f in zip_files if os.path.isfile(os.path.join(self.selected_path, f))], reverse=True)

                current_check, prev_due, next_due, current_timestamp = self.get_grading_period(self.selected_path, due_file)


                if current_timestamp < next_due:
                    # we cannot grade before the due date
                    self.status_bar.setText('Current date is less than next due date. It is too early to import.')
                    self.import_but.setText('Import labs')
                    self.import_but.setEnabled(True)
                    return False

                selected_files = []
                for file in real_zip_files_rev:
                    parts = file.split('.')[0].split('-')
                    if int(parts[2]) > prev_due and int(parts[2]) <= next_due:
                        if len(selected_files) == 0:
                            selected_files.append(file)
                        elif selected_files[-1].split('.')[0].split('-')[0] != parts[0]:
                            selected_files.append(file)

                penalty_mess = ''
                if current_check == 1:
                    penalty_mess = '100% - this is your max point(no resubmissions)'
                elif current_check == 2:
                    penalty_mess = '90% - first resubmission'
                elif current_check == 3:
                    penalty_mess = '70% - second resubmission'
                elif current_check == 4:
                    penalty_mess = '50% - third resubmission'

                lab_type, _, lab_num = self.selected_lab_name.split('_')
                max_points = get_lab_max_value(lab_type[0] + 'LA' + lab_num)
                lab_filename = get_lab_filename(lab_type[0] + 'LA' + lab_num)

                # temporary solution. path should be stored as local var
                paths_to_grading_dir = self.main_lab_path + '/' + self.selected_lab_name + '_' + str(current_check) + '/'

                proc_time = datetime.utcfromtimestamp(current_timestamp).strftime('%Y-%m-%d %H:%M:%S')

                # File manipulations goes below:

                if not os.path.isdir(paths_to_grading_dir):
                    os.makedirs(paths_to_grading_dir)

                imported_files_counter = 0
                for file in reversed(selected_files):
                    zipped_file = zipfile.ZipFile(self.selected_path + file)
                    extraction_dir = paths_to_grading_dir + file.split('.')[0]
                    zipped_file.extractall(paths_to_grading_dir + file.split('.')[0])
                    zipped_file.close()

                    subm_time = datetime.utcfromtimestamp(int(extraction_dir.split('-')[-1])).strftime('%Y-%m-%d %H:%M:%S')
                    # check for required files
                    if not lab_filename[0] or os.path.isfile(extraction_dir + '/' + lab_filename[0]):
                        lab_responce = 'I did not find any errors. Good job !'
                        cur_grade = max_points
                    else:
                        lab_responce = 'File "' + lab_filename[0] +'" was not found.\nThese files were found: ' +\
                                       " ".join(os.listdir(extraction_dir))
                        cur_grade = 0

                    # This check is for a case when you graded the lab and trying to import it again.
                    # No existing files should be wiped
                    if not os.path.isfile(extraction_dir+'/penalty.txt'):
                        with open(extraction_dir+'/penalty.txt', 'w') as f:
                            f.write(penalty_mess)

                    if not os.path.isfile(extraction_dir + '/grade.txt'):
                        with open(extraction_dir + '/grade.txt', 'w') as f:
                            f.write(str(cur_grade))

                    if not os.path.isfile(extraction_dir + '/responce.txt'):
                        with open(extraction_dir + '/responce.txt', 'w') as f:
                            f.write(lab_responce)

                    if not os.path.isfile(extraction_dir + '/tech_info.txt'):
                        with open(extraction_dir + '/tech_info.txt', 'w') as f:
                            f.writelines(['File was submited at %s<br/>\n' % subm_time,
                                         'I started processing your file at %s<br/>\n' % proc_time,
                                          "I found that your lab type is '%s' and it's number is %s <br/>" % (lab_type, lab_num),
                                          'So max points for this lab type is <u>%d</u><br/>' % max_points,
                                          'Theoretical max points: %s)' % penalty_mess])
                    imported_files_counter += 1

                cp2(self.selected_path + due_file[current_check-1], paths_to_grading_dir)

                check_filename = paths_to_grading_dir + 'check_' + str(current_check) + '_' + str(current_timestamp)
                with open(check_filename, 'w'): pass

                cp2(check_filename, self.selected_path)

                self.import_but.setEnabled(True)
                self.status_bar.setText("Imported " + str(imported_files_counter) + " files.")
                return True

        return False

    def get_grading_period(self, dir, due_files):
        # should comput correct grading period and return the due date in Unix timestamp format
        import time
        due_timestamps = [int(f.split('_')[2]) for f in due_files]
        check_files = [int(f.split('_')[2]) for f in os.listdir(dir) if 'check_' in f]
        if len(check_files) > 0:
            cur_check_num = len(check_files) + 1           # 1 + 1
            from_time = due_timestamps[cur_check_num - 2]  # 0 => after first due date
            to_time = due_timestamps[cur_check_num - 1]    # 1 => before second due date
        else:
            from_time = 0
            to_time = due_timestamps[0]
            cur_check_num = 1
        current_timestampt = int(time.time())
        return cur_check_num, from_time, to_time, current_timestampt

    def check_for_due_dates(self, dir):
        """
        It will be using old desing of due files.
        I am going to switch to DB due dates when the time comes.
        At this point DB has full support for it.
        :param dir:
        :return:
        """
        return sorted([f for f in os.listdir(dir) if 'due_' in f])


    def open_dates_dialog(self):
        """
        Function bound to 'Create due dates' button.
        Creates new window, saves selected dates into files, but calling 'due_date_creator'
        :return: nothing.
        """
        self.create_due_dates_but.setDisabled(True)
        self.create_due_dates_but.repaint()
        self.cal_window = QtWidgets.QDialog()
        dui = Ui_Create_dates_dialog1()
        dui.setupUi(self.cal_window, self.selected_lab_name)
        # self.cal_window.finished.connect(self.check_new_win_result)
        self.cal_window.show()
        accepted = self.cal_window.exec_()
        if accepted:
            due_dates = list()
            due_dates.append(dui.init_subm_date_time.dateTime().toTime_t())
            due_dates.append(dui.first_subm_date_time.dateTime().toTime_t())
            due_dates.append(dui.second_subm_date_time.dateTime().toTime_t())
            due_dates.append(dui.third_subm_date_time.dateTime().toTime_t())
            due_location = dui.lab_path.text()
            self.due_date_creator(due_location, due_dates)
        self.create_due_dates_but.setEnabled(True)

    # noinspection PyMethodMayBeStatic
    def due_date_creator(self, due_location, due_dates):
        """
        Saves due files into location specified by user.
        :param due_location: where to save.
        :param due_dates: list of dates to save.
        :return: nothing.
        """
        if len(due_location) > 1:
            i = 1
            for due_date in due_dates:
                with open('%sdue_%d_%d' % (due_location, i, due_date), 'w'):
                    i += 1
        else:
            print('Location was not specified.')

    def export_pdfs(self):
        self.export_but.setDisabled(True)
        self.export_but.setText('Exporting..')
        self.export_but.repaint()
        export_pdf()
        self.export_but.setText('Export pdfs')
        self.export_but.setEnabled(True)


class Ui_Create_dates_dialog1(Ui_Create_dates_dialog):

    def bind_functions(self):
        """
        Place where all the bindings happen.
        :return: Nothing
        """
        self.init_subm_date_time.dateTimeChanged.connect(self.date_select)
        # self.select_file_path.clicked.connect(self.open_file_diag)
        # self.lineEdit.left_clicked[int].connect(self.dummy_d)
        self.lab_path.dclicked.connect(self.open_file_diag)

    # noinspection PyMethodMayBeStatic
    def __dummy_d(self, nb):
        """
        It is here for testing new features
        :param nb:
        :return:
        """
        if nb == 1:
            print('Single left click ', nb)
        else:
            print('Double left click ', nb)

    # noinspection PyMethodMayBeStatic
    def __dummy_d_1(self):
        """
        It is here for testing new features
        :return:
        """
        print('Single left click ')

    def setupUi(self, Create_dates_dialog, selected_lab=''):
        """
        Initiates creation of the new window for
        due dates creation.
        Adds binded functions and sets some important variables (like current time).
        :param Create_dates_dialog - parent class generated with Qt5 Designer.
        :return: nothing.
        """
        super().setupUi(Create_dates_dialog)
        self.bind_functions()
        self.init_subm_date_time.setDateTime(QDateTime.currentDateTime())
        paths, local = settings_db_read_settings()
        good_path = get_full_path(paths, local) + '/server_sync/'
        try:
            good_path += selected_lab + '/'
        except Exception as e:
            print('Exception when tried to append selected folder from Manage labs. ', e)
        self.lab_path.setText(good_path)

    def date_select(self):
        """
        Automatically set next due dates.
        :return: nothing.
        """
        self.first_subm_date_time.setDateTime(self.init_subm_date_time.dateTime().addDays(7))
        self.second_subm_date_time.setDateTime(self.init_subm_date_time.dateTime().addDays(14))
        self.third_subm_date_time.setDateTime(self.init_subm_date_time.dateTime().addDays(21))

    def open_file_diag(self):
        """
        Creates File browser in a new window.
        :return: nothing.
        """
        obtained_dir = QFileDialog.getExistingDirectory(caption='Select where to create due files',
                                                        directory=self.lab_path.text())+'/'
        if len(obtained_dir) > 1:
            self.lab_path.setText(obtained_dir)


if __name__ == "__main__":
    # generate_final_grades('./grades.sqlite3', 2018, 1)
    # reconstruct_grades_and_comments()
    # update_lab_submissions_paths('./grades.sqlite3', '/home/vanya/Documents/3130_labs/2018/', 2018, 1)
    # import_previous_grades_into_db('./grades.sqlite3', 'grades.xls', 2018, 1)
    # load_student_list_into_grades_db('./grades.sqlite3', 2018, '1')

    # sync_files()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMainWindow1()
    ui.setupUi(MainWindow)
    # MainWindow.setStyleSheet(styleData)
    MainWindow.show()
    sys.exit(app.exec_())
