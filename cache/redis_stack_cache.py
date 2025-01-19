"""Redis Stack caching layer
"""
import redis
from os import getenv


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
