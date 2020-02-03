#!/usr/bin/python3

import sqlite3 as lite
import os
import os.path
# import pandas as pd

SETTINGS_DB_NAME = './work/settings.sqlite3'  # Default settings filename


def settings_db_create(db_name=SETTINGS_DB_NAME, force=False):
    """
    Creates sqlite3 database with settings in app's root directory.
    If found file with the same name - asks user to overwrite it, but only if force flag is False
    :param db_name: name of the database in app's root directory
    :param force: flag to overwrite existing db
    :return: False if wrong name was supplied, True after database was created
    """
    if not force and os.path.isfile(db_name):
        user_choice = input('Do you really want to drop database ? Type "yes" to continue\n ')
        if not user_choice.isalpha() or not user_choice.lower() == 'yes':
            return False

    # DB creation logic goes here
    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.execute('DROP TABLE IF EXISTS PATHS')
        cur.execute("CREATE TABLE PATHS "
                    "( LOGISIM_HOME VARCHAR NOT NULL,\
                       GRADING_PATH VARCHAR NOT NULL,\
                       IMPORT_PATH  VARCHAR,\
                       GRADES_DB  VARCHAR); ")
        cur.execute("CREATE TABLE LOCAL (\
                    GRADER_NAME VARCHAR,\
                    YEAR        INT,\
                    SEMESTER    CHAR (1),\
                    USE_STYLE   BOOLEAN,\
                     SYNC_COMMAND VARCHAR);")
        con.commit()
    return True


def settings_db_read_settings(db_name=SETTINGS_DB_NAME):
    """
    Reads settings from the DB with specified name in 'db_name'
    :param db_name: name of DB to query
    :return: paths - list of paths to various locations and local - info about grader, grading year, etc.
    """
    paths = local = None
    if os.path.isfile(db_name):
        with lite.connect(db_name) as con:
            cur = con.cursor()
            result = cur.execute("SELECT LOGISIM_HOME, GRADING_PATH, IMPORT_PATH, GRADES_DB\
                                  FROM PATHS")
            paths = result.fetchone()
            result = cur.execute("SELECT GRADER_NAME, YEAR, SEMESTER, USE_STYLE, SYNC_COMMAND\
                                              FROM LOCAL")
            local = result.fetchone()

    return paths, local


def update_settings(paths, local, db_name=SETTINGS_DB_NAME):
    """
    Procedure that loads parameters specified in paths and local into settings DB
    :param paths: list of paths to various locations
    :param local: local - info about grader, grading year, etc.
    :param db_name: name of DB to query to update
    :return: nothing
    """
    if os.path.isfile(db_name):
        with lite.connect(db_name) as con:
            cur = con.cursor()
            cur.execute('DELETE FROM PATHS;')
            cur.execute('INSERT OR REPLACE INTO PATHS (LOGISIM_HOME, GRADING_PATH, IMPORT_PATH, GRADES_DB)'
                        ' VALUES (?, ?, ?, ?);', paths)
            cur.execute('DELETE FROM LOCAL;')
            cur.execute('INSERT OR REPLACE INTO LOCAL (GRADER_NAME, YEAR, SEMESTER, USE_STYLE, SYNC_COMMAND)'
                        'VALUES (?, ?, ?, ?, ?);', local)
            con.commit()

        with lite.connect(db_name) as con:
            cur = con.cursor()
            cur.execute('VACUUM;')
            con.commit()


