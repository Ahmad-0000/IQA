"""Test quizze endpoints
"""
from os import getenv
from datetime import datetime, timedelta
import unittest
from unittest.mock import patch
from api.v1.app import app
from models import storage
from models.users import User
from models.quizzes import Quiz
from models.engine.storage import Storage
from uuid import uuid4
from api.v1.auth.session_auth import SessionAuth
import bcrypt


session_cookie_name = getenv('SESSION_COOKIE_NAME')


class TestAuth(unittest.TestCase):
    """Main test class
    """
    @classmethod
    def setUpClass(cls):
        """Initialize the test class environment
        """
        app.config.update({"TESTING": True})
        cls.client = app.test_client()

    @patch.object(User, 'save', **{'return_value.id': 'some id'})
    @patch.object(Storage, 'get', return_value=True)
    def setUp(self, patched_get, patched_save):
        """Prepare the test method
        """
        self.email = f'{str(uuid4())}@fake.fake'
        self.res = self.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": self.email,
                "password": "fakepass"
        });

    def test_register(self):
        """Test "POST /users/<user_id>/quizzes"
        """
        self.assertEqual(self.res.status_code, 201)
        self.assertIn("Set-Cookie", self.res.headers)
        cookie = self.res.headers.get('Set-Cookie')
        self.assertTrue(cookie.startswith(session_cookie_name + '='))

    @patch.object(Storage, 'get_filtered')
    @patch('bcrypt.checkpw')
    @patch.object(SessionAuth, 'create_session')
    def test_login(self, patched_create_session, patched_bcrypt_checkpw, patched_get_filtered):
        """PUT /api/v1/users/<user_id>/quizzes/<quiz_id>
        """
        patched_get_filtered.return_value.__len__.return_value = 1
        patched_get_filtered.return_value.__getitem__.return_value.to_dict.return_value = {"key": "value"}
        patched_get_filtered.return_value.__getitem__.return_value.password = "fakepassword"
        patched_bcrypt_checkpw.return_value = True
        patched_create_session.return_value = "session_id"
        res = self.client.post("/api/v1/login", json={
                "email": self.email,
                "password": "fakepass"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("Set-Cookie", res.headers)
        cookie = res.headers.get('Set-Cookie')
        self.assertTrue(cookie.startswith(session_cookie_name + '=session_id'))

    @patch.object(SessionAuth, 'destroy_session', return_value=True)
    @patch.object(SessionAuth, 'current_user', return_value=True)
    def test_logout(self, patched_current_user, patched_destroy_session):
        """Test "DELETE /api/v1/quizzes/<quiz_id>"
        """
        res = self.client.delete("/api/v1/logout");
        self.assertEqual(res.status_code, 200)
        yesterday_this_time = (datetime.utcnow() - timedelta(1)).ctime()
        day = yesterday_this_time.split(' ')[0]
        month = yesterday_this_time.split(' ')[1]
        day_num = yesterday_this_time.split(' ')[2]
        time = yesterday_this_time.split(' ')[3]
        year = yesterday_this_time.split(' ')[4]
        yesterday_this_time = f"{day}, {day_num} {month} {year} {time} GMT"
        expiry_date = res.headers.get('Set-Cookie').split('Expires=')[1].split(';')[0]
        self.assertEqual(expiry_date, yesterday_this_time)
