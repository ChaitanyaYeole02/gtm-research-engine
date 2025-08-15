import redis

from app.models import Evidence

class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
    
    def is_evidence_cached(self, domain: str, evidence: Evidence) -> bool:
        if self.client.sismember(f"urls:{domain}", evidence.url):
            return True

        if self.client.sismember(f"titles:{domain}", evidence.title):
            return True

        if self.client.sismember(f"snippets:{domain}", evidence.snippet):
            return True

        return False
    
    def add_evidence_to_cache(self, domain: str, evidence: Evidence) -> None:
        self.client.sadd(f"urls:{domain}", evidence.url)
        self.client.sadd(f"titles:{domain}", evidence.title)
        self.client.sadd(f"snippets:{domain}", evidence.snippet)
    
    def clear_cache(self, domain: str) -> None:
        self.client.delete(f"urls:{domain}")
        self.client.delete(f"titles:{domain}")
        self.client.delete(f"snippets:{domain}")

redis_client = RedisCache()