def grades_db_create(db_name, force=False):
    """
    Will create database that contains all information about grades
    :param db_name: path and name of the database
    :param force: flag to overwrite existing db
    :return: Unknown
    """
    # from pathlib import Path
    print("I am going to create a grades DB with next name: ", db_name)
    db_name = str(db_name)
    if not os.path.isfile(db_name) or force:
        # compute some vars before the connection
        lab_names = list()
        for i in range(1, 13):
            lab_names.append(('CLA' + str(i), 'Closed', i, 10))
        for i in range(1, 9):
            lab_names.append(('OLA' + str(i), 'Open', i, 20))
        lab_names.append(('OLA9', 'Open', 9, 100))
        a = list(zip(*lab_names))
        a.append(('initial_labs.circ', 'initial_labs.circ', 'seven_seg.circ', 'RSC.circ', 'custom_reg.circ', 'RSC.circ', 'RSC.circ', 'RSC.circ', 'PLDs.circ', 'PLDs.circ', 'PLDs.circ', '', '','', 'bin_converter.circ', 'mod_counter.circ', 'custom_reg.circ', 'RSC.circ', 'RSC.circ', 'ram2.txt', ''))
        b = list(zip(*a))

        with lite.connect(db_name) as con:
            cur = con.cursor()
            # TODO: force should remove 'IF NOT EXISTS' and add 'DROP TABLE' to ensure new table creation
            # WISH: add TRY blocks for each CREATE and spawn new info window in case of error
            print('Creating students...')
            cur.execute("""CREATE TABLE students (
                            pipeline_id    TEXT    NOT NULL
                                                   PRIMARY KEY,
                            first_name     TEXT    NOT NULL,
                            second_name    TEXT    NOT NULL,
                            comment        TEXT,
                            cheating_ratio INTEGER DEFAULT (0)    );""")
            con.commit()
            print('Done.')
            print('Creating semesters...')
            cur.execute("""CREATE TABLE semesters (
                            semester CHAR (1) NOT NULL PRIMARY KEY,
                            name     VARCHAR      );""")
            con.commit()
            print('Done.')
            print('Creating class...')
            cur.execute("""CREATE TABLE class (
                            id             INTEGER PRIMARY KEY AUTOINCREMENT,
                            pipeline_id    TEXT    REFERENCES students (pipeline_id),
                            year           INTEGER,
                            semester       INTEGER REFERENCES semesters (semester),
                            cheating_ratio INTEGER DEFAULT (0),
                            UNIQUE (
                                pipeline_id,
                                year,
                                semester)     );""")
            con.commit()
            print('Done.')
            print('Creating labs...')
            cur.execute("""CREATE TABLE lab_names (
                            id              INT     NOT NULL PRIMARY KEY,
                            type            TEXT    NOT NULL,
                            num             INTEGER NOT NULL,
                            max_grade       INTEGER NOT NULL,
                            name            VARCHAR,
                            description     VARCHAR,
                            grader_comment  VARCHAR,
                            mandatory_files VARCHAR );""")
            con.commit()
            print('Done.')
            print('Creating grades...')
            cur.execute("""CREATE TABLE grades (
                            id               INTEGER PRIMARY KEY AUTOINCREMENT,
                            class_id                 NOT NULL
                                                     REFERENCES class (id) ON UPDATE CASCADE,
                            lab                      NOT NULL
                                                     REFERENCES lab_names (id) ON UPDATE CASCADE,
                            attempt          INT     DEFAULT (0),
                            submitted        INTEGER,
                            graded           INTEGER,
                            grader           VARCHAR,
                            grade            INTEGER NOT NULL
                                                     DEFAULT (0),
                            pass_fail        BOOLEAN NOT NULL
                                                     DEFAULT (0),
                            grader_comment   TEXT,
                            extra_comment    TEXT,
                            report_generated BOOLEAN,
                            report_time      INTEGER,
                            lab_path         VARCHAR,
                            UNIQUE (
                                class_id,
                                lab,
                                attempt,
                                pass_fail) ON CONFLICT REPLACE );""")
            con.commit()
            print('Done.')

            print("Creating penalties...")
            cur.execute("""CREATE TABLE penalties (
                            id        INTEGER PRIMARY KEY AUTOINCREMENT,
                            percent   INTEGER NOT NULL
                        );""")
            con.commit()
            print("Done.")

            print('Creating lab schedule...')
            cur.execute("""CREATE TABLE lab_schedule (
                            id         INTEGER PRIMARY KEY AUTOINCREMENT,
                            lab_id             REFERENCES lab_names (id),
                            year       INTEGER NOT NULL,
                            semester   INTEGER REFERENCES semesters (semester)
                                               NOT NULL,
                            due_date_1 INTEGER,
                            due_date_2 INTEGER,
                            due_date_3 INTEGER,
                            due_date_4 INTEGER,
                            imported_1 INTEGER,
                            imported_2 INTEGER,
                            imported_3 INTEGER,
                            imported_4 INTEGER,
                            posted_1   INTEGER,
                            posted_2   INTEGER,
                            posted_3   INTEGER,
                            posted_4   INTEGER
                        );""")
            con.commit()
            print('Done.')



            print('Filling semesters...')
            cur.executemany('INSERT OR REPLACE INTO semesters\
                        (semester, name) VALUES (?, ?)', [(1, 'SPRING'), (2, 'SUMMER'), (3, 'FALL')])
            con.commit()
            print('Done.')
            print('Filling labs...')
            cur.executemany('INSERT OR REPLACE INTO lab_names\
                        (id, type, num, max_grade, mandatory_files) VALUES (?, ?, ?, ?, ?)', b)
            con.commit()
            print('Done.')
            print('Filling penalties...')
            cur.executemany('INSERT INTO penalties\
                        (percent) VALUES (?)', [(100,), (90,), (70,), (50,)])
            con.commit()
            print("Done.")
            print('Vacuuming...')

            cur.execute('VACUUM;')
            con.commit()

            print('Done.')
            print('Creation of GRADES DB finished.')

            return True


