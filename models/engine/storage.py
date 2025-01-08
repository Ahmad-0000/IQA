"""Declare a class to handle DB storage
"""
from os import getenv
from datetime import datetime
from sqlalchemy import  create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models.base_model import Base
from models.users import User
from models.quizzes import Quiz
from models.questions import Question
from models.answers import Answer
from models.feedbacks import FeedBack
from models.scores import Score
from models.categories import Category


class Storage():
    """Its objects handle db storage
    """
    __engine = None
    __session = None
    classes = [User, Quiz, Question, Answer, FeedBack, Category, Score]

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

    def get_all(self, cls):
        """Get all objects blonging to "cls"
        """
        if cls not in Storage.classes:
            return None
        return Storage.__session.query(cls).order_by(cls.added_at.desc()).all()

    def get_paged(self, cls, order_by, order_type, after):
        """Get paged members for api
        """
        if cls is not Quiz:
            return None
        if order_by not in ["added_at", "likes_num", "times_taken"]:
            return None
        if order_by == "added_at" and after:
            try:
                after = datetime.fromisoformat(after)
            except ValueError:
                return None
        elif after:
            try:
                after = int(after)
            except ValueError:
                return None
        if order_type not in ["desc", "asc"]:
            order_type = "desc"
        if after:
            if order_type == "asc":
                return Storage.__session.query(cls).filter(cls.__dict__[order_by] > after).limit(20)
            else:
                return Storage.__session.query(cls).filter(cls.__dict__[order_by] < after).limit(20)
        else:
            return Storage.__session.query(cls).order_by(cls.__dict__[order_by]).limit(20)
        
    def get(self, cls, id):
        """Return the object belonging to "cls" with id "id"
        """
        if cls not in Storage.classes:
            return None
        obj = Storage.__session.query(cls).filter_by(id=id).one_or_none()
        return obj

    def get_filtered(self, cls, filters: dict):
        """Getting filtered data
        """
        allowed_filters = {
                "Common": ["added_at", "updated_at"],
                "User": [
                            "first_name",
                            "middle_name",
                            "last_name",
                            "email"
                        ],
                "Quiz": [
                            "times_taken",
                            "likes_num",
                            "duration",
                            "difficulty",
                            "category_id",
                            "user_id"
                        ],
                "Question": ["quiz_id"],
                "Answer": ["is_true", "question_id"],
                "Category": ["name"],
                "FeedBack": ["user_id", "quiz_id"]
            }
        if cls not in Storage.classes[:-1]:
            return []
        q = Storage.__session.query(cls)
        for k, v in filters.items():
            if k not in allowed_filters["Common"] and k not in allowed_filters[cls.__name__]:
                pass
            else:
                q = q.filter_by(**{k: v})
        result = q.all()
        return result

    def get_quizzes_with_cats(self, cats: list, after, options) -> list:
        """Get filtered quizzes for the main wrapper
        """
        for cat in cats:
            if type(cat) is not str:
                return None
        result = []
        for_cat = 20 // len(cats)
        order_attribute = options.get("order_attribute")
        order_type = options.get("order_type")
        if not order_attribute or order_attribute not in ["added_at", "times_taken"]:
            order_attribute = "added_at"
        if order_attribute == "added_at":
            try:
                after = datetime.fromisoformat(after)
            except (ValueError, TypeError):
                return None
        elif order_attribute == "times_taken":
            if type(after) is not int:
                return None
        if not order_type or order_type not in ["asc", "desc"]:
            order_type = "desc"
        prev = 0
        for cat in cats:
            if order_type == "asc":
                sub_result = Storage.__session.query(Quiz)\
                            .filter(Quiz.__dict__[order_attribute] > after)\
                            .filter(Quiz.category_id == cat)\
                            .limit(for_cat + prev)
            else:
                sub_result = Storage.__session.query(Quiz)\
                            .filter(Quiz.__dict__[order_attribute] < after)\
                            .filter(Quiz.category_id == cat)\
                            .limit(for_cat + prev)
            prev = for_cat - len(sub_result.all())
            result.extend(sub_result.all())
        return result
