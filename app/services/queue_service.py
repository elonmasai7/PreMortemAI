from app.config import Settings


def get_queue(settings: Settings):
    if not settings.queue_enabled or not settings.redis_url:
        return None
    try:
        import redis
        from rq import Queue
    except ImportError:  # pragma: no cover
        return None
    connection = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    return Queue(name=settings.queue_name, connection=connection)


def enqueue_investigation_run(settings: Settings, investigation_id: int, tenant_id: int) -> str | None:
    queue = get_queue(settings)
    if not queue:
        return None
    job = queue.enqueue("app.workers.investigation_worker.process_investigation_job", investigation_id, tenant_id)
    return job.id
