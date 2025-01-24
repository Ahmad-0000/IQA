"""Test quizze endpoints
"""
import sys
import unittest
from api.v1.app import app
from models import storage
from models.users import User
from models.quizzes import Quiz
from uuid import uuid4
from pprint import pprint


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
        res = cls.client.get("/api/v1/quizzes");
        cls.quizzes = res.json
        for quiz in cls.quizzes:
            if quiz.get("user_id") != cls.user.json.get("id"):
                cls.quiz = quiz
                break
        else:
            sys.exit(1)

    def test_new_like(self):
        """Test "POST /quizzes/<quiz_id>/like
        """
        old_likes_num = self.quiz["likes_num"]
        res = self.client.post(f"/api/v1/quizzes/{self.quiz['id']}/like")
        new_likes_num = res.json['likes_num']
        self.assertEqual(res.status_code, 201)
        self.assertEqual(old_likes_num + 1, new_likes_num)

    def test_own_quiz_like(self):
        """
        """
        own_quiz_res = self.client.post(f"/api/v1/quizzes", json={
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
        own_quiz = own_quiz_res.json
        res = self.client.post(f"/api/v1/quizzes/{own_quiz['id']}/like")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "You can't make a like to your own quiz"})

    @unittest.skip
    def test_remove_like(self):
        """Test remove likes
        """
        old_likes_num = self.quiz["likes_num"]
        res = self.client.delete(f"/api/v1/quizzes/{self.quiz['id']}/remove_like")
        new_likes_num = res.json['likes_num']
        self.assertEqual(res.status_code, 200)
        self.assertEqual(old_likes_num - 1, new_likes_num)

    @unittest.skip
    def test_remove_unmade_like(self):
        """Test remove unmade like
        """
        for quiz in self.quizzes:
            if quiz['likes_num'] == 0 and quiz['user_id'] != self.user.json['id']:
                break
        else:
            sys.exit(1)
        res = self.client.delete(f"/api/v1/quizzes/{quiz['id']}/remove_like")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"error": "You didn't like this quiz"})
