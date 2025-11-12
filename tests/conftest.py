"""Pytest configuration and fixtures."""

import asyncio
import pytest
import tempfile
import shutil

from src.core.event_bus import EventBus
from src.core.state_manager import StateManager
from src.utils.metrics import MetricsCollector


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def event_bus():
    """Create a fresh EventBus instance for testing."""
    return EventBus()


@pytest.fixture
def temp_state_dir():
    """Create a temporary directory for state management."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def state_manager(temp_state_dir):
    """Create a StateManager with temporary storage."""
    return StateManager(state_dir=temp_state_dir)


@pytest.fixture
def metrics_collector():
    """Create a fresh MetricsCollector instance for testing."""
    return MetricsCollector()


@pytest.fixture
def bot_config():
    """Provide default bot configuration for testing."""
    return {
        "log_level": "DEBUG",
        "check_interval": 1,
        "num_workers": 2,
        "monitor_interval": 1,
        "health_check_interval": 1,
    }
