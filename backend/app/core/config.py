from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    max_parallel_searches: int
    circuit_breaker_failures: int
    circuit_breaker_reset_seconds: float
    
    # API Rate Limits
    tavily_rpm: int
    gemini_rpm: int
    newsapi_rpm: int


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        max_parallel_searches=20,
        circuit_breaker_failures=5,
        circuit_breaker_reset_seconds=30.0,
        
        # API Rate Limits - Conservative defaults
        tavily_rpm=500, 
        gemini_rpm=2000,
        newsapi_rpm=300, 
    )
