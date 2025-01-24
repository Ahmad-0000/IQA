"""Snapshot class model
"""
from sqlalchemy import Column, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class Snapshot(BaseModel, Base):
    """Represents "snapshots" table
    """
    __tablename__ = "snapshots"
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    score_id = Column(String(36), ForeignKey('scores.id'), nullable=False)
    answer_id = Column(String(36), nullable=True)
    question_id = Column(String(36), ForeignKey('questions.id'), nullable=False)
    is_true = Column(Boolean, nullable=False)

    user = relationship('User', back_populates='snapshots')
    question = relationship('Question')
    score = relationship('Score', back_populates='snapshots')
