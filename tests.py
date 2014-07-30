#!jsachs/bin/python
import os
import unittest

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
        rv = self.app.get('/')
        print rv

    def test_add_user(self):
        rv = self.add_user("jsachs", "12345", "jsachs@epic.com")
        print rv

    def add_user(self, username, password, data):
        return self.app.post('/user', data=dict(
            username=username,
            password=password),
            follow_redirects=True)

if __name__ == '__main__':
    unittest.main()
