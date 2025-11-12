"""Integration tests for bot system."""

import pytest
import asyncio
from src.bots.pipeline_bot import PipelineBot
from src.bots.data_processor_bot import DataProcessorBot
from src.bots.monitor_bot import MonitorBot


@pytest.mark.asyncio
async def test_pipeline_bot_initialization(bot_config, event_bus, state_manager):
    """Test PipelineBot initialization."""
    bot = PipelineBot(
        name='test_pipeline',
        config=bot_config,
        event_bus=event_bus,
        state_manager=state_manager
    )

    success = await bot.initialize()
    assert success is True
    assert bot.status.value == 'initializing'

    await bot.cleanup()


@pytest.mark.asyncio
async def test_data_processor_bot_initialization(bot_config, event_bus, state_manager, metrics_collector):
    """Test DataProcessorBot initialization."""
    bot = DataProcessorBot(
        name='test_processor',
        config=bot_config,
        event_bus=event_bus,
        state_manager=state_manager,
        metrics=metrics_collector
    )

    success = await bot.initialize()
    assert success is True

    await bot.cleanup()


@pytest.mark.asyncio
async def test_monitor_bot_initialization(bot_config, event_bus, state_manager, metrics_collector):
    """Test MonitorBot initialization."""
    bot = MonitorBot(
        name='test_monitor',
        config=bot_config,
        event_bus=event_bus,
        state_manager=state_manager,
        metrics=metrics_collector
    )

    success = await bot.initialize()
    assert success is True

    await bot.cleanup()


@pytest.mark.asyncio
async def test_bot_communication(bot_config, event_bus, state_manager, metrics_collector):
    """Test communication between bots via event bus."""
    events_received = []

    async def handler(event):
        events_received.append(event)

    event_bus.subscribe('pipeline.completed', handler)

    # Create and initialize pipeline bot
    pipeline_bot = PipelineBot(
        name='test_pipeline',
        config=bot_config,
        event_bus=event_bus,
        state_manager=state_manager
    )

    await pipeline_bot.initialize()

    # Register and run a pipeline
    pipeline_config = {
        'id': 'test_pipeline_1',
        'name': 'Test Pipeline',
        'stages': [
            {'name': 'stage1', 'type': 'task', 'duration': 0.1}
        ],
        'enabled': True
    }

    await pipeline_bot.register_pipeline(pipeline_config)
    await pipeline_bot.run_pipeline('test_pipeline_1')

    # Wait a bit for event propagation
    await asyncio.sleep(0.5)

    # Verify event was received
    assert len(events_received) > 0

    await pipeline_bot.cleanup()


@pytest.mark.asyncio
async def test_data_processor_submit_and_process(bot_config, event_bus, state_manager, metrics_collector):
    """Test data processor bot processing data."""
    bot = DataProcessorBot(
        name='test_processor',
        config=bot_config,
        event_bus=event_bus,
        state_manager=state_manager,
        metrics=metrics_collector
    )

    await bot.initialize()

    # Submit data for processing
    await bot.submit_data('text', 'Hello World', {'source': 'test'})

    # Wait for processing
    await asyncio.sleep(0.5)

    # Check queue was processed
    assert bot.processing_queue.qsize() == 0

    await bot.cleanup()
