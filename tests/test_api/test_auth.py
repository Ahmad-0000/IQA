"""Test quizze endpoints
"""
import unittest
from api.v1.app import app
from models import storage
from models.users import User
from models.quizzes import Quiz
from uuid import uuid4


unittest.TestLoader.sortTestMethodUsing = None


class TestAuth(unittest.TestCase):
    """Main test class
    """
    email = None
    session_id = None
    
    @classmethod
    def setUpClass(cls):
        """Initialize the test class environment
        """
        app.config.update({"TESTING": True})
        cls.client = app.test_client()
        cls.email = f'{str(uuid4())}@fake.fake'
        cls.session_id = None

    @classmethod
    def tearDownClass(cls):
        """Destroying class test environment
        """
        del cls.client
   
    def test_register(self):
        """Test "POST /users/<user_id>/quizzes"
        """
        res = self.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": self.email,
                "password": "fakepass"
            });
        self.assertEqual(res.status_code, 201)
        self.assertIn("Set-Cookie", res.headers)

    @unittest.skip
    def test_login(self):
        """PUT /api/v1/users/<user_id>/quizzes/<quiz_id>
        """
        res = self.client.post("/api/v1/login", json={
                "email": self.email,
                "password": "fakepass"
            })
        self.assertEqual(res.status_code, 200)
        self.assertIn("Set-Cookie", res.headers)

    @unittest.skip
    def test_logout(self):
        """Test "DELETE /api/v1/quizzes/<quiz_id>"
        """
        res = self.client.delete("/api/v1/logout");
        self.assertEqual(res.status_code, 200)
