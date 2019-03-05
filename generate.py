import os
import shutil
from dateutil import tz
from datetime import datetime
from PyQt5.QtCore import QLocale
from PyQt5.QtCore import QDateTime, Qt
import sqlite3 as lite
import multiprocessing as mp
from db_init import get_pipids_in_class_by_year_semester, commit_gen_report, get_grades_by_lab_and_att, get_max_grade_for_lab
QLocale.setDefault(QLocale(QLocale.English))


def convert_to_pdf(html_file, func_type):
    """
    Provides different ways to generate pdf report.
    :param html_file: report in html format.
    :param func_type: selects the function used to generate pdf.
    :return: nothing, pdf is generated instead.
    """
    if func_type == "wkhtmltopdf":  # old way
        from subprocess import call
        call(["wkhtmltopdf", "-q", html_file, html_file[:-4] + 'pdf'])
    elif func_type == "pdfkit":  # best margins
        import pdfkit
        options = {
            'page-size': 'A4',
            'margin-top': '0.0in',
            'margin-right': '0.0in',
            'margin-bottom': '0.0in',
            'margin-left': '0.0in',
        }
        pdfkit.from_url(html_file, html_file[:-4] + 'pdf', options=options)
    elif func_type == 'weasyprint':  # potentially the fastest
        # if string is passed as param, but has margins problem
        from weasyprint import HTML
        with open(html_file, 'r') as html_in_file:
            cont = html_in_file.readlines()
        str_file = ''.join(cont)
        pdf = HTML(string=str_file)
        pdf.write_pdf(html_file[:-4] + 'pdf')


# def create_html_pdf_report(joined_path, stud_name, cur_dir, grade, max_points, penalty,
#                            final_score, top_part, bot_part, generated_time):
#     """
#     Creates nice html report for submitted labs and converts it to pdf format.
#     TODO: use latex instead of ugly html.
#     :param joined_path: working directory
#     :param stud_name: full student name(first, last)
#     :param cur_dir: directory with all labs(usually same as joined_path)
#     :param grade: what grade to assign.
#     :param max_points: max possible grade for this lab.
#     :param penalty: usually for resubmission, like 90%, 70%...
#     :param final_score: final grade = grade * penalty
#     :param top_part: predefined top part of html document
#     :param bot_part: predefined bottom part of html document
#     :param generated_time: some extra statistics for curious students.
#     :return: nothing, pdf is generated instead.
#     """
#     with open(joined_path + '-returned.html', 'w') as stud_report:
#         stud_report.writelines(top_part)
#         stud_report.write('<p>Grading directory : ' + cur_dir + ' </br>')
#
#         with open(joined_path + '/tech_info.txt', 'r') as tech_file:
#             stud_report.writelines(tech_file.readlines())
#
#         stud_report.write('</p><p><i>Dear ' + stud_name + ', ')
#
#         with open(joined_path + '/responce.txt', 'r') as resp_file:
#             stud_report.writelines(resp_file.readlines())
#
#         stud_report.write("</i></p>\n"
#                           "<p>According to the comment above, next grade was assigned: "
#                           "%d of %d <br/>\n \
#                           Your final grade is %d*%.1f=<b>%d</b> of %d <br/>\n"
#                           % (grade, max_points, grade, penalty, final_score, max_points))
#         stud_report.write('This report was generated {} </p>'.format(generated_time))
#         # TODO add current date/time
#         stud_report.writelines(bot_part)
#
#     convert_to_pdf(joined_path + '-returned.html', "pdfkit")
#     os.remove(joined_path + '-returned.html')
#

