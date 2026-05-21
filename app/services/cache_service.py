import hashlib
import json


class RedisCache:
    def __init__(self, client, ttl_seconds: int = 60):
        self.client = client
        self.ttl_seconds = ttl_seconds

    def _key(self, prefix: str, value: str) -> str:
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return f"cache:{prefix}:{digest}"

    def get_json(self, prefix: str, value: str):
        cache_key = self._key(prefix, value)
        raw = self.client.get(cache_key)
        if not raw:
            return None
        return json.loads(raw)

    def set_json(self, prefix: str, value: str, payload) -> None:
        cache_key = self._key(prefix, value)
        self.client.setex(cache_key, self.ttl_seconds, json.dumps(payload))
