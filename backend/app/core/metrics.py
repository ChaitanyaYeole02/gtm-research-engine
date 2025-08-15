import time

from dataclasses import dataclass


@dataclass
class RunMetrics:
    start_time: float
    total_queries_executed: int = 0
    failed_requests: int = 0

    def record_query(self, successes: int = 1) -> None:
        self.total_queries_executed += successes

    def record_failure(self, failures: int = 1) -> None:
        self.failed_requests += failures

    def to_dict(self) -> dict:
        elapsed = max(0.0001, time.perf_counter() - self.start_time)
        qps = self.total_queries_executed / elapsed
        return {
            "queries_per_second": round(qps, 2),
            "failed_requests": self.failed_requests,
        }
