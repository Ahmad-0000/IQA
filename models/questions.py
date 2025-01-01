"""Question model class
"""
from sqlalchemy import Column, Text, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class Questions(BaseModel, Base):
    """Represent questions table
    """
    __tablename__ = 'questions'
    body = Column(Text, nullable=False)
    image_path = Column(String(256), nullalbe=True, defualt=None)
