"""Unit tests for MetricsCollector."""

import pytest
import asyncio
from src.utils.metrics import MetricsCollector


def test_metrics_increment(metrics_collector):
    """Test incrementing a counter."""
    metrics_collector.increment('test.counter', 5)
    assert metrics_collector.get_counter('test.counter') == 5

    metrics_collector.increment('test.counter', 3)
    assert metrics_collector.get_counter('test.counter') == 8


def test_metrics_gauge(metrics_collector):
    """Test setting a gauge value."""
    metrics_collector.gauge('test.gauge', 42)
    assert metrics_collector.get_gauge('test.gauge') == 42

    metrics_collector.gauge('test.gauge', 100)
    assert metrics_collector.get_gauge('test.gauge') == 100


def test_metrics_timing(metrics_collector):
    """Test recording timing metrics."""
    metrics_collector.timing('test.operation', 1.5)
    metrics_collector.timing('test.operation', 2.0)
    metrics_collector.timing('test.operation', 1.0)

    stats = metrics_collector.get_timing_stats('test.operation')
    assert stats['count'] == 3
    assert stats['min'] == 1.0
    assert stats['max'] == 2.0
    assert stats['avg'] == pytest.approx(1.5, rel=0.01)


def test_metrics_timer_context_manager(metrics_collector):
    """Test timer context manager."""
    import time

    with metrics_collector.timer('test.operation'):
        time.sleep(0.01)

    stats = metrics_collector.get_timing_stats('test.operation')
    assert stats['count'] == 1
    assert stats['avg'] > 0.01


def test_metrics_get_all(metrics_collector):
    """Test getting all metrics."""
    metrics_collector.increment('counter1', 10)
    metrics_collector.gauge('gauge1', 50)
    metrics_collector.timing('timing1', 1.5)

    all_metrics = metrics_collector.get_all_metrics()

    assert 'counters' in all_metrics
    assert 'gauges' in all_metrics
    assert 'timings' in all_metrics
    assert all_metrics['counters']['counter1'] == 10
    assert all_metrics['gauges']['gauge1'] == 50


def test_metrics_reset(metrics_collector):
    """Test resetting all metrics."""
    metrics_collector.increment('counter1', 10)
    metrics_collector.gauge('gauge1', 50)
    metrics_collector.timing('timing1', 1.5)

    metrics_collector.reset()

    all_metrics = metrics_collector.get_all_metrics()
    assert len(all_metrics['counters']) == 0
    assert len(all_metrics['gauges']) == 0
    assert len(all_metrics['timings']) == 0