def load_student_list_into_grades_db(db_name, year, semester, filename='students_list3.txt'):
    """
    Imports list of students from file in format: `id % lname, fname` into Grades DB.
    Should be called before first grading.
    :param db_name: db that contains grades and student info
    :param year: grading (current) year
    :param semester: grading (current) semester
    :param filename: file that contains student list
    :return: nothing
    """

    with open(filename, 'r') as sl:
        ids, names = zip(*(line.strip().split('%') for line in sl))
        ids = list(sid.strip() for sid in ids)
        names = (name.strip() for name in names)  # for case when file contains extra whitespaces
        lname, fname = zip(*(namer.split(',') for namer in names))
        lname = (name.strip() for name in lname)
        fname = (name.strip() for name in fname)

    if os.path.isfile(db_name):
        insert_students(ids, fname, lname, db_name)
        register_students_in_class(ids, year, semester, db_name)


def insert_students(ids, fname, lname, db_name='./grades.sqlite3'):
    """
    Takes students' info from the parameters and insert them into grades DB
    :param ids: pipeline ids
    :param fname: first name
    :param lname: last name
    :param db_name: specific name for grades DB
    :return: nothing
    """
    names_tupple = list(zip(ids, fname, lname, [0] * len(ids)))
    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.executemany('INSERT OR REPLACE INTO STUDENTS \
                    (pipeline_id, first_name, second_name, cheating_ratio)'
                        ' VALUES (?, ?, ?, ?)', names_tupple)
        con.commit()


def register_students_in_class(pipeline_ids, year, semester, db_name='./grades.sqlite3'):
    """

    :param pipeline_ids:
    :param year:
    :param semester:
    :param db_name:
    :return:
    """
    len_id = len(pipeline_ids)
    names_tupple = list(zip(pipeline_ids, [year] * len_id, [semester] * len_id, [0] * len_id))
    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.executemany('INSERT OR REPLACE INTO class\
                    (pipeline_id, year, semester, cheating_ratio) VALUES (?, ?, ?, ?)', names_tupple)
        con.commit()


def get_pipeline_ids(db_name='./grades.sqlite3'):
    """

    :param db_name:
    :return:
    """
    with lite.connect(db_name) as con:
        cur = con.cursor()
        result = cur.execute("SELECT pipeline_id FROM students")
        try:
            resut = (ids[0] for ids in result.fetchall())
        except Exception as e:
            print(e)
            return None
    return resut


def get_ids_in_class_by_year_semester(year, semester, db_name='./grades.sqlite3'):
    """

    :param year:
    :param semester:
    :param db_name:
    :return:
    """
    with lite.connect(db_name) as con:
        cur = con.cursor()
        result = cur.execute("SELECT pipeline_id, id FROM class\
                             WHERE year=" + str(year) + " and semester=" + str(semester))
        try:
            res = result.fetchall()
            pip_to_id = dict(res)
            to_id_to_pip = dict([(res_id[1], res_id[0]) for res_id in res])
        except Exception as e:
            print(e)
            return None
    return pip_to_id, to_id_to_pip


