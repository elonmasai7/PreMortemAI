#!/usr/bin/env python3

from app.config import get_settings


def main() -> None:
    try:
        import redis
        from rq import Worker
    except ImportError as exc:
        raise RuntimeError("Missing worker dependencies. Install redis and rq.") from exc

    settings = get_settings()
    if not settings.redis_url:
        raise RuntimeError("REDIS_URL is required to run the background worker.")
    connection = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    worker = Worker([settings.queue_name], connection=connection)
    worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()
