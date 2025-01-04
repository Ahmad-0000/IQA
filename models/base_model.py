"""Contain BaseModel class
"""
import bcrypt
from datetime import datetime, date, timedelta
from uuid import uuid4
from sqlalchemy import Column, String, DateTime
from sqlalchemy.exc import DataError
from sqlalchemy.ext.declarative import declarative_base
from models.exc import DOBError


# Create Base class that some other models will inherit from
Base = declarative_base()


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
            self.added_at = datetime.utcnow().isoformat()
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
                self.added_at = datetime.utcnow()
            if "password" in self.__dict__:
                self.password = bytes(self.password, "utf-8")
                self.password = bcrypt.hashpw(self.password, bcrypt.gensalt())
                self.password = self.password.decode('utf-8')
            if "image_path" in kwargs and kwargs['image_path']:
                self.image_path = f'/data/iqa/profile_images/{self.id}'
        
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
            elif k == "added_at" or k == "updated_at" or k == "dob":
                dict_repr[k] = str(self.__dict__[k])
            else:
                dict_repr[k] = self.__dict__[k]
        return dict_repr

    def save(self):
        """Save the current object in the session
        """
        from models import storage
        if self.__class__.__name__ == "User":
            if self.dob > (date.today() - timedelta(3650)):
                raise DOBError()
        storage.add(self)
        storage.save()

    def delete(self):
        """Remove the current object from the session
        """
        from models import storage
        storage.delete(self)
        storage.save()