def import_previous_grades_into_db(year, semester, db_name='./grades.sqlite3', filename='./grades.xls'):
    """
    Takes xls file with grades from previous semester(s) and loads all grades into DB.
    In case students are not found in the DB and xls file contains ids - loads them too
    :param year: year when grades were assigned
    :param semester: semester when grades were assigned
    :param db_name: specific name of the grades DB
    :param filename: xls file to load
    :return: nothing
    """
    if not os.path.isfile(db_name):
        raise Exception("DB not found")

    df1 = pd.read_excel(filename)

    try:
        cls = df1.filter(like='CL')
    except Exception as e:
        print(e)
        cls = None  # no CLA's found

    try:
        ols = df1.filter(like='OL')
    except Exception as e:
        print(e)
        ols = None  # no OLAs found

    try:
        ids = df1.filter(like='sername').values.ravel().tolist()
        ids_len = len(ids)
    except Exception as e:
        print('Was not able to parse user ids, check xls file you are trying to import: ', e)
        raise e  # may be improved in the future - strange case
    try:
        names = df1.filter(like='Name').values.ravel().tolist()
    except Exception as e:  # either does not exist or has different name
        print(e)
        names = None

    class_dict = get_ids_in_class_by_year_semester(year, semester, db_name)

    if (not class_dict and not names) or (class_dict and len(class_dict) < ids_len and not names):
        raise Exception('Did not find ids in table CLASS and did not find names in xls file')
    elif names and (not class_dict or (class_dict and len(class_dict) < ids_len)):
        print('Did not find existing students, but found names in xsl\nAdding new students...\n')
        existing_ids = get_pipeline_ids(db_name)
        need_to_update_students = False
        # otherwise just add ids to the class list
        if existing_ids:
            for sid in ids:
                if sid not in existing_ids:
                    need_to_update_students = True
        else:
            need_to_update_students = True

        if need_to_update_students:
            fname, lname = zip(*(name.split(', ') for name in names))
            fname = (name.strip() for name in fname)
            lname = (name.strip() for name in lname)
            insert_students(ids, fname, lname, db_name)
        register_students_in_class(ids, year, semester, db_name)

    class_ids = [class_dict[sid] for sid in ids]
    if ols is None and cls is None or len(class_ids) == 0:
        raise Exception('No grades to load')

    grades_tupples = list()
    if ols is not None:
        for lab_name in ols:
            grades = (str(grade) for grade in ols[lab_name].values)
            grades_tupples += list(zip(class_ids, [lab_name] * ids_len, [-1] * ids_len, grades, ['TRUE'] * ids_len))

    if cls is not None:
        for lab_name in cls:
            grades = (str(grade) for grade in cls[lab_name].values)
            grades_tupples += list(zip(class_ids, [lab_name] * ids_len, [-1] * ids_len, grades, ['TRUE'] * ids_len))

    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.executemany('INSERT OR REPLACE INTO grades\
                    (class_id, lab, attempt, grade, pass_fail) VALUES (?, ?, ?, ?, ?)', grades_tupples)
        con.commit()


def gen_filenotfound_resp(lab_id, stud_path, corr_file, grader, att=None, next_date=None, db_name='./grades.sqlite3'):
    resp_text = 'file with name "{}" was not found.</br>'.format(corr_file)
    file_found = os.listdir(stud_path)
    potential_files = list()
    for file in file_found:
        if file not in ['grade.txt', 'penalty.txt', 'responce.txt', 'tech_info.txt', ]:
            potential_files.append(file)
    if potential_files:
        resp_text += '\nNext files|folders were found:</br>\n'
    for file in potential_files:
        if os.path.isdir(os.path.join(stud_path, file)):
            resp_text += file + ' - directory.</br>\n'
        else:
            resp_text += file + ' - regular file.</br>\n'

    if att and att < 4 and next_date:
        resp_text += 'Please submit your file by next due date ({}).</br>\n'.format(next_date)

    if not os.path.isfile(db_name):
        raise Exception("DB not found")
    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.execute("UPDATE `grades` SET `graded`=strftime('%s','now'), `pass_fail`=?, `grader_comment`=?, `grader`=? WHERE `id`=?", (False, resp_text, grader, lab_id))
        con.commit()


