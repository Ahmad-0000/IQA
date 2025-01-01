"""Declare a class to handle DB storage
"""
from os import getenv
from sqlalchemy import  create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models.base_model import Base
from models.users import User


class Storage():
    """Its objects handle db storage
    """
    __engine = None
    __session = None
    classes = [User]

    def __init__(self):
        """Initialize storage object
        """
        user = getenv("IQA_DB_USER")
        pawd = getenv("IQA_DB_PAWD")
        host = getenv("IQA_DB_HOST")
        port = getenv("IQA_DB_PORT")
        db = getenv("IQA_DB_NAME")
        connection_url = 'mysql+mysqldb://{}:{}@{}:{}/{}'.format(user, pawd, host, port, db)
        Storage.__engine = create_engine(connection_url, pool_pre_ping=True)

    def reload(self):
        """Reload data from the database
        """
        Base.metadata.create_all(Storage.__engine)
        Session = scoped_session(sessionmaker(bind=Storage.__engine, expire_on_commit=False))
        Storage.__session = Session()

    def close(self):
        """Remove the current session
        """
        Storage.__session.close()

    def add(self, obj):
        """Add obj to the current session
        """
        Storage.__session.add(obj)

    def delete(self, obj):
        """Delete obj from the current session
        """
        Storage.__session.delete(obj)

    def save(self):
        """Save changes to the database
        """
        Storage.__session.commit()
    
    def get(self, cls, id):
        """Return the object belonging to "cls" with id "id"
        """
        if cls not in Storage.classes:
            return None
        obj = Storage.__session.query(cls).filter_by(id=id).one_or_none()
        return obj
