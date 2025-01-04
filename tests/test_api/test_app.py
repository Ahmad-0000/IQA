"""Test IQA API
"""
import unittest
from api.v1.app import app
from models import storage
from models.users import User
from uuid import uuid4


unittest.TestLoader.sortTestMethodUsing = None


class TestAPI(unittest.TestCase):
    """Main test class
    """
    @classmethod
    def setUpClass(cls):
        """Initialize the test class environment
        """
        app.config.update({"TESTING": True})
        cls.client = app.test_client()

    @classmethod
    def tearDownClass(cls):
        """Destroying class test environment
        """
        del cls.client

    def test_404(self):
        """Test error 404
        """
        error_404 = self.__class__.client.get("/none");
        self.assertEqual(error_404.status_code, 404)
    
    def test_new_user(self):
        """Test "POST /api/v1/users"
        """
        res = self.__class__.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": f"{str(uuid4())}@fake.fake",
                "password": "fakepass"
            });
        self.assertEqual(res.status_code, 201)
        user_email = res.json['email']
        res = self.__class__.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": user_email,
                "password": "fakepass"
            });
        self.assertEqual(res.status_code, 409)
    
    def test_users(self):
        """Test "GET /api/v1/users"
        """
        res = self.__class__.client.get("/api/v1/users")
        self.assertEqual(res.status_code, 200)
        self.assertIs(type(res.json), list)

    def test_user(self):
        """Test "GET /api/v1/users/<uuid_id>"
        """
        user = storage.get_all(User)[0]
        res = self.__class__.client.get(f"/api/v1/users/{user.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, user.to_dict())

    def test_account_update(self):
        """Test "PUT /api/v1/users/<user_id>"
        """
        old_res = self.__class__.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": f"{str(uuid4())}@fake.fake",
                "password": "fakepass"
            })
        id = old_res.json['id']
        old_first_name = old_res.json['first_name']
        old_update_date = old_res.json['updated_at']
        new_res = self.__class__.client.put(f"/api/v1/users/{id}", json={
                "first_name": "A new name"
            })
        self.assertEqual(new_res.status_code, 200)
        self.assertEqual(new_res.json['first_name'], 'A new name')
        self.assertGreater(new_res.json['updated_at'], old_update_date)

    def test_delete_account(self):
        """Test "DELETE /api/v1/users/<user_id>"
        """
        res = self.__class__.client.get("/api/v1/users");
        id = res.json[0]['id']
        res = self.__class__.client.delete(f"/api/v1/users/{id}")
        self.assertEqual(res.status_code, 204)
        res = self.__class__.client.delete(f"/api/v1/users/{id}")
        self.assertEqual(res.status_code, 404)
