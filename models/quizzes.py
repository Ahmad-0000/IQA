"""Quiz model class
"""
<<<<<<< HEAD
=======
from datetime import datetime
>>>>>>> storage
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from models.base_model import Base, BaseModel
from models.users import quizzes_likes
from typing import List


class Quiz(BaseModel, Base):
    """Represents quizzes table
    """
    __tablename__ = 'quizzes'
    title = Column(String(100), nullable=False)
    description = Column(String(512), nullable=False)
    repeats = Column(Integer, nullable=False, default=0)
    likes_num = Column(Integer, nullable=False, default=0)
    duration = Column(Integer, nullable=False, default=5)
    image_path = Column(String(57), nullable=True, default=None)
    difficulty = Column(Enum('Easy', 'Medium', 'Hard'), nullable=False)
    category = Column(String(20), nullable=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='quizzes')
    questions = relationship(
                'Question',
                cascade='all, delete, delete-orphan',
                back_populates='quiz'
            )
    feedbacks = relationship(
                'FeedBack',
                cascade='all, delete, delete-orphan',
                back_populates='quiz'
            )
    fans_users: Mapped[List['User']] = relationship(
                                            secondary=quizzes_likes,
                                            back_populates='liked_quizzes'
<<<<<<< HEAD
                                        )
=======
    )

    def to_a_cache_pool(self):
        """Prepare a quiz to be stored in a cache pool
        """
        prepared_quiz = {}
        prepared_quiz['general_details'] = self.to_dict()
        prepared_quiz['general_details']['questions_num'] = len(self.questions)
        prepared_quiz['general_details']['added_at'] = int(
                                datetime.fromisoformat(
                                    prepared_quiz['general_details']['added_at']
                                ).timestamp()
                            )
        prepared_quiz['to_ongoing_session'] = self.to_ongoing_session()
        return prepared_quiz

    def to_ongoing_session(self):
        """Prepare a quiz to be stored in an ongoing test session
        """
        question_ids = []
        correct_answers = []
        questions = []
        for question in self.questions:
            question_ids.append(question.id)
            questions.append(
                    {
                        "id": question.id,
                        "body": question.body,
                        "answers": []
                    }
            )
            for answer in question.answers:
                questions[-1]['answers'].append(
                        {
                            'id': answer.id,
                            'body': answer.body,
                        }
                )
                if answer.is_true:
                    correct_answers.append(answer.id)
        prepared_quiz = {
                            "references": 1,
                            "questions_num": len(self.questions),
                            "questions": questions,
                            "question_ids": question_ids,
                            "correct_answers": correct_answers
                        }
        return prepared_quiz
>>>>>>> storage
