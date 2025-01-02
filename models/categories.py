"""Category model class
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class Category(BaseModel, Base):
    """Represent "categories" table
    """
    __tablename__ = 'categories'
    name = Column(String(20), nullable=False)
    quizzes = relationship('Quiz', back_populates='category')
