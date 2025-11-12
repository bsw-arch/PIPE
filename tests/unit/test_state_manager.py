"""Unit tests for StateManager."""

import pytest
from src.core.state_manager import StateManager


@pytest.mark.asyncio
async def test_state_manager_save_and_load(state_manager):
    """Test saving and loading state."""
    bot_name = "test_bot"
    state_data = {
        'counter': 42,
        'name': 'test'
    }

    # Save state
    success = await state_manager.save_state(bot_name, state_data)
    assert success is True

    # Load state
    loaded_state = await state_manager.load_state(bot_name)
    assert loaded_state['counter'] == 42
    assert loaded_state['name'] == 'test'


@pytest.mark.asyncio
async def test_state_manager_get_set_value(state_manager):
    """Test getting and setting individual values."""
    bot_name = "test_bot"

    # Set value
    await state_manager.set_value(bot_name, 'key1', 'value1')

    # Get value
    value = await state_manager.get_value(bot_name, 'key1')
    assert value == 'value1'


@pytest.mark.asyncio
async def test_state_manager_default_value(state_manager):
    """Test getting value with default."""
    bot_name = "test_bot"

    value = await state_manager.get_value(bot_name, 'nonexistent', default='default_val')
    assert value == 'default_val'


@pytest.mark.asyncio
async def test_state_manager_delete_value(state_manager):
    """Test deleting a value."""
    bot_name = "test_bot"

    # Set and delete
    await state_manager.set_value(bot_name, 'key1', 'value1')
    deleted = await state_manager.delete_value(bot_name, 'key1')
    assert deleted is True

    # Try to get deleted value
    value = await state_manager.get_value(bot_name, 'key1')
    assert value is None


@pytest.mark.asyncio
async def test_state_manager_clear_state(state_manager):
    """Test clearing all state for a bot."""
    bot_name = "test_bot"

    # Set multiple values
    await state_manager.set_value(bot_name, 'key1', 'value1')
    await state_manager.set_value(bot_name, 'key2', 'value2')

    # Clear state
    await state_manager.clear_state(bot_name)

    # Verify cleared
    state = await state_manager.load_state(bot_name)
    assert len(state) == 0
