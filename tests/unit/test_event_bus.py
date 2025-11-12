"""Unit tests for EventBus."""

import pytest
from src.core.event_bus import Event, EventBus


@pytest.mark.asyncio
async def test_event_bus_subscribe_and_publish(event_bus):
    """Test subscribing to and publishing events."""
    received_events = []

    async def handler(event: Event):
        received_events.append(event)

    event_bus.subscribe('test.event', handler)

    event = Event(
        event_type='test.event',
        source='test',
        data={'message': 'hello'}
    )

    await event_bus.publish(event)

    assert len(received_events) == 1
    assert received_events[0].event_type == 'test.event'
    assert received_events[0].data['message'] == 'hello'


@pytest.mark.asyncio
async def test_event_bus_unsubscribe(event_bus):
    """Test unsubscribing from events."""
    received_events = []

    async def handler(event: Event):
        received_events.append(event)

    event_bus.subscribe('test.event', handler)
    event_bus.unsubscribe('test.event', handler)

    event = Event(
        event_type='test.event',
        source='test',
        data={}
    )

    await event_bus.publish(event)

    assert len(received_events) == 0


@pytest.mark.asyncio
async def test_event_bus_multiple_subscribers(event_bus):
    """Test multiple subscribers to same event."""
    received_1 = []
    received_2 = []

    async def handler1(event: Event):
        received_1.append(event)

    async def handler2(event: Event):
        received_2.append(event)

    event_bus.subscribe('test.event', handler1)
    event_bus.subscribe('test.event', handler2)

    event = Event(
        event_type='test.event',
        source='test',
        data={}
    )

    await event_bus.publish(event)

    assert len(received_1) == 1
    assert len(received_2) == 1


def test_event_bus_history(event_bus):
    """Test event history tracking."""
    assert len(event_bus.get_history()) == 0

    event_bus.event_history.append(Event(
        event_type='test.event',
        source='test',
        data={}
    ))

    history = event_bus.get_history()
    assert len(history) == 1
    assert history[0].event_type == 'test.event'


def test_event_bus_clear_history(event_bus):
    """Test clearing event history."""
    event_bus.event_history.append(Event(
        event_type='test.event',
        source='test',
        data={}
    ))

    event_bus.clear_history()
    assert len(event_bus.get_history()) == 0
