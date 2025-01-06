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
   
    def test_new_valid_question(self):
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
        quiz_id = res.json['id']
        res = self.__class__.client.post(f"/api/v1/quizzes/{quiz_id}/questions", json={
                    "body": "Some question",
                    "answers_collection": [
                        {"body": "Answer 1", "is_true": True},
                        {"body": "Answer 2", "is_true": False}
                    ]
                }
            )
        self.assertEqual(res.status_code, 201)

    def test_new_question_minimum_requirements(self):
        """Test minimum requirements for new questions
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
        quiz_id = res.json['id']
        question_json = {
                "answers_collection": []
            } 
        res = self.__class__.client.post(f"/api/v1/quizzes/{quiz_id}/questions", json=question_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing body"})
        question_json['body'] = "Body"
        del question_json["answers_collection"]
        res = self.__class__.client.post(f"/api/v1/quizzes/{quiz_id}/questions", json=question_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing answers collection"})

    def test_question_minimum_requirements_data_types(self):
        """Test questions minimum requirements data types
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
        quiz_id = res.json.get("id")
        question_json = {
                "body": {"body": "Body"},
                "answers_collection": {"answer - 1": "True"}
            }
        res = self.__class__.client.post(f"/api/v1/quizzes/{quiz_id}/questions", json=question_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Abide to data constraints"})
        question_json = {
                "body": "Body",
                "answers_collection": {"body": "Body"}
            }
        res = self.__class__.client.post(f"/api/v1/quizzes/{quiz_id}/questions", json=question_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Abide to data constraints"})

    def test_question_mimimum_requirements_numbers(self):
        """Test the minimum number of data required to make a question
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
        quiz_id = res.json.get('id')
        question_json = {
                "body": "",
                "answers_collection": []
            }
        res = self.__class__.client.post(f"/api/v1/quizzes/{quiz_id}/questions", json=question_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing body"})
        question_json["body"] = "Body"
        res = self.__class__.client.post(f"/api/v1/quizzes/{quiz_id}/questions", json=question_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing answers collection"})
        question_json["answers_collection"].append({"body": "Body", "is_true": True})
        res = self.__class__.client.post(f"/api/v1/quizzes/{quiz_id}/questions", json=question_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Abide to data constraints"})
        question_json["answers_collection"].append({"body": "Body", "is_true": True})
        res = self.__class__.client.post(f"/api/v1/quizzes/{quiz_id}/questions", json=question_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Abide to data constraints"})
        question_json['answers_collection'].append({"body": "Body", "is_true": False})
        res = self.__class__.client.post(f"/api/v1/quizzes/{quiz_id}/questions", json=question_json)
        self.assertEqual(res.status_code, 201)

    def test_update_question(self):
        """Test update question
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
        quiz_id = res.json['id']
        res = self.__class__.client.post(f"/api/v1/quizzes/{quiz_id}/questions", json={
                    "body": "Some question",
                    "answers_collection": [
                        {"body": "Answer 1", "is_true": True},
                        {"body": "Answer 2", "is_true": False}
                    ]
                }
            )
        question_id = res.json.get("question").get("id")
        question_json = {"None": "None"}
        res = self.__class__.client.put(f"/api/v1/questions/{question_id}", json=question_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing body"})
        question_json['body'] = ""
        res = self.__class__.client.put(f"/api/v1/questions/{question_id}", json=question_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing body"})
        new_body = str(uuid4())
        question_json['body'] = new_body
        res = self.__class__.client.put(f"/api/v1/questions/{question_id}", json=question_json)
        self.assertEqual(res.status_code, 200)

    def test_delete_question(self):
        """Test delete question
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
        quiz_id = res.json['id']
        res = self.__class__.client.post(f"/api/v1/quizzes/{quiz_id}/questions", json={
                    "body": "Some question",
                    "answers_collection": [
                        {"body": "Answer 1", "is_true": True},
                        {"body": "Answer 2", "is_true": False}
                    ]
                }
            )
        question_id = res.json.get("question").get("id")
        res = self.__class__.client.delete(f"/api/v1/questions/{question_id}")
        self.assertEqual(res.status_code, 204)
