from flask import Flask, escape, request, jsonify, abort, url_for, send_from_directory
import time, json
import sqlite3
from sqlite3 import Error
from PIL import Image
import pytesseract
import io
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['JSON_SORT_KEYS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/tests', methods = ['POST'])
def create_test():
    test_req = request.get_json()
    subject = test_req['subject']
    answer_keys = test_req['answer_keys']
    submissions = []
    conn = create_connection()
    
    with conn:
        test = (subject,)
        test_id = create_test(conn, test)

        for question, answer in answer_keys.items():
            answer_key = (question, answer, test_id)
            create_answer_key(conn, answer_key)
    
    new_test = {
       'test_id' : test_id,
       'subject' : subject,
       'answer_keys' : answer_keys,
       'submissions' : submissions
    }

    return jsonify({'test':new_test}), 201

@app.route('/api/tests/<int:test_id>/scantrons', methods = ['POST'])
def upload_scantron(test_id):
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    filePath = url_for('uploaded_file', filename=filename)
    scantron_url = request.url_root + filePath
    
    conn = create_connection()

    test = select_test(conn, test_id)
    subject = test['subject']
    answer_keys = test['answer_keys']

    scantron_json = ""
    with open(basedir + filePath, 'r') as f:
        scantron_json = json.load(f)
        msg = validate_scantron(scantron_json)
        if msg != "":
            return msg

    name = scantron_json['name']
    scantron_answers = scantron_json['answers']
    
    result = {}
    score = 0
    for question, expected in answer_keys.items():
        actual = scantron_answers.get(question, None)
        if(expected == actual):
            score += 1
        entry = {
            "actual" : actual,
            "expected" : expected
        }
        result[question] = entry

    conn = create_connection()
    with conn:
        scantron = (scantron_url, name, subject, score, test_id)
        scantron_id = create_scantron(conn, scantron)

    for question, result_entry in result.items():
        conn = create_connection()
        with conn:
            scantron_result = (question, result_entry['actual'], result_entry['expected'], scantron_id)
            create_scantron_result(conn, scantron_result)

    submission = {
        "scantron_id" : scantron_id,
        "scantron_url" : scantron_url,
        "name" : name,
        "subject" : subject,
        "score" : score,
        "result" : result
    }

    return jsonify({'submission':submission}), 201 

def validate_scantron(scantron_json):
    name = scantron_json['name']
    if name == "":
        return "Invalid JSON, incorrect name"
    scantron_answers = scantron_json['answers']
    values = scantron_answers.values()
    for value in values:
        if not value.isalpha():
            return "Invalid JSON, answer should be an alphabet"
    return ""

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/api/tests/<int:test_id>', methods = ['GET'])
def check_all_submissions(test_id):
    conn = create_connection()
    test = select_test(conn, test_id)

    return jsonify({'test':test}), 200

@app.route('/')
def main():
    sql_create_test_table = """ CREATE TABLE IF NOT EXISTS test (
                                        id integer PRIMARY KEY,
                                        subject text NOT NULL
                                    ); """

    sql_create_answer_key_table = """CREATE TABLE IF NOT EXISTS answer_key (
                                    id integer PRIMARY KEY,
                                    question text NOT NULL,
                                    answer text NOT NULL,
                                    test_id integer NOT NULL,
                                    FOREIGN KEY (test_id) REFERENCES test (id)
                                );"""

    sql_create_scantron_table =  """CREATE TABLE IF NOT EXISTS scantron (
                                    id integer PRIMARY KEY,
                                    scantron_url text,
                                    name text NOT NULL,
                                    subject text NOT NULL,
                                    score integer NOT NULL,
                                    test_id integer NOT NULL,
                                    FOREIGN KEY (test_id) REFERENCES test (id)
                                );"""

    sql_create_result_table = """CREATE TABLE IF NOT EXISTS result (
                                    id integer PRIMARY KEY,
                                    question integer NOT NULL,
                                    actual text NOT NULL,
                                    expected text NOT NULL,
                                    scantron_id integer NOT NULL,
                                    FOREIGN KEY (scantron_id) REFERENCES scantron (id)
                                );"""

    conn = create_connection()
    if conn is not None:
        create_table(conn, sql_create_test_table)
        create_table(conn, sql_create_answer_key_table)
        create_table(conn, sql_create_scantron_table)
        create_table(conn, sql_create_result_table)

    return f'Scantron API started!'

def create_connection():
    database = r"pythonsqlite.db"
    conn = None
    try:
        conn = sqlite3.connect(database)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_test(conn, test):
    sql = ''' INSERT INTO test(subject)
              VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, test)
    return cur.lastrowid

def create_answer_key(conn, answer_key):
    sql = ''' INSERT INTO answer_key(question, answer, test_id)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, answer_key)
    return cur.lastrowid

def create_scantron(conn, scantron):
    sql = ''' INSERT INTO scantron(scantron_url, name, subject, score, test_id)
              VALUES(?, ?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, scantron)
    return cur.lastrowid

def create_scantron_result(conn, result):
    sql = ''' INSERT INTO result(question, actual, expected, scantron_id)
              VALUES(?, ?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, result)
    return cur.lastrowid

def select_test(conn, test_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM test WHERE id=?", (test_id,))
    row = cur.fetchone()
    answer_keys = select_answer_keys(conn, test_id)
    submissions = select_scantron(conn,test_id )

    test = {
        "test_id" : row[0],
        "subject" : row[1],
        "answer_keys" : answer_keys,
        "submissions" : submissions
    }
    return test

def select_answer_keys(conn, test_id):
    cur = conn.cursor()
    cur.execute("SELECT question, answer FROM answer_key WHERE test_id=?", (test_id,))

    rows = cur.fetchall()
    answer_keys = {}

    for row in rows:
        answer_keys[row[0]] = row[1]

    return answer_keys

def select_scantron(conn, test_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM scantron WHERE test_id=?", (test_id,))
    rows = cur.fetchall()
    submissions = []
    for row in rows:
        result = select_scantron_result(conn, row[0])

        submission = {
            "scantron_id" : row[0],
            "scantron_url" : row[1],
            "name" : row[2],
            "subject" : row[3],
            "score" : row[4],
            "result" : result
        }
        submissions.append(submission)

    return submissions

def select_scantron_result(conn, scantron_id):
    cur = conn.cursor()
    cur.execute("SELECT question, actual, expected FROM result WHERE scantron_id=?", (scantron_id,))
    rows = cur.fetchall()

    result = {}

    for row in rows:
        entry = {
            "actual" : row[1],
            "expected" : row[2]
        }
        result[row[0]] = entry

    return result

main()
    