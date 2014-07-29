#!jsachs/bin/python
from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from models import User
import os, datetime

app = Flask(__name__)
db = SQLAlchemy(app)

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI


@app.route('/')
def index():
    # no authentication
    return jsonify({'message': "Hello World"})

@app.route('/user/', methods = ['GET'])
def get_user():
    if request.method == 'GET':
        pass

@app.route('/user', methods = ['POST'])
def add_user():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        email = request.json.get('email')
        if not username or not password:
            # missing signup information
            abort(400)
        if User.query.filter_by(username = username).first():
            # username already exists
            abort(400)
        user = User(username, password, email)
        db.session.add(user)
        db.session.commit()
        return jsonify({'username': user.username, 'email': user.email}), 201

@app.route('/user', methods = ['PUT'])
def update_user():
    pass

@app.route('/user', methods = ['DELETE'])
def delete_user():
    pass

@app.route('/auth', methods = ['POST'])
def auth_user():
    pass

@app.route('/auth', methods = ['DELETE'])
def unauth_user():
    pass

#@app.route('/auth', methods = ['POST','DELETE'])

# @app.route(API_STRING + '/patients', methods = ['GET'])
# def get_patients():
#     if request.method == 'GET':
#         results = Patient.query.all()
#         json_results = []
#         for result in results:
#             d = {'id': result.id,
#                  'name': result.name,
#                  'date_of_birth': result.date_of_birth}
#             json_results.append(d)
#         return jsonify({'patients': json_results})
#
# @app.route(API_STRING + 'patients/<int:patient_id>', methods = ['GET'])
# def get_patient(patient_id):
#     if request.method == 'GET':
#         result = Patient.query.filter_by(id=patient_id).first()
#         json_result = {'id': result.id,
#                        'name': result.name,
#                        'date_of_birth': result.date_of_birth}
#         return jsonify({'patient': json_result})
#
# @app.route(API_STRING + 'patients', methods = ['POST'])
# def create_task():
#     if not request.json or not 'name' in request.json:
#         abort(400)
#     dob = request.json.get('date_of_birth', "")
#     date_of_birth = datetime.datetime.strptime(dob, '%m-%d-%Y')
#     patient = Patient(request.json['name'], date_of_birth)
#     #patient = {'name': request.json['name'],
#     #            'date_of_birth': request.json.get('date_of_birth', "")}
#     db.session.add(patient)
#     db.session.commit()
#     return jsonify({'name': patient.name,
#                     'date_of_birth': dob}), 201

if __name__ == '__main__':
    db.create_all()
    app.run(debug = True)
