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
        cls.user = cls.client.post("/api/v1/users", json={
                "first_name": "ahmad",
                "middle_name": "husain",
                "last_name": "basheer",
                "dob": "2005-03-05",
                "email": f"{str(uuid4())}@fake.fake",
                "password": "fakepass"
            });
        cls.quiz = cls.client.post(f"/api/v1/quizzes", json={
            "title": "Fake",
            "description": "Fake",
            "difficulty": "easy",
            "questions_collection": [
                    {
                        "body": "Fake",
                        "answers_collection": [
                                {
                                    "body": "fake",
                                    "status": True
                                },
                                {
                                    "body": "fake",
                                    "status": False
                                }
                            ]
                    }
                ] 
            }).json 

    @classmethod
    def tearDownClass(cls):
        """Destroying class test environment
        """
        del cls.client
   
    def test_new_valid_feedback(self):
        """Test "POST /quizzes/<quiz_id>/feedbacks
        """
        res = self.client.post(
                f"/api/v1/quizzes/{self.quiz['id']}/feedbacks",
                json={"body": "Feedback"}
            )
        self.assertEqual(res.status_code, 201)
        # session_id = res.headers['Set-Cookie'].split(";")[0].split("=")[1]

    def test_new_feedback_minimum_requirements(self):
        """Test minimum requirements for new feedbacks
        """
        res = self.client.post(
                f"/api/v1/quizzes/{self.quiz['id']}/feedbacks",
                json={"None": ""}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing body"})


    def test_feedbacks_mimimum_requirements_lengths(self):
        """Test the minimum length of data required to make an answer
        """
        res = self.client.post(
                f"/api/v1/quizzes/{self.quiz['id']}/feedbacks",
                json={"body": ""}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Missing body"})

    def test_update_feedback(self):
        """Test update feedback
        """
        res = self.client.post(
                f"/api/v1/quizzes/{self.quiz['id']}/feedbacks",
                json={"body": "A feedback"}
            )
        feedback = res.json
        res = self.client.put(f"/api/v1/feedbacks/{feedback['id']}", 
                json={"body": ""}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Provide a body"})
        res = self.client.put(f"/api/v1/feedbacks/{feedback['id']}", 
                json={"body": [1]}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Abide to data constraints"})
        res = self.client.put(f"/api/v1/feedbacks/{feedback['id']}", 
                json={"body": "A feedback"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "Provide a different body"})
        res = self.client.put(f"/api/v1/feedbacks/{feedback['id']}", 
                json={"body": "An updated feedback"}
            )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['body'], "An updated feedback")
        

    def test_delete_feedback(self):
        """Test delete feedback
        """
        res = self.client.post(
                f"/api/v1/quizzes/{self.quiz['id']}/feedbacks",
                json={"body": "A feedback"}
            )
        res = self.client.delete(f"/api/v1/feedbacks/{res.json['id']}")
        self.assertEqual(res.status_code, 204)
