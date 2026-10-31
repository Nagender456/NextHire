"""Small dependency-free metrics registry for local and managed deployments."""

from __future__ import annotations

from collections import Counter
from threading import Lock


class Metrics:
    def __init__(self) -> None:
        self._counts: Counter[str] = Counter()
        self._lock = Lock()

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counts[name] += value

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counts)

    def prometheus(self) -> str:
        lines = []
        for name, value in sorted(self.snapshot().items()):
            metric = name.replace("-", "_")
            lines.extend(
                (f"# TYPE nexthire_{metric} counter", f"nexthire_{metric} {value}")
            )
        return "\n".join(lines) + ("\n" if lines else "")


metrics = Metrics()
