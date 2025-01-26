"""Stores login sessions
"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String ForeignKey
from sqlalchemy.orm import relationship


class Session(BaseModel, Base):
    """session model
    """
    __tablename__ = "login_sessions"
    user_id = Column(String(36), Foreign Key('users.id'), mullable=False)

    user = relationship("User", back_populates="login_sessions")