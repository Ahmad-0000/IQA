"""User model class
"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Date


class User(BaseModel, Base):
    """Represents users table
    """
    __tablename__ = "users"
    first_name = Column(String(20), nullable=False)
    middle_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    dob = Column(Date, nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)
    image_path = Column(String(256), nullable=True)
    bio = Column(String(300), nullable=True)