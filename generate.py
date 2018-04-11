import os
import shutil
from PyQt5.QtCore import QLocale
from PyQt5.QtCore import QDateTime, Qt
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


def create_html_pdf_report(joined_path, stud_name, cur_dir, grade, max_points, penalty,
                           final_score, top_part, bot_part, generated_time):
    """
    Creates nice html report for submitted labs and converts it to pdf format.
    TODO: use latex instead of ugly html.
    :param joined_path: working directory
    :param stud_name: full student name(first, last)
    :param cur_dir: directory with all labs(usually same as joined_path)
    :param grade: what grade to assign.
    :param max_points: max possible grade for this lab.
    :param penalty: usually for resubmission, like 90%, 70%...
    :param final_score: final grade = grade * penalty
    :param top_part: predefined top part of html document
    :param bot_part: predefined bottom part of html document
    :param generated_time: some extra statistics for curious students.
    :return: nothing, pdf is generated instead.
    """
    with open(joined_path + '-returned.html', 'w') as stud_report:
        stud_report.writelines(top_part)
        stud_report.write('<p>Grading directory : ' + cur_dir + ' </br>')

        with open(joined_path + '/tech_info.txt', 'r') as tech_file:
            stud_report.writelines(tech_file.readlines())

        stud_report.write('</p><p><i>Dear ' + stud_name + ', ')

        with open(joined_path + '/responce.txt', 'r') as resp_file:
            stud_report.writelines(resp_file.readlines())

        stud_report.write("</i></p>\n"
                          "<p>According to the comment above, next grade was assigned: "
                          "%d of %d <br/>\n \
                          Your final grade is %d*%.1f=<b>%d</b> of %d <br/>\n"
                          % (grade, max_points, grade, penalty, final_score, max_points))
        stud_report.write('This report was generated ' + generated_time + '</p>')
        # TODO add current date/time
        stud_report.writelines(bot_part)

    convert_to_pdf(joined_path + '-returned.html', "pdfkit")
    os.remove(joined_path + '-returned.html')


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
        zeroes_file.write("<p>According to comments above, next grade was assigned : 0")
        zeroes_file.writelines(bot_part)
    convert_to_pdf(filename, "pdfkit")
    os.remove(filename)


def generate_answers(resubmit_num, dir_name, lab_type, lab_num):
    """
    general function that figures out max points, filenames, etc
    and calls generate function with appropriate parameters
    :param resubmit_num: resubmission attempt
    :param dir_name: working dir
    :param lab_type: open or closed lab
    :param lab_num: just lab identifier
    :return:
    """
    students = {}
    if not students:
        with open('students_list.txt', 'r') as stud_list_file:
            temp_arr = stud_list_file.readlines()
            for line in temp_arr:
                sid, name = line.split('%')
                students[sid.strip()] = name.strip()
        del temp_arr
    else:
        pass  # TODO add global student list ?

    if lab_type == 'Closed':
        max_points = 10
        type_for_name = 'CL'
    elif lab_type == 'Open':
        max_points = 20
        type_for_name = 'OL'
    else:
        raise Exception('Unknown lab type')

    if resubmit_num == 1:
        penalty = 1.0
    elif resubmit_num == 2:
        penalty = 0.9
    elif resubmit_num == 3:
        penalty = 0.7
    elif resubmit_num == 4:
        penalty = 0.5
    else:
        penalty = 0.0

    generated_time = QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate)

    print('This is ', type_for_name, ' lab, so max points is ', max_points)

    try:
        shutil.rmtree(dir_name + 'Answers', ignore_errors=True)
        os.remove(dir_name + "grades.csv")
        os.remove(dir_name + "grades_for_" + type_for_name + "lab_num.csv")
    except Exception as e:
        print('Exception during dir preparetion : ', e)

    dirs = os.walk(dir_name).__next__()[1]

    with open('./answer.top', 'r') as partial_html:
        top_part = partial_html.readlines()

    with open('./answer.bottom', 'r') as partial_html:
        bot_part = partial_html.readlines()

    grades = list()
    for cur_dir in dirs:
        student_id = cur_dir.split('-')[0]
        joined_path = os.path.join(dir_name, cur_dir)
        with open(joined_path + '/grade.txt', 'r') as grade_file:
            grade = grade_file.readlines()

        grade = int(grade[0].strip())
        final_score = grade * penalty
        grades.append((student_id, final_score))
        create_html_pdf_report(joined_path, students[student_id], cur_dir, grade,
                               max_points, penalty, final_score, top_part, bot_part, generated_time)

    submitted = [x.split('-')[0] for x in dirs]

    zeroes = list()
    for student in students:
        if student not in submitted:
            grades.append((student, 0))
            zeroes.append(student)

    if resubmit_num == 1:
        for student_id in zeroes:
            filename = '%s/%s-%s%d-0000000000-returned' % \
                       (dir_name, student_id, type_for_name, lab_num)
            create_html_pdf_zero_report(filename+'.html', students[student_id], top_part, bot_part)

    with open(dir_name + '/' + 'grades.csv', 'w') as grades_file:
        for grade in sorted(grades):
            grades_file.write("%s, %f \n" % grade)

    os.mkdir(dir_name + '/Answers')
    files = os.walk(dir_name).__next__()[2]
    for file in files:
        if file[-3:] == 'pdf':
            shutil.move(dir_name + '/' + file, dir_name + '/Answers/' + file)

    print('Done')


# if __name__ == '__main__':
#     # generate_answers(3, 'Open_Lab_3_3', 'Open', 3)