def create_html_pdf_report2(lab_dict):
    """
    Creates nice html report for submitted labs and converts it to pdf format.

    :return: nothing, pdf is generated instead.
    """
    with open('./answer.top', 'r') as partial_html:
        top_part = partial_html.readlines()

    with open('./answer.bottom', 'r') as partial_html:
        bot_part = partial_html.readlines()

    with open(lab_dict['lab_path'] + '-returned.html', 'w') as stud_report:
        stud_report.writelines(top_part)

        stud_report.write('<p>Grading directory : {} </br>'.format(lab_dict['lab_path'].split('/')[-1]))
        stud_report.write('Due date was {} <br/>'.format(time_to_str_with_tz(lab_dict['due_date'])))
        stud_report.write('File was submited at {} <br/>'.format(time_to_str_with_tz(lab_dict['submitted'])))
        stud_report.write('I imported your file at {} <br/>'.format(time_to_str_with_tz(lab_dict['import_date'])))
        if lab_dict['graded'] is not None:
            stud_report.write('I graded your lab at {} <br/>'.format(time_to_str_with_tz(lab_dict['graded'])))
        else:
            stud_report.write('I did not grad your lab or grade timestamp was not set.<br/>')
        stud_report.write('Lab type : \'{}\' and it\'s number is \'{}\' <br/>'.format(lab_dict['type'], lab_dict['num']))
        stud_report.write('</p><p><i>Dear {} {}, '.format(lab_dict['first_name'], lab_dict['second_name']))
        if lab_dict['grader_comment'] is None or len(lab_dict['grader_comment']) < 2:
            stud_report.write('There were no comments.')
        else:
            stud_report.write(lab_dict['grader_comment'])
        if lab_dict['extra_comment'] is not None and len(lab_dict['extra_comment']) > 0:
            stud_report.write('<br/>\nExtra comment: {}'.format(lab_dict['extra_comment']))

        stud_report.write("</i></p>\n"
                          "<p>According to the comment above, next grade was assigned: {} of {} <br/>\n"
                          " Your final grade is computed as {}*{:.1f}=<b>{}</b> of {} <br/>\n"
                          "".format(lab_dict['final_grade'], lab_dict['max_grade'], lab_dict['grade'], lab_dict['percent']/100, lab_dict['final_grade'], lab_dict['max_grade']))
        if lab_dict['grade'] == 0:
            stud_report.write('<br/>Don\'t forget to resubmit it by {} <br/><br/>\n'.format(time_to_str_with_tz(lab_dict['due_date'] + 604800)))  # one extra week
        stud_report.write('This report was generated {} </p>\n'.format(QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate)))

        stud_report.writelines(bot_part)

    convert_to_pdf(lab_dict['lab_path'] + '-returned.html', "pdfkit")
    os.remove(lab_dict['lab_path'] + '-returned.html')


def create_html_pdf_zero_report(filename, stud_name, top_part, bot_part):
    """
    Creates nice html report for nonsubmitted labs and converts it to pdf format.
    :param filename: filename with correct naming(zeroes instead of timestamp)
    :param stud_name: full student name(first, last)
    :param top_part: predefined top part of html document
    :param bot_part: predefined bottom part of html document
    :return:
    """
    with open(filename, 'w') as zeroes_file:
        zeroes_file.writelines(top_part)
        zeroes_file.write(stud_name + ' : You did not submit your lab. :(</p>\n')
        zeroes_file.write("<p>According to comments above, next grade was assigned : 0 </p>")
        zeroes_file.write("<p>Please submit your file before the next due date.")
        zeroes_file.writelines(bot_part)
    convert_to_pdf(filename, "pdfkit")
    os.remove(filename)


