"""Answer model class
"""
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class Answer(BaseModel, Base):
    """Represent answers table
    """
    __tablename__ = 'answers'
    body = Column(String(100), nullable=False)
    is_true = Column(Boolean, nullable=False)
