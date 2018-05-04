#!/usr/bin/python

import sqlite3 as lite
import os
import os.path

SETTINGS_DB_NAME = 'settings.sqlite3'  # Default settings filename

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
                    USE_STYLE   BOOLEAN );")
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
            result = cur.execute("SELECT GRADER_NAME, YEAR, SEMESTER, USE_STYLE\
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
            cur.execute('INSERT OR REPLACE INTO LOCAL (GRADER_NAME, YEAR, SEMESTER, USE_STYLE)'
                        'VALUES (?, ?, ?, ?);', local)
            con.commit()
            cur.execute('VACUUM;')
            con.commit()


def grades_db_create(db_name, force=False):
    """
    Will create database that contains all information about grades
    :param db_name: path and name of the database
    :param force: flag to overwrite existing db
    :return: Unknown
    """
    if os.path.isfile(db_name) and force:
        with lite.connect(db_name) as con:
            cur = con.cursor()
            # TODO: force should remove 'IF NOT EXISTS' and add 'DROP TABLE' to ensure new table creation
            # WISH: add try blocks for each CREATE and spawn new info window in case of error
            cur.execute("""CREATE TABLE grades (
                            id               INTEGER PRIMARY KEY AUTOINCREMENT,
                            stud_id                  NOT NULL REFERENCES students (id) ON UPDATE CASCADE,
                            lab                      NOT NULL REFERENCES lab_names (id) ON UPDATE CASCADE,
                            attempt          INT     DEFAULT (0),
                            submitted        INTEGER,
                            graded           INTEGER,
                            grade            INTEGER NOT NULL DEFAULT (0),
                            pass_fail        BOOLEAN NOT NULL DEFAULT (FALSE),
                            grader_comment   TEXT,
                            extra_comment    TEXT,
                            report_generated BOOLEAN,
                            report_time      INTEGER  );""")

            cur.execute("""CREATE TABLE students (
                            id             TEXT    NOT NULL,
                            year           INT     NOT NULL,
                            semester       CHAR    NOT NULL REFERENCES semesters (semester) ON DELETE RESTRICT
                                                                                            ON UPDATE CASCADE,
                            first_name     TEXT    NOT NULL,
                            second_name    TEXT    NOT NULL,
                            comment        TEXT,
                            cheating_ratio INTEGER DEFAULT (0),
                            PRIMARY KEY (id, year, semester)    );""")

            cur.execute("""CREATE TABLE semesters (
                            semester CHAR (1) NOT NULL PRIMARY KEY,
                            name     VARCHAR  );""")

            cur.execute("""CREATE TABLE lab_names (
                            id             INT     NOT NULL PRIMARY KEY,
                            type           TEXT    NOT NULL,
                            num            INTEGER NOT NULL,
                            max_grade      INTEGER NOT NULL,
                            name           VARCHAR,
                            description    VARCHAR,
                            grader_comment VARCHAR  );""")
            con.commit()


def load_student_list_into_grades_db(db_name, year, semester, filename='students_list.txt'):
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
        lname, fname = zip(*(namer.split(',') for namer in names))
        names_tupple = list(zip(ids, fname, lname, [year]*len(ids), [semester]*len(ids), [0]*len(ids)))

    if os.path.isfile(db_name):
        with lite.connect(db_name) as con:
            cur = con.cursor()
            cur.executemany('INSERT OR REPLACE INTO STUDENTS \
                        (id, first_name, second_name, year, semester, cheating_ratio) VALUES (?, ?, ?, ?, ?, ?)',
                        names_tupple)
            con.commit()

if __name__ == '__main__':
    settings_db_create()
