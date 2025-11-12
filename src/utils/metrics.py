"""Metrics collection for PIPE domain bots."""

import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class Metric:
    """Represents a single metric data point."""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Collects and aggregates metrics from bots.

    Provides counters, gauges, and timing metrics.
    """

    def __init__(self):
        """Initialize the metrics collector."""
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.timings: Dict[str, List[float]] = defaultdict(list)
        self.metrics_history: List[Metric] = []
        self.max_history = 10000

    def increment(self, name: str, value: float = 1.0, tags: Dict[str, str] = None) -> None:
        """
        Increment a counter metric.

        Args:
            name: Metric name
            value: Value to add
            tags: Optional tags for the metric
        """
        self.counters[name] += value
        self._record_metric(name, self.counters[name], tags)

    def gauge(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """
        Set a gauge metric.

        Args:
            name: Metric name
            value: Current value
            tags: Optional tags for the metric
        """
        self.gauges[name] = value
        self._record_metric(name, value, tags)

    def timing(self, name: str, duration: float, tags: Dict[str, str] = None) -> None:
        """
        Record a timing metric.

        Args:
            name: Metric name
            duration: Duration in seconds
            tags: Optional tags for the metric
        """
        self.timings[name].append(duration)
        self._record_metric(name, duration, tags)

    def get_counter(self, name: str) -> float:
        """Get current counter value."""
        return self.counters.get(name, 0.0)

    def get_gauge(self, name: str) -> float:
        """Get current gauge value."""
        return self.gauges.get(name, 0.0)

    def get_timing_stats(self, name: str) -> Dict[str, float]:
        """
        Get timing statistics.

        Returns:
            Dictionary with min, max, avg, and count
        """
        timings = self.timings.get(name, [])
        if not timings:
            return {'min': 0, 'max': 0, 'avg': 0, 'count': 0}

        return {
            'min': min(timings),
            'max': max(timings),
            'avg': sum(timings) / len(timings),
            'count': len(timings)
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all current metrics.

        Returns:
            Dictionary with all metrics
        """
        timing_stats = {
            name: self.get_timing_stats(name)
            for name in self.timings.keys()
        }

        return {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'timings': timing_stats
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.counters.clear()
        self.gauges.clear()
        self.timings.clear()

    def _record_metric(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Record a metric in history."""
        metric = Metric(name=name, value=value, tags=tags or {})
        self.metrics_history.append(metric)

        # Trim history if needed
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]

    class Timer:
        """Context manager for timing operations."""

        def __init__(self, collector: 'MetricsCollector', name: str, tags: Dict[str, str] = None):
            self.collector = collector
            self.name = name
            self.tags = tags
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            self.collector.timing(self.name, duration, self.tags)

    def timer(self, name: str, tags: Dict[str, str] = None) -> 'MetricsCollector.Timer':
        """
        Create a timer context manager.

        Usage:
            with metrics.timer('operation_name'):
                # ... do work ...
        """
        return self.Timer(self, name, tags)
