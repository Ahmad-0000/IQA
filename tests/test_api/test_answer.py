"""Test quizze endpoints
"""
import unittest
from api.v1.app import app
from models import storage
from models.users import User
from models.quizzes import Quiz
from uuid import uuid4


unittest.TestLoader.sortTestMethodUsing = None


class TestAnswer(unittest.TestCase):
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
   
    def test_new_valid_answer(self):
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
        question_id = res.json.get("question").get("id")
        res = self.__class__.client.post(f"/api/v1/questions/{question_id}/answers", json={
                "body": "Answer",
                "is_true": True
            })
        self.assertEqual(res.status_code, 201)

    def test_new_answer_minimum_requirements(self):
        """Test minimum requirements for new answers
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
        answer_json = {"body": "Answer"}
        res = self.__class__.client.post(f"/api/v1/questions/{question_id}/answers", json=answer_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing answer status"})
        answer_json['is_true'] = True
        del answer_json['body']
        res = self.__class__.client.post(f"/api/v1/questions/{question_id}/answers", json=answer_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing body"})

    def test_answers_mimimum_requirements_lengths(self):
        """Test the minimum length of data required to make an answer
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
        answer_json = {"body": "", "is_true": None}
        res = self.__class__.client.post(f"/api/v1/questions/{question_id}/answers", json=answer_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing body"})
        answer_json["body"] = "Answer"
        res = self.__class__.client.post(f"/api/v1/questions/{question_id}/answers", json=answer_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing answer status"})
        answer_json["is_true"] = True
        res = self.__class__.client.post(f"/api/v1/questions/{question_id}/answers", json=answer_json)
        self.assertEqual(res.status_code, 201)
        

    def test_update_answer(self):
        """Test update answer
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
        answer = res.json.get("answers")[0]
        answer_json = {}
        res = self.client.put(f"/api/v1/answers/{answer['id']}", json=answer_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Provide attributes to update"})
        answer_json["body"] = ""
        res = self.client.put(f"/api/v1/answers/{answer['id']}", json=answer_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Provide attributes to update"})
        new_body = str(uuid4())
        answer_json["body"] = new_body
        res = self.client.put(f"/api/v1/answers/{answer['id']}", json=answer_json)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["body"], new_body)
        answer_json = {"is_true": ""}
        res = self.client.put(f"/api/v1/answers/{answer['id']}", json=answer_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Provide attributes to update"})
        answer_json = {"is_true": ""}
        res = self.client.put(f"/api/v1/answers/{answer['id']}", json=answer_json)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Provide attributes to update"})
        # Test the only true answer logic later 


    def test_delete_answer(self):
        """Test delete answer
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
        answer = res.json["answers"][0]
        res = self.client.delete(f"/api/v1/answers/{answer['id']}")
        self.assertEqual(res.status_code, 400)
        if answer["is_true"]:
            self.assertEqual(res.json, {"error": "Can't delete the true answer"})
        else:
            self.assertEqual(res.json, {"error": "Abide to data constraints"})
