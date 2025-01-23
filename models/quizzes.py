"""Quiz model class
"""
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
    times_taken = Column(Integer, nullable=False, default=0)
    likes_num = Column(Integer, nullable=False, default=0)
    duration = Column(Integer, nullable=False, default=5)
    image_path = Column(String(256), nullable=True, default=None)
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
    scores = relationship(
                'Score',
                cascade='all, delete, delete-orphan',
                back_populates='quiz'
            )
    fan_user: Mapped[List['User']] = relationship(secondary=quizzes_likes, back_populates='liked_quizzes')