# def generate_answers(resubmit_num, dir_name, lab_type, lab_num, year, semester, grader_name):
#     """
#     general function that figures out max points, filenames, etc
#     and calls generate function with appropriate parameters
#     :param resubmit_num: resubmission attempt
#     :param dir_name: working dir
#     :param lab_type: open or closed lab
#     :param lab_num: just lab identifier
#     :param year: used wit semester to identify correct class list
#     :param semester: used wit year to identify correct class list
#     :param grader_name: name that will be displayed in the report
#     :return:
#     """
#     students = {}
#     # select
#
#     ids = get_pipids_in_class_by_year_semester(year, semester, 'grades.sqlite3')
#     with lite.connect('grades.sqlite3') as con:
#         cur = con.cursor()
#
#         for sid in ids.keys():
#             result = cur.execute('SELECT first_name, second_name FROM students WHERE pipeline_id=?', (str(sid),))
#             students[sid] = " ".join(result.fetchall()[0])
#
#     if not students:
#         with open('students_list1.txt', 'r') as stud_list_file:
#             temp_arr = stud_list_file.readlines()
#             for line in temp_arr:
#                 sid, name = line.split('%')
#                 students[sid.strip()] = name.strip()
#         del temp_arr
#
#
#     if lab_type == 'Closed':
#         max_points = 10
#         type_for_name = 'CL'
#     elif lab_type == 'Open':
#         max_points = 20
#         type_for_name = 'OL'
#     else:
#         raise Exception('Unknown lab type')
#
#     if resubmit_num == 1:
#         penalty = 1.0
#     elif resubmit_num == 2:
#         penalty = 0.9
#     elif resubmit_num == 3:
#         penalty = 0.7
#     elif resubmit_num == 4:
#         penalty = 0.5
#     else:
#         penalty = 0.0
#
#     generated_time = QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate)
#
#     print('This is ', type_for_name, ' lab, so max points is ', max_points)
#
#     try:
#         shutil.rmtree(dir_name + 'Answers', ignore_errors=True)
#         os.remove(dir_name + "grades.csv")
#         os.remove(dir_name + "grades_for_" + type_for_name + "lab_num.csv")
#     except Exception as e:
#         print('Exception during dir preparetion : ', e)
#
#     dirs = os.walk(dir_name).__next__()[1]
#
#     with open('./answer.top', 'r') as partial_html:
#         top_part = partial_html.readlines()
#
#     with open('./answer.bottom', 'r') as partial_html:
#         bot_part = partial_html.readlines()
#
#     grades = list()
#     for cur_dir in dirs:
#         student_id = cur_dir.split('-')[0]
#         joined_path = os.path.join(dir_name, cur_dir)
#         with open(joined_path + '/grade.txt', 'r') as grade_file:
#             grade = grade_file.readlines()
#
#         grade = int(grade[0].strip())
#         final_score = grade * penalty
#         grades.append((student_id, final_score))
#         create_html_pdf_report(joined_path, students[student_id], cur_dir, grade,
#                                max_points, penalty, final_score, top_part, bot_part, generated_time)
#
#     submitted = [x.split('-')[0] for x in dirs]
#
#     zeroes = list()
#     for student in students:
#         if student not in submitted:
#             grades.append((student, 0))
#             zeroes.append(student)
#
#     if resubmit_num == 1:
#         for student_id in zeroes:
#             filename = '%s/%s-%s%d-0000000000-returned' % \
#                        (dir_name, student_id, type_for_name, lab_num)
#             create_html_pdf_zero_report(filename+'.html', students[student_id], top_part, bot_part)
#
#     with open(dir_name + '/' + 'grades.csv', 'w') as grades_file:
#         for grade in sorted(grades):
#             grades_file.write("%s, %f \n" % grade)
#
#     os.mkdir(dir_name + '/Answers')
#     files = os.walk(dir_name).__next__()[2]
#     for file in files:
#         if file[-3:] == 'pdf':
#             shutil.move(dir_name + '/' + file, dir_name + '/Answers/' + file)
#
#     print('Done')
#
#
# def generate_answers2(resubmit_num, dir_name, lab_type, lab_num, year, semester, grader_name):
#     """
#     general function that figures out max points, filenames, etc
#     and calls generate function with appropriate parameters
#     :param resubmit_num: resubmission attempt
#     :param dir_name: working dir
#     :param lab_type: open or closed lab
#     :param lab_num: just lab identifier
#     :param year: used wit semester to identify correct class list
#     :param semester: used wit year to identify correct class list
#     :param grader_name: name that will be displayed in the report
#     :return:
#     """
#     students = {}
#     # select
#     import sqlite3 as lite
#     from db_init import get_ids_in_class_by_year_semester
#     ids = get_ids_in_class_by_year_semester(year, semester, 'grades.sqlite3')
#     with lite.connect('grades.sqlite3') as con:
#         cur = con.cursor()
#
#         for sid in ids.keys():
#             result = cur.execute('SELECT first_name, second_name FROM students WHERE pipeline_id=?', (str(sid),))
#             students[sid] = " ".join(result.fetchall()[0])
#
#     if not students:
#         with open('students_list1.txt', 'r') as stud_list_file:
#             temp_arr = stud_list_file.readlines()
#             for line in temp_arr:
#                 sid, name = line.split('%')
#                 students[sid.strip()] = name.strip()
#         del temp_arr
#
#
#     if lab_type == 'Closed':
#         max_points = 10
#         type_for_name = 'CL'
#     elif lab_type == 'Open':
#         max_points = 20
#         type_for_name = 'OL'
#     else:
#         raise Exception('Unknown lab type')
#
#     if resubmit_num == 1:
#         penalty = 1.0
#     elif resubmit_num == 2:
#         penalty = 0.9
#     elif resubmit_num == 3:
#         penalty = 0.7
#     elif resubmit_num == 4:
#         penalty = 0.5
#     else:
#         penalty = 0.0
#
#     generated_time = QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate)
#
#     print('This is ', type_for_name, ' lab, so max points is ', max_points)
#
#     try:
#         shutil.rmtree(dir_name + 'Answers', ignore_errors=True)
#         os.remove(dir_name + "grades.csv")
#         os.remove(dir_name + "grades_for_" + type_for_name + "lab_num.csv")
#     except Exception as e:
#         print('Exception during dir preparetion : ', e)
#
#     dirs = os.walk(dir_name).__next__()[1]
#
#     with open('./answer.top', 'r') as partial_html:
#         top_part = partial_html.readlines()
#
#     with open('./answer.bottom', 'r') as partial_html:
#         bot_part = partial_html.readlines()
#
#     grades = list()
#     for cur_dir in dirs:
#         student_id = cur_dir.split('-')[0]
#         joined_path = os.path.join(dir_name, cur_dir)
#         with open(joined_path + '/grade.txt', 'r') as grade_file:
#             grade = grade_file.readlines()
#
#         grade = int(grade[0].strip())
#         final_score = grade * penalty
#         grades.append((student_id, final_score))
#         create_html_pdf_report(joined_path, students[student_id], cur_dir, grade,
#                                max_points, penalty, final_score, top_part, bot_part, generated_time)
#
#     submitted = [x.split('-')[0] for x in dirs]
#
#     zeroes = list()
#     for student in students:
#         if student not in submitted:
#             grades.append((student, 0))
#             zeroes.append(student)
#
#     if resubmit_num == 1:
#         for student_id in zeroes:
#             filename = '%s/%s-%s%d-0000000000-returned' % \
#                        (dir_name, student_id, type_for_name, lab_num)
#             create_html_pdf_zero_report(filename+'.html', students[student_id], top_part, bot_part)
#
#     with open(dir_name + '/' + 'grades.csv', 'w') as grades_file:
#         for grade in sorted(grades):
#             grades_file.write("%s, %f \n" % grade)
#
#     os.mkdir(dir_name + '/Answers')
#     files = os.walk(dir_name).__next__()[2]
#     for file in files:
#         if file[-3:] == 'pdf':
#             shutil.move(dir_name + '/' + file, dir_name + '/Answers/' + file)
#
#     print('Done')