def get_resp_and_grade(grade_id, db_name='./grades.sqlite3'):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        result = cur.execute("SELECT grade, grader_comment, extra_comment, graded FROM grades WHERE id=?", (grade_id,))
        grade, resp, uresp, graded = result.fetchone()

    return grade, resp, uresp, graded


def get_prev_resp(grade_id, class_id, lab_id, db_name='./grades.sqlite3'):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        result = cur.execute("SELECT grader_comment, extra_comment FROM grades WHERE class_id=? AND lab=? AND id<?", (class_id, lab_id, grade_id))
        res = result.fetchall()
    if len(res) == 0:
        return ''
    else:
        gresp, uresp = zip(*res)
        return '\n'.join(('{} :\n{}'.format(gresp[i], uresp[i]) for i in range(len(gresp))))


def save_a_grade_to_db(grade_id, grade, grader_comment, extra_comment, grader_name, graded=True, pass_fail=True, db_name='./grades.sqlite3'):
    pass


# def get_submissions_to_grade(lab_id, att, db_name='./grades.sqlite3'):
#     if not os.path.isfile(db_name):
#         raise Exception("DB not found")
#     with lite.connect(db_name) as con:
#         cur = con.cursor()
#         result = cur.execute("SELECT id, FROM grades where lab=lab_id attempt=att and graded is NULL")
#         try:
#             lab_id, lab_type, lab_num = zip(*result.fetchall())
#         except Exception as e:
#             print(e)
#             return None, None, None
#     return lab_id, lab_type, lab_num


def init_new_lab(stud_id, lab_name, att, submitted, lab_path, db_name='./grades.sqlite3'):
    if not os.path.isfile(db_name):
        raise Exception("DB not found")
    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.execute('INSERT INTO grades (class_id, lab, attempt, submitted, lab_path) VALUES (?, ?, ?, ?, ?)', (stud_id, lab_name, att, submitted, lab_path))
        con.commit()


def get_lab_names(db_name='./grades.sqlite3'):
    """

    :param db_name:
    :return:
    """
    with lite.connect(db_name) as con:
        cur = con.cursor()
        result = cur.execute("SELECT id, type, num FROM lab_names")
        try:
            lab_id, lab_type, lab_num = zip(*result.fetchall())
        except Exception as e:
            print(e)
            return None, None, None
    return lab_id, lab_type, lab_num


def update_lab_submissions_paths(db_name, repository_root, year, semester):
    import fnmatch
    import glob
    # import_previous_grades_into_db(year, semester, db_name, repository_root+'grades.xlsx')
    lab_id, lab_type, lab_num = get_lab_names()
    if lab_id is None or lab_type is None or lab_num is None:
        raise Exception("Error during lab type/num import: ")
    class_dict = get_ids_in_class_by_year_semester(year, semester, db_name)
    total_labs = len(lab_type)

    all_dirs = list()
    for lab_iter in range(total_labs):
        for attempt in range(1, 5):  # class rule - 4 attempts
            full_lab_name = repository_root + lab_type[lab_iter] + '_Lab_' + str(lab_num[lab_iter]) + '_' + str(attempt) + '/'
            print('Processing ', full_lab_name)
            for stud_id in class_dict.keys():
                found_dir = glob.glob(full_lab_name+stud_id+'*')
                if found_dir:
                    # since it is initial pass, we do not set pass/fail. It will be set later with grade and comment.
                    all_dirs.append((class_dict[stud_id], lab_id[lab_iter], attempt, 'FALSE', found_dir[-1]))

    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.executemany('INSERT OR REPLACE INTO grades (class_id, lab, attempt, pass_fail, lab_path)'
                        ' VALUES (?, ?, ?, ?, ?)', all_dirs)
        con.commit()


