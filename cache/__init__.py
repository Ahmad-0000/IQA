"""Initialize the package
"""
from cache.redis_stack_cache import RedisStackCache

RedisStackCache._pool_size = 100
cache_client = RedisStackCache()
cache_client.populate_quizzes_pool('newest')
cache_client.populate_quizzes_pool('oldest')
cache_client.populate_popular_pool()
