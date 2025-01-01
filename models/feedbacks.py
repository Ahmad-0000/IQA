"""Feedback model class
"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class FeedBack(BaseModel, Base):
    """Represents feedbacks table
    """
    __tablename__ = 'feedbacks'
    body = Column(String(512), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'))
    quiz_id = Column(String(36), ForeignKey('quizzes.id'))
    user = relationship('User', back_populates='feedbacks')
    quiz = relationship('Quiz', back_populates='feedbacks')