def get_empty_grades_by_lid(lab_id, att, db_name='./grades.sqlite3'):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        result = cur.execute("SELECT submitted, class_id, id, lab_path FROM grades WHERE lab=? AND attempt=? AND graded is NULL", (lab_id, att))
        try:
            subm, class_id, lab_id, lab_path = zip(*result.fetchall())
        except Exception as e:
            # print(e)
            return None, None, None, None

    return subm, class_id, lab_id, lab_path


def get_all_grades_by_lid(lab_id, att, db_name='./grades.sqlite3'):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        result = cur.execute("SELECT submitted, class_id, id, lab_path FROM grades WHERE lab=? AND attempt=? ", (lab_id, att))
        try:
            subm, class_id, lab_id, lab_path = zip(*result.fetchall())
        except Exception as e:
            print(e)
            return None, None

    return subm, class_id, lab_id, lab_path


def reconstruct_grades_and_comments(db_name='./grades.sqlite3'):
    lab_id, lab_path = get_empty_grades(db_name)
    updated_grades = list()
    for l_iter in range(len(lab_path)):
        lpath = lab_path[l_iter]
        submition_t = int(lpath.split('-')[-1])
        try:
            with open(lpath+'/grade.txt', 'r') as gfile:
                cur_grade = int(gfile.readline().strip())
        except Exception as e:
            print("Error during grade file reading :", e)
            cur_grade = 0
        try:
            cur_t_graded = int(os.path.getmtime(lpath + '/grade.txt'))
        except Exception as e:
            print("Error during grade file statistics retrieval: ", e)
            cur_t_graded = None

        pass_fail = 'TRUE' if cur_grade else 'FALSE'
        try:
            with open(lpath+'/responce.txt', 'r') as rfile:
                cur_resp = rfile.readlines()
                if type(cur_resp) == list:
                    cur_resp = ' '.join(cur_resp)
        except Exception as e:
            print("Error during grade file reading", e)
            cur_resp = 'NULL'
        updated_grades.append((submition_t, cur_grade, cur_t_graded, pass_fail, cur_resp, lab_id[l_iter]))


    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.executemany('UPDATE grades SET submitted=?, grade=?, graded=?, pass_fail=?, grader_comment=? '
                        'WHERE id=?', updated_grades)
        con.commit()

    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.execute('VACUUM;')
        con.commit()


def generate_final_grades(db_name, year, semester):
    ids = get_ids_in_class_by_year_semester(year, semester, db_name)
    with lite.connect(db_name) as con:
        cur = con.cursor()

        labs = list()
        for sid in ids.values():  # using JOIN here will add too much extra data
            result = cur.execute('SELECT lab, MAX(grade * (select percent from penalties where id=GRADES.attempt)/100) '
                            'FROM GRADES WHERE class_id=? and attempt > 0 group by lab order by lab', (str(sid),))
            labs.append(result.fetchall() )

        stud_info = list()
        for sid in ids.keys():
            result = cur.execute('SELECT first_name, second_name FROM students WHERE pipeline_id=?', (str(sid),))
            stud_info.append(result.fetchall() )

    df_stud_info = pd.DataFrame(dict(zip(ids.keys(), stud_info)))
    df_grades = pd.DataFrame(dict(zip(ids.keys(), labs)))
    # id_list = list(ids.keys())
    # a = id_list[list(ids.values()).index(class_id)]


def get_max_grade_for_lab(lid, year, semester, db_name='./grades.sqlite3'):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        result = cur.execute('SELECT e.pipeline_id as pipid, IFNULL(MAX(k.final_grade), 0) as grade '
                             'FROM class e '
                             'LEFT OUTER JOIN '
                             '  (SELECT d.pipeline_id, c.grade*f.percent/100 AS final_grade '
                             '   FROM grades c '
                             '     JOIN class d ON d.id = c.class_id '
                             '     JOIN penalties f ON f.id = c.attempt '
                             '   WHERE c.lab = ? ) k '
                             'ON e.pipeline_id = k.pipeline_id '
                             'WHERE year=? AND semester=? '
                             'GROUP BY e.pipeline_id '
                             'ORDER BY e.pipeline_id ', (lid, int(year), int(semester)))
        return result.fetchall()


