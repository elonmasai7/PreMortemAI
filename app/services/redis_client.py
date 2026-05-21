from app.config import Settings


def build_redis_client(settings: Settings):
    if not settings.redis_url:
        return None
    try:
        import redis
    except ImportError:  # pragma: no cover
        return None
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)
