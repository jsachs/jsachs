#!jsachs/bin/python
from flask import Flask, request, jsonify, redirect, url_for, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
import os, datetime
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

app = Flask(__name__)
db = SQLAlchemy(app)

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = "This is the secret key!"

# session management
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# API endpoints
@app.route('/')
def index():
    
    return jsonify({'message': "Hello World"})

@app.route('/user', methods = ['GET'])
@auth.login_required
def get_user():
    user = User.query.filter_by(username = g.user.username).first()
    json_result = {'username': user.username, 'data': user.data}
    return jsonify({'user': json_result})

@app.route('/user', methods = ['POST'])
def add_user():
    username = request.get_json(force=True).get('username')
    password = request.get_json(force=True).get('password')
    data = request.get_json(force=True).get('data')
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
    user = User.query.filter_by(username = g.user.username).first()
    if not user:
        # user not found to update
        abort(404)
    user.data = request.get_json(force=True).get('data')
    db.session.commit()
    return jsonify({'username': user.username, 'data': user.data}), 204

@app.route('/user', methods = ['DELETE'])
@auth.login_required
def delete_user():
    user = User.query.filter_by(username = g.user.username).first()
    if not user:
        # user not found to delete
        abort(404)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': "Deleted "+user.username}), 204

@app.route('/auth', methods = ['POST'])
@auth.login_required
def auth_user():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

@app.route('/auth', methods = ['DELETE'])
@auth.login_required
def unauth_user():
    g.user.invalidate_auth_token()
    return jsonify({'message': "Token invalidated"})


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True)
    password_hash = db.Column(db.String(128))
    data = db.Column(db.String(120))

    def __init__(self, username, password, data=""):
        self.username = username
        self.data = data
        self.hash_password(password)

    # password management
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    # token management
    def generate_auth_token(self, expiration = 900):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    def invalidate_auth_token(self):
        del(s)
        return

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
