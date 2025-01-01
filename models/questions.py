"""Question model class
"""
from sqlalchemy import Column, Text, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class Question(BaseModel, Base):
    """Represent questions table
    """
    __tablename__ = 'questions'
    body = Column(Text, nullable=False)
    image_path = Column(String(256), nullable=True, default=None)
    quiz_id = Column(String(36), ForeignKey('quizzes.id'))
    answers = relationship(
                'Answer',
                cascade='all, delete, delete-orphan',
                back_populates='question'
            )
    quiz = relationship(
                'Quiz',
                back_populates='questions'
            )