def get_grades_by_lab_and_att(lid, att, db_name='./grades.sqlite3'):
    with lite.connect(db_name, detect_types=lite.PARSE_COLNAMES) as con:
        cur = con.cursor()
        result = cur.execute('select a.due_date_{0} as due_date, a.imported_{0} as import_date, '
                             'b.type, b.num, b.max_grade, '
                             'c.id as grade_id, c.submitted, c.graded, c.grade, c.pass_fail, c.grader_comment, c.extra_comment, c.grader, c.lab_path, '
                             'd.pipeline_id, e.first_name, e.second_name, f.percent, c.grade*f.percent/100 as final_grade '
                             'from lab_schedule a '
                             'join lab_names b on a.lab_id=b.id '
                             'join grades c on c.lab=a.id '
                             'join class d on d.id=c.class_id '
                             'join students e on e.pipeline_id=d.pipeline_id '
                             'join penalties f on f.id=c.attempt '
                             'where c.attempt={0} AND a.id=? ORDER BY d.pipeline_id'.format(int(att)), (lid,))
        info_tup = result.fetchall()
        info_desc = result.description
    return info_tup, info_desc


def get_lab_filename(lab_id, db_name='./grades.sqlite3'):
    with lite.connect(db_name) as con:
        cur = con.cursor()

        result = cur.execute('SELECT mandatory_files FROM lab_names WHERE id=? ', (str(lab_id),))
        return result.fetchall()[0]
    return None


def get_lab_max_value(lab_id, db_name='./grades.sqlite3'):
    with lite.connect(db_name) as con:
        cur = con.cursor()

        result = cur.execute('SELECT max_grade FROM lab_names WHERE id=? ', (str(lab_id),))
        return int(result.fetchone()[0])
    return None


def get_full_path(paths, local):
    import os
    return os.path.expanduser(paths[1]) + str(local[1]) + "_" + str(local[2])


def sync_files(self=None):
    import subprocess
    import os

    paths, local = settings_db_read_settings()
    full_path = get_full_path(paths, local) + "/server_sync/"
    lab_ids, lab_types, lab_nums = get_lab_names()
    lab_names = []
    for i in range(len(lab_types)):
        lab_names.append(lab_types[i] + '_Lab_' + str(lab_nums[i]))

    if not os.path.isdir(full_path):
        os.makedirs(full_path)
        for lab_name in lab_names:
            os.makedirs(full_path + lab_name)

    proc_arr = []
    for lab_name in lab_names:
        command = local[4] + ' ' + os.path.expanduser(paths[2] + lab_name) + '/*.zip' + ' ' + full_path + lab_name + '/'
        try:
            proc_arr.append(subprocess.Popen(os.path.expandvars(command), stdout=subprocess.PIPE, shell=True))
            proc_arr[-1].communicate()
        except Exception as e:
            print('Error in rsync: ', e)
        # output, error = process.communicate()
        # print(output)
        # print(error)

    for proc_elem in proc_arr:
        proc_elem.wait()


def export_pdf(self=None):
    import subprocess
    import os

    paths, local = settings_db_read_settings()
    lab_ids, lab_types, lab_nums = get_lab_names()
    lab_names = []
    for i in range(len(lab_types)):
        lab_names.append(lab_types[i] + '_Lab_' + str(lab_nums[i]))

    full_path = get_full_path(paths, local) + "/"
    for lab_name in lab_names:
        nums_to_sync = '_{'
        i = 1
        while os.path.isdir(full_path + lab_name + '_' + str(i) + '/Answers'):
            nums_to_sync += str(i) + ','
            i += 1
        if i == 1:
            continue
        nums_to_sync = nums_to_sync[0:-1] + '}'
        # for case when we have only one directory to sync
        if len(nums_to_sync) == 4:
            nums_to_sync = '_1'
        if len(nums_to_sync) > 1:
            command = local[4] + ' ' + full_path + lab_name + nums_to_sync + '/Answers/*.pdf ' + os.path.expanduser(paths[2]) + lab_name + '/'
            process = subprocess.Popen(os.path.expandvars(command), stdout=subprocess.PIPE, shell=True)
            process.communicate()
            # print(output)
            # print(error)


