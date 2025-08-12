from collections import defaultdict
from typing import Dict
import time

class Metrics:
    def __init__(self) -> None:
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timings_ms: Dict[str, list[float]] = defaultdict(list)

    def inc(self, key: str, value: int = 1) -> None:
        self.counters[key] += value

    def set_gauge(self, key: str, value: float) -> None:
        self.gauges[key] = value

    def observe_time_ms(self, key: str, ms: float) -> None:
        self.timings_ms[key].append(ms)

    def snapshot(self) -> Dict:
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "timings_ms": {k: v[:] for k, v in self.timings_ms.items()},
        }

metrics = Metrics()

def time_block(metric_key: str):
    start = time.time()
    class _Ctx:
        def __enter__(self):
            return None
        def __exit__(self, exc_type, exc, tb):
            end = time.time()
            metrics.observe_time_ms(metric_key, (end - start) * 1000.0)
    return _Ctx()