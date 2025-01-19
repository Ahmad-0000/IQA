"""Redis Stack caching layer
"""
import redis
import json
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

    def populate_recent_quizzes_pool(self, pool_size):
        """Populate the recent quizzes pool with the 1st 100
        newest quizzes from the database
        """
        added = 0
        # Get the quizzes
        quizzes = storage.get_paged(Quiz, "added_at", "desc", "initial", pool_size)
        # Put them in an appropriate JSON format
        prepared_quizzes = [quiz.to_a_cache_pool() for quiz in quizzes]
        # store the quizzes
        for prepared_quiz in prepared_quizzes:
            RedisStackCache.__client.json()\
                    .set(
                        f"newest:quiz:{prepared_quiz['general_details']['id']}",
                        "$",
                        json.dumps(prepared_quiz)
                    )
            result = RedisStackCache.__client\
                        .expire(
                                f"newest:quiz:{prepared_quiz['general_details']['id']}",
                                RedisStackCache.__expiry_time * 60
                            )
            if result:
                added += 1 # Count how many quizzes was set
        return added