#
# def create_a_report(lab_dict):
#
#     create_html_pdf_report2( lab_dict)


def create_not_submitted(stud_id, lab_type, lab_num, dir_name):
    with open('./answer.top', 'r') as partial_html:
        top_part = partial_html.readlines()

    with open('./answer.bottom', 'r') as partial_html:
        bot_part = partial_html.readlines()
    filename = '%s/%s-%s%d-0000000000-returned' % \
               (dir_name, stud_id, lab_type, lab_num)
    create_html_pdf_zero_report(filename + '.html', stud_id, top_part, bot_part)


def generate_answers3(lid, att, year, semester, db_name='./grades.sqlite3'):
    all_ids = get_pipids_in_class_by_year_semester(year, semester)
    info_tup, info_desc = get_grades_by_lab_and_att(lid, att)
    col_names = [elem[0] for elem in info_desc]
    main_list = list()
    for tup in info_tup:
        a = dict()
        for i, elem in enumerate(tup):
            a[col_names[i]] = elem
        main_list.append(a)
    graded_students = [elem['pipeline_id'] for elem in main_list]
    grades = [elem['final_grade'] for elem in main_list]
    grade_dict = dict(zip(graded_students, grades))
    lab_type = main_list[0]['type']
    lab_num = main_list[0]['num']
    dir_name = main_list[0]['lab_path']
    dir_name = dir_name[:dir_name.rfind('/')]
    correctd_lab_type = 'CL' if lab_type == 'Closed' else 'OL'

    # for elem in main_list:
    #     create_a_report(elem)
    #
    # for elem in main_list:
    #     commit_gen_report(elem['grade_id'])

    not_subm_ids = [stud_id for stud_id in all_ids if stud_id not in graded_students]

    if len(main_list) + len(not_subm_ids) == 0:
        return

    ans_dir = os.path.join(dir_name, 'Answers')
    if os.path.exists(ans_dir):
        shutil.rmtree(ans_dir, ignore_errors=True)
    gr_file = os.path.join(dir_name, 'grades.csv')
    if os.path.exists(gr_file):
        os.remove(gr_file)
    gr_long_file = os.path.join(dir_name, "grades_for_{}lab_num.csv".format(correctd_lab_type))
    if os.path.exists(gr_long_file):
        os.remove(gr_long_file)
    files_to_rem = (os.path.join(dir_name, file) for file in (el for el in os.walk(dir_name).__next__()[2] if el[-3:] in ['pdf', 'html']))

    with mp.Pool() as pool:
        pool.map(os.remove, files_to_rem)
        r1 = pool.map_async(create_html_pdf_report2, main_list)
        r2 = pool.map_async(commit_gen_report, (elem['grade_id'] for elem in main_list))
        if att == 1:
            pool.starmap(create_not_submitted, ((stud_id, correctd_lab_type, lab_num, dir_name) for stud_id in not_subm_ids))
        r1.wait()
        r2.wait()

    with open(os.path.join(dir_name, '{}_lab_{}_grades.csv'.format(lab_num, lab_type)), 'w') as grades_file:
        grades_file.write("{1} Lab {0}, {1} Lab {0}\n".format(lab_num, lab_type))
        for stud_id in all_ids:
            if stud_id not in not_subm_ids:
                grades_file.write("{:s}, {:d}\n".format(stud_id, int(grade_dict[stud_id])))
            else:
                grades_file.write("{:s}, {:d}\n".format(stud_id, 0))


    best_grade_list = get_max_grade_for_lab(lid, year, semester)
    with open(os.path.join(dir_name, '{}_lab_{}_grades_best_so_far.csv'.format(lab_num, lab_type)), 'w') as grades_file:
        grades_file.write("{1} Lab {0}, {1} Lab {0}\n".format(lab_num, lab_type))
        for stud_tup in best_grade_list:
            grades_file.write('{}, {}\n'.format(stud_tup[0], stud_tup[1]))

    # for elem in main_list:
    #     create_html_pdf_report2(elem)
    # for elem in main_list:
    #     commit_gen_report(elem['grade_id'])

    # if att == 1:  # we do not form report for second attempt since most people are happy with previous grade
        # for stud_id in not_subm_ids:
        #     create_not_submitted(stud_id, correctd_lab_type, lab_num, dir_name)

    os.mkdir(os.path.join(dir_name, 'Answers'))
    files = os.walk(dir_name).__next__()[2]
    for file in files:
        if file[-3:] == 'pdf':
            shutil.move(os.path.join(dir_name, file), os.path.join(dir_name, 'Answers/{}'.format(file)))

    print('Done')


def time_to_str_with_tz(in_time):
    return datetime.utcfromtimestamp(in_time).replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).strftime('%m-%d-%Y %H:%M')
# if __name__ == '__main__':
#     # generate_answers(3, 'Open_Lab_3_3', 'Open', 3)
