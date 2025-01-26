"""Contain BaseModel class
"""
import bcrypt
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.collections import InstrumentedList


# Create Base class that all other models will inherit from
class Base(DeclarativeBase):
    """Base model class
    """


class BaseModel():
    """Main model that others will inherit from
    """
    # 3 important attributes all the objects will have
    id = Column(String(36), primary_key=True)
    added_at = Column(DateTime, nullable=False, default=datetime.utcnow())
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow())
    
    def __init__(self, *args, **kwargs):
        """Intialize an object
        """
        if not kwargs:
            self.id = str(uuid4())
            self.added_at = datetime.utcnow()
            self.updated_at = self.added_at
        else:
            for k in kwargs:
                self.__dict__[k] = kwargs[k]
            if 'id' not in kwargs:
                self.id = str(uuid4())
            if 'added_at' not in kwargs:
                self.added_at = datetime.utcnow()
                self.updated_at = self.added_at
            if 'updated_at' not in kwargs:
                self.updated_at = self.added_at
            if "password" in self.__dict__:
                self.password = bytes(self.password, "utf-8")
                self.password = bcrypt.hashpw(self.password, bcrypt.gensalt())
                self.password = self.password.decode('utf-8')
            if "image_path" in kwargs and kwargs['image_path']:
                self.image_path = '/data/iqa/images/{}/{}'\
                                  .format(self.__class__.__name__.lower(),
                                          self.id)
 
    def __str__(self):
        """Customize __str__ output
        """
        return '[{}] ({}) {}'.format(self.__class__.__name__, self.id, self.to_dict())

    def to_dict(self):
        """Return dictionary representation of an object
        """
        dict_repr = {}
        for k in self.__dict__:
            if k == '_sa_instance_state' or k == 'password':
                pass
            elif type(self.__dict__[k]) is InstrumentedList:
                pass
            elif k == "added_at" or k == "updated_at" or k == "dob":
                dict_repr[k] = self.__dict__[k].isoformat()
            else:
                dict_repr[k] = self.__dict__[k]
        if self.__class__.__name__ == "Quiz":
            dict_repr['questions number'] = len(self.questions)
        return dict_repr

    def save(self):
        """Save the current object in the db session
        """
        from models import storage
        storage.add(self)
        storage.save()

    def delete(self):
        """Remove the current object from the db
        """
        from models import storage
        storage.delete(self)
        storage.save()

    def update(self, **kwargs):
        """Update object attributes
        """
        from models import storage
        for k, v in kwargs.items():
            if k == "password" and self.__class__.__name___ == "User":
                password = bytes(v, "utf-8")
                password = bcrypt.hashpw(v, bcrypt.gensalt())
                password = password.decode('utf-8')
                setattr(self, k, password)
            else:
                setattr(self, k, v)
        self.updated_at = datetime.utcnow()
        storage.save()
