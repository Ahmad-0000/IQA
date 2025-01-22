"""Redis Stack caching layer
"""
import redis
import json
from os import getenv
from datetime import datetime, timedelta
from models import storage
from models.quizzes import Quiz
from models.scores import Score
from models.snapshots import Snapshot
from redis.commands.search.field import NumericField
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import (IndexDefinition,
        IndexType
)


def register_snapshots(user_id, quiz_id, score_id, snapshots) -> list:
    """A function to create snapshots for a specific quiz sesssion
    """
    snapshot_ids = []
    for question_id, info in snapshots:
        snapshot = Snapshot(
                                user_id=user_id,
                                quiz_id=quiz_id,
                                score_id=score_id,
                                question_id=question_id,
                                answer_id=(info[0] if len(info[0]) == 36 else None),
                                is_true=info[1]
        )
        snapshot.save()
        snapshot_ids.append(snapshot.id)
    return snapshot_ids

class RedisStackCache():
    """Handles cache logic
    """
    __expiry_time = 30 # In minutes
    __client = None
    _pool_size = 100

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

    def populate_quizzes_pool(self, _type):
        """Populate the recent or oldest quizzes pool with
        some newest or oldest quizzes from the database
        """
        added = 0
        if _type not in ["newest", "oldest"]:
            return 0
        if _type == "newest":
            order = "desc"
        else:
            order = "asc"
        if RedisStackCache.__client.get(f'{_type}_pool_size') is not None:
            return RedisStackCache._pool_size
        # Get the quizzes
        quizzes = storage.get_paged(Quiz, "added_at", order, "initial", RedisStackCache._pool_size)
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

    def populate_popular_pool(self):
        """Populate the popular quizzes pool
        """
        added = 0
        if RedisStackCache.__client.get(f'popular_pool_size') is not None:
            return RedisStackCache._pool_size
        # Get the quizzes
        quizzes = storage.get_paged(Quiz, "times_taken", "desc", "initial", RedisStackCache._pool_size)
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
        return True

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
                RedisStackCache.__client.incr('newest_pool_size')
            result += RedisStackCache.__client.json().delete(f'newest:quiz:{quiz_id}')
            RedisStackCache.__client.decr('newest_pool_size')
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
                RedisStackCache.__client.incr('oldest_pool_size')
            result += RedisStackCache.__client.json().delete(f'oldest:quiz:{quiz_id}')
            RedisStackCache.__client.decr('oldest_pool_size')
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
                RedisStackCache.__client.incr('popular_pool_size')
            result += RedisStackCache.__client.json().delete(f'popular:quiz:{quiz_id}')
            RedisStackCache.__client.decr('popular_pool_size')
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

    def start_a_quiz(self, quiz_id: str, user_id: str, session_id: str):
        """Starti a quiz session for multiple users
        """
        from_cache = True
        quiz = RedisStackCache.__client.json().get(f'newest:quiz:{quiz_id}')
        if not quiz:
            quiz = RedisStackCache.__client.json().get(f'oldest:quiz:{quiz_id}')
        if not quiz:
            quiz = RedisStackCache.__client.json().get(f'popular:quiz:{quiz_id}')
        if not quiz:
            from_cache = False
            quiz = storage.get(Quiz, quiz_id)
        if not quiz:
            return 404
        if type(quiz) is dict:
            deadline =  int(
                            (
                                datetime.utcnow() +
                                timedelta(minutes=quiz['general_details']['duration'])
                            ).timestamp()
                        )
        else:
            deadline =  int(
                            (
                                datetime.utcnow() +
                                timedelta(minutes=quiz.duration)
                            ).timestamp()
                        )
        if not RedisStackCache.__client.exists(f'ongoing:{quiz_id}'):
            if from_cache:
                RedisStackCache.__client.json().set(f'ongoing:{quiz_id}', "$", quiz['to_ongoing_session'])
            else:
                RedisStackCache.__client.json().set(f'ongoing:{quiz_id}', "$", quiz.to_ongoing_session())
        RedisStackCache.__client.sadd(f'ongoing_quiz_tracker:{quiz_id}', f'{session_id}:{quiz_id}')
        session = {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "deadline": deadline,
            "score": 0,
            "snapshots": {}
        }
        session_cookie = session_id + ':' + quiz_id 
        RedisStackCache.__client.json().set(session_cookie, "$", session)
        return session_cookie

    def register_a_snapshot(self, session_cookie: str, question_id: str, answer_id: str):
        """Register a snapshot, which is a data about the answer
        a user choose for a particular question
        """
        session = RedisStackCache.__client.json().get(session_cookie)
        if session is None:
            return 404
        user_id = session['user_id']
        quiz_id = session_cookie.split(':')[1]
        if int(datetime.utcnow().timestamp()) >= session['deadline']:
            score = session['score']
            score = Score(score=score, user_id=user_id, quiz_id=quiz_id)
            score.save()
            snapshots = session['snapshots']
            snapshot_ids = register_snapshots(score_id=score.id, user_id=user_id, quiz_id=quiz_id, snapshots=snapshots.items())
            RedisStackCache.__client.json().delete('session_cookie')
            RedisStackCache.__client.srem(f'ongoing_quiz_tracker:{quiz_id}', session_cookie)
            return (404, snapshot_ids)
        if RedisStackCache.__client.json().arrindex(f'ongoing:{quiz_id}', "$.question_ids", question_id)[0] == -1:
            return 400
        elif RedisStackCache.__client.json().get(session_cookie, f"$.snapshots.{question_id}" ):
            return 409
        if RedisStackCache.__client.json().arrindex(f'ongoing:{quiz_id}', "$.correct_answers", answer_id)[0] != -1:
            status = True
            questions_num = RedisStackCache.__client.json().get(f'ongoing:{quiz_id}', '$.questions_num')[0]
            RedisStackCache.__client.json().numincrby(session_cookie, "$.score", 100 / questions_num)
        else:
            status = False
        return RedisStackCache.__client.json().set(session_cookie, f"$.snapshots.{question_id}", [answer_id, status])

    def get_next_question(self, session_cookie: str, idx: int):
        """Get the next question from an ongoing quiz session
        """
        session = RedisStackCache.__client.json().get(session_cookie)
        if not session:
            return 404
        quiz_id = session['quiz_id']
        if int(datetime.utcnow().timestamp()) >= session['deadline'] or idx == -1:
            score = session['score']
            score = Score(score=score, user_id=user_id, quiz_id=quiz_id)
            score.save()
            snapshots = session['snapshots']
            snapshot_ids = register_snapshots(
                                                score_id=score.id,
                                                user_id=session['user_id'],
                                                quiz_id=['quiz_id'],
                                                snapshots=snapshots.items()
            )
            RedisStackCache.__client.json().delete('session_cookie')
            RedisStackCache.__client.srem(f'ongoing_quiz_tracker:{quiz_id}', session_cookie)
        if int(datetime.utcnow().timestamp()) >= session['deadline']:
            return (404, snapshot_ids)
        elif idx == -1:
            return (201, score.score)
        ongoing_quiz = RedisStackCache.__client.json().get(f'ongoing:{quiz_id}')
        try:
            return ongoing_quiz['questions'][idx]
        except IndexError:
            return (404, ongoing_quiz['questions_num'])
