from flask import Flask, escape, request, jsonify
from ariadne import gql, make_executable_schema, QueryType, graphql_sync, MutationType
from ariadne.constants import PLAYGROUND_HTML
import time

students = []
classes = []

type_defs = gql("""
    type Query {
        hello: String! 
        student(id: Int): Student
        class(id: Int): Class
    }
    type Mutation {
        createStudent(name: String!): Student
        createClass(name: String!): Class
        addStudentToClass(classID: Int, studentID: Int): Class
    }
    type Student {
        id: Int
        name: String
    }

    type Class {
        id: Int
        name: String
        students: [Student]
    }
""")

query = QueryType()
mutation = MutationType()

@query.field("hello")
def resolve_hello(_, info):
    return "Hello Shweta!"

@query.field("student")
def resolve_student(_, info, id):
    for student in students:
        if student['id'] == id:
            return student

@mutation.field("createStudent")
def resolve_createStudent(_, info, name):
    id = int(time.time())
    student = {
        'id' : id,
        'name' : name
    }
    students.append(student)
    return student

@query.field("class")
def resolve_class(_, info, id):
    for req_class in classes:
        if req_class['id'] == id:
            return req_class

@mutation.field("createClass")
def resolve_createClass(_, info, name):
    id = int(time.time())
    new_class = {
        'id' : id,
        'name' : name,
        'students' : []
    }
    classes.append(new_class)
    return new_class

@mutation.field("addStudentToClass")
def resolve_addStudentToClass(_, info, classID, studentID):
    for student in students:
        if student['id'] == studentID:
            break
    
    for available_class in classes:
        if available_class['id'] == classID:
            student_list = available_class['students']
            student_list.append(student)

    return available_class

schema = make_executable_schema(type_defs, [query, mutation])

app = Flask(__name__)

@app.route("/graphql", methods=["GET"])
def graphql_playgroud():
    return PLAYGROUND_HTML, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():

    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(debug=True)