def save_grade_and_report(grade_id, grade, report, user_comment, grader, db_name='./grades.sqlite3'):
    if not os.path.isfile(db_name):
        raise Exception("DB not found")
    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.execute("UPDATE grades SET graded=strftime('%s','now'), pass_fail=?, grade=?, grader_comment=?, extra_comment=?, grader=? WHERE id=?", (True, grade, report, user_comment, grader, grade_id))
        con.commit()


def commit_gen_report(grade_id, db_name='./grades.sqlite3'):
    if not os.path.isfile(db_name):
        raise Exception("DB not found")
    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.execute("UPDATE grades SET report_generated=strftime('%s','now') WHERE id=?", (grade_id,))
        con.commit()



def get_lab_id(ltype, lab_num):
    lab_ids, lab_types, lab_nums = get_lab_names()
    for i, lid in enumerate(lab_ids):
        if lab_types[i] == ltype and lab_num == lab_nums[i]:
            return lid
    return None


def register_lab_in_semester(ltype, lab_num, year, semester, due_dates, db_name='./grades.sqlite3'):
    lid = get_lab_id(ltype, int(lab_num))
    # TODO: add a check so you do not insert lab twice
    if lid is None:
        raise Exception('No such lab')
    if not os.path.isfile(db_name):
        raise Exception("DB not found")
    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.execute('INSERT OR REPLACE INTO lab_schedule (lab_id, year, semester, due_date_1, due_date_2, due_date_3, due_date_4) VALUES (?, ?, ?, ?, ?, ?, ?)', (lid, year, semester, due_dates[0], due_dates[1], due_dates[2], due_dates[3]))
        con.commit()

def get_labid_in_schedule(lid, year, semester, db_name='./grades.sqlite3'):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        result = cur.execute('SELECT id FROM lab_schedule WHERE lab_id=? AND year=? AND semester=?', (lid, year, semester))
        fetched_red = result.fetchone()
    return int(fetched_red[0]) if fetched_red is not None else None


def get_due_date_by_labid(lid_sem, att=None, db_name='./grades.sqlite3'):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        if att:
            result = cur.execute('SELECT due_date_{} FROM lab_schedule WHERE id=?'.format(int(att)), (lid_sem,))
        else:
            result = cur.execute('SELECT due_date_1, due_date_2, due_date_3, due_date_4 FROM lab_schedule WHERE id=?', (lid_sem,))
        return result.fetchone()
    return None


def get_import_dates_by_labid(lid_sem, att=None, db_name='./grades.sqlite3'):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        if att:
            result = cur.execute('SELECT imported_{} FROM lab_schedule WHERE id=?'.format(int(att)), (lid_sem,))
        else:
            result = cur.execute('SELECT imported_1, imported_2, imported_3, imported_4 FROM lab_schedule WHERE id=?', (lid_sem,))
        return result.fetchone()
    return None


# save_grade_and_report(self.grade_ids[self.cur_idx], self.final_grade, self.user_comment, self.grader)
def gen_report(lid_sem, att=None, db_name='./grades.sqlite3'):
    if not os.path.isfile(db_name):
        raise Exception("DB not found")
    with lite.connect(db_name) as con:
        cur = con.cursor()
        cur.execute("UPDATE lab_schedule SET imported_{}=strftime('%s','now') WHERE id=?".format(att), (lid_sem,))
        con.commit()


def get_pipids_in_class_by_year_semester(year, semester, db_name='./grades.sqlite3'):
    if not os.path.isfile(db_name):
        raise Exception("DB not found")
    with lite.connect(db_name) as con:
        cur = con.cursor()
        result = cur.execute('SELECT pipeline_id FROM class WHERE year=? AND semester=?', (year, semester))
        all_ids = result.fetchall()
    return [elem[0] for elem in all_ids]



if __name__ == '__main__':
    settings_db_create()
