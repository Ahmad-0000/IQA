"""Quiz model class
"""
import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from models.base_model import Base, BaseModel
from models.users import quizzes_likes
from typing import List


class QuizDifficulty(enum.Enum):
    """Represents quiz difficulty levels
    """
    easy = 'Easy'
    medium = 'Medium'
    hard = 'Hard'


class Quiz(BaseModel, Base):
    """Represents quizzes table
    """
    __tablename__ = 'quizzes'
    title = Column(String(100), nullable=False)
    description = Column(String(512), nullable=False)
    times_taken = Column(Integer, nullable=False, default=0)
    likes_num = Column(Integer, nullable=False, default=0)
    duration = Column(Integer, nullable=False, default=5)
    image_path = Column(String(256), nullable=True, default=None)
    difficulty = Column(Enum(QuizDifficulty), nullable=False)
    category_id = Column(String(36), ForeignKey('categories.id'), nullable=True)
    user_id = Column(String(36), ForeignKey('users.id'))
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
    scores = relationship(
                'Score',
                cascade='all, delete, delete-orphan',
                back_populates='quiz'
            )
    fan_user: Mapped[List['User']] = relationship(secondary=quizzes_likes, back_populates='liked_quizzes')
