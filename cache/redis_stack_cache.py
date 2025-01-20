"""Redis Stack caching layer
"""
import redis
from os import getenv
from models import storage
from models.quizzes import Quiz


class RedisStackCache():
    """Handles cache logic
    """
    __expiry_time = 30 # In minutes
    __client = None

    def __init__(self):
        """Initialization
        """
        db = getenv("IQA_REDIS_DB")
        host = getenv("IQA_REDIS_HOST")
        port = getenv("IQA_REDIS_PORT")
        if not db:
            db = 0
        if not host:
            host = 'localhost'
        if not port:
            port = 6379
        RedisStackCache.__client = redis.Redis(
                host=host, port=port, db=db, decode_responses=True
                )

    def populate_quizzes_pool(self, _type, pool_size):
        """Populate the recent or oldest quizzes pool with the 1st 100
        newest or oldest quizzes from the database
        """
        added = 0
        if _type not in ["newest", "oldest"]:
            return 0
        if _type == "newest":
            order = "desc"
        else:
            order = "asc"
        # Get the quizzes
        quizzes = storage.get_paged(Quiz, "added_at", order, "initial", pool_size)
        # Put them in an appropriate JSON format
        prepared_quizzes = [quiz.to_a_cache_pool() for quiz in quizzes]
        # store the quizzes
        for prepared_quiz in prepared_quizzes:
            RedisStackCache.__client.json()\
                    .set(
                        f"{_type}:quiz:{prepared_quiz['general_details']['id']}",
                        "$",
                        prepared_quiz
                    )
            result = RedisStackCache.__client\
                    .expire(
                        f"{_type}:quiz:{prepared_quiz['general_details']['id']}",
                        RedisStackCache.__expiry_time * 60
                    )
            if result:
                added += 1 # Count how many quizzes was set
        return added

    def populate_popular_pool(self, pool_size):
        """Populate the popular quizzes pool
        """
        added = 0
        # Get the quizzes
        quizzes = storage.get_paged(Quiz, "times_taken", "desc", "initial", pool_size)
        # Put them in an appropriate JSON format
        prepared_quizzes = [quiz.to_a_cache_pool() for quiz in quizzes]
        # store the quizzes
        for prepared_quiz in prepared_quizzes:
            RedisStackCache.__client.json()\
                    .set(
                        f"popular:quiz:{prepared_quiz['general_details']['id']}",
                        "$",
                        prepared_quiz
                    )
            result = RedisStackCache.__client\
                    .expire(
                        f"popular:quiz:{prepared_quiz['general_details']['id']}",
                        RedisStackCache.__expiry_time * 60
                    )
            if result:
                added += 1 # Count how many quizzes was set
        return added
