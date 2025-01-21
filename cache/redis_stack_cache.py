"""Redis Stack caching layer
"""
import redis
import json
from os import getenv
from datetime import datetime
from models import storage
from models.quizzes import Quiz
from redis.commands.search.field import NumericField
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import (IndexDefinition,
        IndexType
)


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
        index_name = "newest"
        schema = (
            NumericField(
                '$.general_details.added_at',
                as_name='date',
                sortable=True
            )
        )
        try:
            RedisStackCache.__client.ft(index_name).dropindex()
        except:
            pass
        RedisStackCache.__client.ft(index_name).create_index(
                schema,
                definition=IndexDefinition(
                    index_type=IndexType.JSON,
                    prefix=['newest:quiz:']
                )
        )
        index_name = "oldest"
        schema = (
            NumericField(
                '$.general_details.added_at',
                as_name='date',
                sortable=True
            )
        )
        try:
            RedisStackCache.__client.ft(index_name).dropindex()
        except:
            pass 
        RedisStackCache.__client.ft(index_name).create_index(
            schema,
            definition=IndexDefinition(
                index_type=IndexType.JSON,
                prefix=["oldest:quiz:"]
            )
        )
        index_name = "popular"
        schema = (
            NumericField(
                '$.general_details.times_taken',
                as_name='repeats',
                sortable=True
            )
        )
        try:
            RedisStackCache.__client.ft(index_name).dropindex()
        except:
            pass 
        RedisStackCache.__client.ft(index_name).create_index(
            schema,
            definition=IndexDefinition(
                index_type=IndexType.JSON,
                prefix=["popular:quiz:"]
            )
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
        RedisStackCache.__client.setex(
                                        f'{_type}_pool_size',
                                        RedisStackCache.__expiry_time * 60,
                                        added
        )
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
        RedisStackCache.__client.setex(
                                        'popular_pool_size',
                                        RedisStackCache.__expiry_time * 60,
                                        added
        )
        return added

    def update_quiz(self, quiz_id, attributes: dict):
        """Update quiz attributes to keep consistency with db
        """
        if RedisStackCache.__client.json().get(f'newest:quiz:{quiz_id}'):
            for k, v in attributes.items():
                RedisStackCache.__client.json().set(
                        f'newest:quiz:{quiz_id}',
                        f'$["general_details"].{k}',
                        v
                    )
        if RedisStackCache.__client.json().get(f'oldest:quiz:{quiz_id}'):
            for k, v in attributes.items():
                RedisStackCache.__client.json().set(
                        f'oldest:quiz:{quiz_id}',
                        f'$["general_details"].{k}',
                        v
                    )
        if RedisStackCache.__client.json().get(f'popular:quiz:{quiz_id}'):
            for k, v in attributes.items():
                RedisStackCache.__client.json().set(f'popular:quiz:{quiz_id}',
                        f'$["general_details"].{k}',
                        v
                    )

    def delete_quiz(self, quiz_id):
        """Delete a quiz to keep consistency with the db
        """
        result = 0
        total = 0
        exists = RedisStackCache.__client.exists(f'newest:quiz:{quiz_id}')
        if exists:
            total += 1
            last_quiz = self.get_paged_newest(
                                                    'initial',
                                                    100
                                                ).docs[-1].json
            last_quiz = json.loads(last_quiz)
            alternate = storage.get_paged(
                                            Quiz,
                                            "added_at",
                                            "desc",
                                            datetime.fromtimestamp(last_quiz['general_details']['added_at']),
                                            1
            )
            if alternate:
                alternate = alternate[0].to_a_cache_pool()
                timeout = RedisStackCache.__client.ttl(f'newest:quiz:{quiz_id}')
                RedisStackCache.__client.json().set(f'newest:quiz:{alternate["general_details"]["id"]}', "$", alternate)
                RedisStackCache.__client.expire(f'newest:quiz:{alternate["general_details"]["id"]}', timeout)
                RedisStackCache.__client.incrby('newest_pool_size')
            result += RedisStackCache.__client.json().delete(f'newest:quiz:{quiz_id}')
            RedisStackCache.__client.incrby('newest_pool_size', -1)
        exists = RedisStackCache.__client.exists(f'oldest:quiz:{quiz_id}')
        if exists:
            total += 1
            last_quiz = self.get_paged_oldest(
                                                    'initial',
                                                    100
                                                ).docs[-1].json
            last_quiz = json.loads(last_quiz)
            alternate = storage.get_paged(
                                            Quiz,
                                            "added_at",
                                            "asc",
                                            datetime.fromtimestamp(last_quiz['general_details']['added_at']),
                                            1
            )
            if alternate:
                alternate = alternate[0].to_a_cache_pool()
                timeout = RedisStackCache.__client.ttl(f'oldest:quiz:{quiz_id}')
                RedisStackCache.__client.json().set(f'oldest:quiz:{alternate["general_details"]["id"]}', "$", alternate)
                RedisStackCache.__client.expire(f'oldest:quiz:{alternate["general_details"]["id"]}', timeout)
                RedisStackCache.__client.incrby('oldest_pool_size')
            result += RedisStackCache.__client.json().delete(f'oldest:quiz:{quiz_id}')
            RedisStackCache.__client.incrby('oldest_pool_size', -1)
        exists = RedisStackCache.__client.exists(f'popular:quiz:{quiz_id}')
        if exists:
            total += 1
            last_quiz = self.get_paged_popular(
                                                    'initial',
                                                    100
                                                ).docs[-1].json
            last_quiz = json.loads(last_quiz)
            alternate = storage.get_paged(
                                            Quiz,
                                            "times_taken",
                                            "desc",
                                            last_quiz['general_details']['times_taken'],
                                            1
            )
            if alternate:
                alternate = alternate[0].to_a_cache_pool()
                timeout = RedisStackCache.__client.ttl(f'popular:quiz:{quiz_id}')
                RedisStackCache.__client.json().set(f'popular:quiz:{alternate["general_details"]["id"]}', "$", alternate)
                RedisStackCache.__client.expire(f'popular:quiz:{alternate["general_details"]["id"]}', timeout)
                RedisStackCache.__client.incrby('popular_pool_size')
            result += RedisStackCache.__client.json().delete(f'popular:quiz:{quiz_id}')
            RedisStackCache.__client.incrby('popular_pool_size', -1)
        return (total, result)

    def get_paged_newest(self, after: str, limit: int):
        """Returns a "limit" number of quizzes from the
        newest index
        """
        if after == "initial":
            q = Query('*').sort_by('date', asc=False).paging(0, limit)
        else:
            after = int(datetime.fromisoformat(after).timestamp())
            q = Query(f'@date:[-inf {after}]').sort_by('date', asc=False).paging(1, limit)
        return RedisStackCache.__client.ft('newest').search(q)
    
    def get_paged_oldest(self, after: str, limit: int):
        """Returns a "limit" number of quizzes from the
        oldest indext
        """
        if after == "initial":
            q = Query('*').sort_by('date', asc=True).paging(0, limit)
        else:
            after = int(datetime.fromisoformat(after).timestamp())
            q = Query(f'@date:[{after} +inf]').sort_by('date', asc=True).paging(1, limit)
        return RedisStackCache.__client.ft('oldest').search(q)
    
    def get_paged_popular(self, after: int, limit: int):
        """Returns a "limit" number of quizzes from the
        popular index
        """
        if after == "initial":
            q = Query('*').sort_by('repeats', asc=False).paging(0, limit)
        else:
            q = Query(f'@repeats:[-inf {after}]').sort_by('repeats', asc=False).paging(1, limit)
        return RedisStackCache.__client.ft('popular').search(q)

    def get_pool_size(self, _type: str):
        """Get the number of quizzes in a pool
        """
        return RedisStackCache.__client.get(f'{_type}_pool_size')
