"""Score model class
"""
from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class Score(BaseModel, Base):
    """Represent a score record
    """
    __tablename__ = 'scores'
    score = Column(Float, nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    quiz_id = Column(String(36), ForeignKey('quizzes.id'), nullable=False)

    user = relationship('User', back_populates='scores')
    snapshots = relationship('Snapshot', back_populates='score')
    quiz = relationship('Quiz')

    def to_dict(self):
        """Score  repr
        """
        return {
            'score': self.score,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'added_at': self.added
        }


