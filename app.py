#!jsachs/bin/python
from flask import Flask, request, jsonify, redirect, url_for, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
import os, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

app = Flask(__name__)
db = SQLAlchemy(app)

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI


# session management
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.check_password(password):
            return False
    g.user = user
    return True


# API endpoints
@app.route('/')
def index():
    # no authentication
    return jsonify({'message': "Hello World"})

@app.route('/user', methods = ['GET'])
@auth.login_required
def get_user():
    user = User.query.filter_by(username = g.user.username).first()
    json_result = {'username': user.username, 'data': user.data}
    return jsonify({'user': json_result})

@app.route('/user', methods = ['POST'])
def add_user():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        data = request.json.get('data')
        if not username or not password:
            # missing signup information
            abort(400)
        if User.query.filter_by(username = username).first():
            # username already exists
            abort(400)
        user = User(username, password, data)
        db.session.add(user)
        db.session.commit()
        return jsonify({'username': user.username, 'data': user.data}), 201

@app.route('/user', methods = ['PUT'])
@auth.login_required
def update_user():
    pass

@app.route('/user', methods = ['DELETE'])
@auth.login_required
def delete_user():
    user = User.query.filter_by(username = g.user.username).first()
    if not user:
        # user not found to delete
        abort(404)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': "Deleted "+user.username})

@app.route('/auth', methods = ['POST'])
@auth.login_required
def auth_user():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

@app.route('/auth', methods = ['DELETE'])
@auth.login_required
def unauth_user():
    # this one will be hard
    return jsonify({'message': "Token invalidated"})


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True)
    password_hash = db.Column(db.String(128))
    data = db.Column(db.String(120), unique = True)

    def __init__(self, username, password, data=""):
        self.username = username
        self.data = data
        self.set_password(password)

    # salted password management
    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    # token management
    def generate_auth_token(self, expiration = 900):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user


if __name__ == '__main__':
    db.create_all()
    app.run(debug = True)
