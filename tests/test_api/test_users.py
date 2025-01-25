"""Test users endpoints
"""
import unittest
from api.v1.app import app
from models import storage
from models.users import User
from uuid import uuid4
from parameterized import parameterized
from unittest.mock import patch
from tests.test_api.fixtures import TEST_FIXTURE
from sqlalchemy.exc import DataError
from api.v1.auth.session_auth import SessionAuth


class TestUser(unittest.TestCase):
    """Main test class
    """
    @classmethod
    def setUpClass(cls):
        """Initialize the test class environment
        """
        app.config.update({"TESTING": True})
        cls.client = app.test_client()
        cls.session_id = None

    @classmethod
    def tearDownClass(cls):
        """Destroying class test environment
        """
        del cls.client

    def test_404(self):
        """Test error 404
        """
        error_404 = self.client.get("/none");
        self.assertEqual(error_404.status_code, 404)
        
    @parameterized.expand(TEST_FIXTURE['POST'])
    @patch.object(SessionAuth, 'create_session', return_value="session")
    @patch.object(User, 'save')
    @patch.object(User, 'to_dict')
    def test_new_user(self, f_name, m_name, l_name, dob, email, pawd, json_res, status, patched_to_dict, patched_save, patched_session):
        """Test "POST /api/v1/users"
        """
        patched_to_dict.return_value = json_res
        patched_save.side_effect = [True, True, True, DataError, True]
        res = self.client.post("/api/v1/users", json={
                "first_name": f_name,
                "middle_name": m_name,
                "last_name": l_name,
                "dob": dob,
                "email": email,
                "password": pawd
        });
        self.assertEqual(res.status_code, status)
        self.assertEqual(res.json, json_res)
    
    def test_users(self):
        """Test "GET /api/v1/users"
        """
        res = self.client.get("/api/v1/users")
        self.assertEqual(res.status_code, 200)
        self.assertIs(type(res.json), list)

    def test_user(self):
        """Test "GET /api/v1/users/<uuid_id>"
        """
        user = storage.get_all(User)[0]
        res = self.client.get(f"/api/v1/users/{user.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, user.to_dict())

    def test_account_update(self):
        """Test "PUT /api/v1/users/<user_id>"
        """
        old_res = self.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": f"{str(uuid4())}@fake.fake",
                "password": "fakepass"
            });
        session_id = old_res.headers['Set-Cookie'].split(";")[0].split("=")[1]
        old_first_name = old_res.json['first_name']
        old_update_date = old_res.json['updated_at']
        new_res = self.client.put(f"/api/v1/users", json={
                "first_name": "A new name"
                }, headers={"Cookie": f"login_session={session_id}"})
        self.assertEqual(new_res.status_code, 200)
        self.assertEqual(new_res.json['first_name'], 'A new name')
        self.assertGreater(new_res.json['updated_at'], old_update_date)

    def test_delete_account(self):
        """Test "DELETE /api/v1/users/<user_id>"
        """
        old_res = self.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": f"{str(uuid4())}@fake.fake",
                "password": "fakepass"
            });
        session_id = old_res.headers['Set-Cookie'].split(";")[0].split("=")[1]
        res = self.client.delete(
                f"/api/v1/users", headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 204)
        res = self.client.delete(f"/api/v1/users")
        self.assertEqual(res.status_code, 401)
