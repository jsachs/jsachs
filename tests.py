#!jsachs/bin/python
import os
import unittest
import json

from app import app, db, User, basedir

class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING']
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
        rv = json.loads(self.app.get('/').data)
        assert rv == {u'message': u'Hello World'}

    def test_add_user(self):
        rv = self.add_user("jsachs", "12345", "jsachs@epic.com")
        assert "username" in rv.data

    def test_auth_user(self):
        self.add_user("jsachs", "12345", "jsachs@epic.com")
        token = self.auth_user("jsachs", "12345")
        print token

    def test_index_auth(self):
        pass

    def test_get_user(self):
        self.add_user("jsachs", "12345", "jsachs@epic.com")
        rv = self.app.get('/user').data
        print rv
        rv = json.loads(self.app.get('/user').data)
        print rv
        token = self.auth_user("jsachs", "12345")
        rv = json.loads(self.app.get('/user').data)
        print rv
    #
    # def test_update_user(self):
    #     pass
    #
    # def test_delete_user(self):
    #     pass
    #
    # def test_unauth_user(self):
    #     pass

    def add_user(self, username, password, user_data):
        return self.app.post('/user',
            data=json.dumps({"username": username,"password": password, "data": user_data}),
            content_type="application/json",
            follow_redirects=True)

    def auth_user(self, username, password):
        return self.app.post('/auth',
            data=json.dumps({"username": username,"password": password}),
            content_type="application/json",
            follow_redirects=True)

if __name__ == '__main__':
    unittest.main()
