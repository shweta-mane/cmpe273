from flask import Flask, escape, request, jsonify, abort
import time, json

app = Flask(__name__)

students = []
classes = []

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

@app.route('/students', methods = ['POST'])
def create_student():
    student_req = request.get_json()
    name = student_req['name']
    id = int(time.time()*1000.0)

    student = {
        'id' : id,
        'name' : name
    }

    students.append(student)
    return jsonify({'student':student}), 201
    
@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    for student in students:
        if student['id'] == student_id:
            return jsonify({'student':student})
    abort(404)
    
@app.route('/classes', methods = ['POST'])
def create_class():
    class_req = request.get_json()
    name = class_req['name']
    id = int(time.time()*1000.0)

    new_class = {
        'id' : id,
        'name' : name,
        'students' : []
    }

    classes.append(new_class)
    return jsonify({'class':new_class}), 201
    
@app.route('/classes/<int:class_id>', methods=['GET'])
def get_class(class_id):
    for available_class in classes:
        if available_class['id'] == class_id:
            return jsonify({'class':available_class})
    abort(404)

@app.route('/classes/<int:class_id>', methods=['PATCH'])
def add_student_to_class(class_id):
    req = request.get_json()
    student_id = req['student_id']

    for student in students:
        if student['id'] == student_id:
            break
    
    for available_class in classes:
        if available_class['id'] == class_id:
            student_list = available_class['students']
            student_list.append(student)

    return jsonify({'class':available_class})
