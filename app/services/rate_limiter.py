import time


class RedisRateLimiter:
    def __init__(self, client, window_seconds: int = 60):
        self.client = client
        self.window_seconds = window_seconds

    def is_limited(self, key: str, limit: int) -> bool:
        now_window = int(time.time() // self.window_seconds)
        bucket = f"rl:{key}:{now_window}"
        count = self.client.incr(bucket)
        if count == 1:
            self.client.expire(bucket, self.window_seconds + 1)
        return count > limit
