"""User model class
"""
from models.base_model import BaseModel, Base
from sqlalchemy import Table, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from typing import List


quizzes_likes = Table(
                'quizzes_likes', Base.metadata,
                Column('user_id', String(36), ForeignKey('users.id'), primary_key=True),
                Column('quiz_id', String(36), ForeignKey('quizzes.id'), primary_key=True)
)


class User(BaseModel, Base):
    """Represents users table
    """
    __tablename__ = "users"
    first_name = Column(String(20), nullable=False)
    middle_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    dob = Column(Date, nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    image_path = Column(String(57), nullable=True, default=None)
    bio = Column(String(300), nullable=True)
    liked_quizzes = Column(Integer, nullable=True, default=0)
    quizzes_taken = Column(Integer, nullable=True, default=0)
    quizzes_made = Column(Integer, nullable=True, default=0)

    quizzes = relationship(
                    'Quiz', 
                    cascade='all, delete, delete-orphan',
                    back_populates='user'
    )
    feedbacks = relationship(
                    'FeedBack', 
                    cascade='all, delete, delete-orphan',
                    back_populates='user'
    )
    scores = relationship(
            'Score',
            cascade='all, delete, delete-orphan',
            back_populates='user'
    )
    liked_quizzes: Mapped[List['Quiz']] = relationship(
                                                secondary=quizzes_likes,
                                                back_populates='fans_users'
    )
    snapshots = relationship(
            'Snapshot',
            cascade='all, delete, delete-orphan',
            back_populates='user'
    )
