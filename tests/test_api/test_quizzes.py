"""Test quizze endpoints
"""
import unittest
from api.v1.app import app
from models import storage
from models.users import User
from models.quizzes import Quiz
from uuid import uuid4


unittest.TestLoader.sortTestMethodUsing = None


class TestQuiz(unittest.TestCase):
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
   
    def test_new_valid_quiz(self):
        """Test "POST /users/<user_id>/quizzes"
        """
        res = self.__class__.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": f"{str(uuid4())}@fake.fake",
                "password": "fakepass"
            });
        session_id = res.headers['Set-Cookie'].split(";")[0].split("=")[1]
        res = self.__class__.client.post(f"/api/v1/quizzes", json={
            "title": "Fake",
            "description": "Fake",
            "difficulty": "easy",
            "questions_collection": [
                    {
                        "body": "Fake",
                        "answers_collection": [
                                {
                                    "body": "fake",
                                    "is_true": True
                                },
                                {
                                    "body": "fake",
                                    "is_true": False
                                }
                            ]
                    }
                ] 
            }, headers={"Cookie": f"login_session={session_id}"});
        self.assertEqual(res.status_code, 201)
        
    def test_new_quiz_minimum_requirements(self):
        """Test "POST /users/<user_id>/quizzes"
        """
        account = self.__class__.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": f"{str(uuid4())}@fake.fake",
                "password": "fakepass"
            });
        session_id = account.headers['Set-Cookie'].split(";")[0].split("=")[1]
        req_json = {
                "description": "Fake",
                "difficulty": "easy",
                "questions_collection": []
            }
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing data"})
        req_json['title'] = "fake"
        del req_json['description']
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing data"})
        req_json['description'] = 'fake'
        del req_json['difficulty']
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing data"})
        req_json['difficulty'] = 'easy'
        del req_json['questions_collection']
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing data"})

    def test_new_quiz_minimum_requirements_data_types(self):
        """Test "POST /users/<user_id>/quizzes"
        """
        account = self.__class__.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": f"{str(uuid4())}@fake.fake",
                "password": "fakepass"
            });
        session_id = account.headers['Set-Cookie'].split(";")[0].split("=")[1]
        req_json = {
                "title": "fake",
                "description": "fake",
                "difficulty": "easy",
                "questions_collection": {}
            }
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing data"})
        req_json['questions_collection'] = []
        req_json['questions_collection'].append({"answers_collection": {}})
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Abide to data constraints"})
        req_json['questions_collection'][-1]['body'] = "fake"
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Abide to data constraints"})

    def test_new_quiz_minimum_requirements_numbers(self):
        """Test "POST /users/<user_id>/quizzes"
        """
        account = self.__class__.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": f"{str(uuid4())}@fake.fake",
                "password": "fakepass"
            });
        session_id = account.headers['Set-Cookie'].split(";")[0].split("=")[1]
        req_json = json={
            "title": "Fake",
            "description": "Fake",
            "difficulty": "easy",
            "questions_collection": [] 
            }
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing data"})
        req_json['questions_collection'].append({"body": "fake", "answers_collection": []})
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Abide to data constraints"})
        req_json['questions_collection'][0]['answers_collection'].append({"body": "fake"})
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Abide to data constraints"})
        req_json['questions_collection'][0]['answers_collection'][0].update({"is_true": True})
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Abide to data constraints"})
        req_json['questions_collection'][0]['answers_collection'].append({"body": "fake", "is_true": True})
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Abide to data constraints"})
        req_json['questions_collection'][0]['answers_collection'].append({"body": "fake", "is_true": False})
        res = self.__class__.client.post(
                f"/api/v1/quizzes", json=req_json,
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 201)

    def test_quiz_update(self):
        """PUT /api/v1/users/<user_id>/quizzes/<quiz_id>
        """
        account = self.__class__.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": f"{str(uuid4())}@fake.fake",
                "password": "fakepass"
            });
        session_id = account.headers['Set-Cookie'].split(";")[0].split("=")[1]
        quiz = self.__class__.client.post(f"/api/v1/quizzes", json={
            "title": "Fake",
            "description": "Fake",
            "difficulty": "easy",
            "questions_collection": [
                    {
                        "body": "Fake",
                        "answers_collection": [
                                {
                                    "body": "fake",
                                    "is_true": True
                                },
                                {
                                    "body": "fake",
                                    "is_true": False
                                }
                            ]
                    }
                ] 
            })
        res = self.__class__.client.put(
                f"/api/v1/quizzes/{quiz.json['id']}", json={"none": "none"},
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Provide at least one attribute to update"})
        self.assertEqual(quiz.json['title'], 'Fake')
        res = self.__class__.client.put(
                f"/api/v1/quizzes/{quiz.json['id']}", json={"title": "new fake"},
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['title'], 'new fake')
        old_id = res.json["id"]
        res = self.__class__.client.put(
                f"/api/v1/quizzes/{quiz.json['id']}", json={"title": "new fake", "id": "some id"},
                headers={"Cookie": f"login_session={session_id}"}
            )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['title'], 'new fake')
        self.assertEqual(res.json['id'], old_id)

    def test_delete_quiz(self):
        """Test "DELETE /api/v1/quizzes/<quiz_id>"
        """
        account = self.__class__.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": f"{str(uuid4())}@fake.fake",
                "password": "fakepass"
            });
        session_id = account.headers['Set-Cookie'].split(";")[0].split("=")[1]
        quiz = self.__class__.client.post(f"/api/v1/quizzes", json={
            "title": "Fake",
            "description": "Fake",
            "difficulty": "easy",
            "questions_collection": [
                    {
                        "body": "Fake",
                        "answers_collection": [
                                {
                                    "body": "fake",
                                    "is_true": True
                                },
                                {
                                    "body": "fake",
                                    "is_true": False
                                }
                            ]
                    }
                ] 
            })
        res = self.__class__.client.delete(f"/api/v1/quizzes/{quiz.json['id']}", headers={"Cookie": f"login_session={session_id}"})
        self.assertEqual(res.status_code, 204)
