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
from models.snapshots import Snapshot


class Storage():
    """Its objects handle db storage
    """
    __engine = None
    __session = None
    classes = [User, Quiz, Question, Answer, FeedBack, Score, Snapshot]

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

    def get_paged_quizzes(self, order_by, order_type, after):
        """Get paged members for api
        """
        if after == 'initial':
            if order_type == 'asc':
                return Storage.__session.query(Quiz).order_by(Quiz.__dict__[order_by].asc()).limit(20).all()
            else:
                return Storage.__session.query(Quiz).order_by(Quiz.__dict__[order_by].desc()).limit(20).all()
        if order_by == "added_at":
            if type(after) is not datetime:
                try:
                    after = datetime.fromisoformat(after)
                except (ValueError, TypeError):
                    return None # 400
        else:
            try:
                after = int(after)
            except ValueError:
                return None # 400
        if order_type == "asc":
            return Storage.__session.query(Quiz).filter(Quiz.__dict__[order_by] > after).limit(20).all()
        else:
            return Storage.__session.query(Quiz).filter(Quiz.__dict__[order_by] < after).limit(20).all()
        
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
                "FeedBack": ["user_id", "quiz_id"],
                "Snapshot": ['user_id', 'quiz_id',
                           'question_id', 'answer_id',
                           'score_id', 'is_true']
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

    def get_quizzes_with_cats(self, cats: list, order_attribute, order_type, after) -> list:
        """Get filtered quizzes for the main wrapper
        """
        result = []
        for cat in cats:
            if type(cat) is not str:
                cats.remove(cat)
        if not cats:
            return []
        for_cat = 20 // len(cats)
        prev = 0
        if after == 'initial':
            for cat in cats:
                if order_type == "asc":
                    sub_result = Storage.__session.query(Quiz)\
                                .order_by(Quiz.__dict__[order_attribute].asc())\
                                .filter(Quiz.category.has(name=cat))\
                                .limit(for_cat + prev)\
                                .all()
                else:
                    sub_result = Storage.__session.query(Quiz)\
                                .order_by(Quiz.__dict__[order_attribute].desc())\
                                .filter(Quiz.category.has(name=cat))\
                                .limit(for_cat + prev)\
                                .all()
                prev = for_cat - len(sub_result)
                result.extend(sub_result)
            return result
        if order_attribute == "added_at":
            if type(after) is not datetime:
                try:
                    after = datetime.fromisoformat(after)
                except (ValueError, TypeError):
                    return None
        else:
            try:
                after = int(after)
            except ValueError:
                return None
        for cat in cats:
            if order_type == "asc":
                sub_result = Storage.__session.query(Quiz)\
                            .filter(Quiz.__dict__[order_attribute] > after)\
                            .filter(Quiz.category.has(name=cat))\
                            .limit(for_cat + prev)\
                            .all()
            else:
                sub_result = Storage.__session.query(Quiz)\
                            .filter(Quiz.__dict__[order_attribute] < after)\
                            .filter(Quiz.category.has(name=cat))\
                            .limit(for_cat + prev)\
                            .all()
            prev = for_cat - len(sub_result)
            result.extend(sub_result)
        return result
