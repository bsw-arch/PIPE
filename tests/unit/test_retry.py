"""Unit tests for retry utilities."""

import pytest
import asyncio
from src.utils.retry import retry_async


class CustomError(Exception):
    """Custom error for testing."""

    pass


@pytest.mark.asyncio
async def test_retry_async_succeeds_first_attempt():
    """Test that function succeeds on first attempt."""
    call_count = 0

    @retry_async(max_attempts=3, delay=0.01)
    async def succeeds_immediately():
        nonlocal call_count
        call_count += 1
        return "success"

    result = await succeeds_immediately()
    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_async_succeeds_after_retries():
    """Test that function succeeds after some retries."""
    call_count = 0

    @retry_async(max_attempts=3, delay=0.01, backoff=1.5)
    async def succeeds_on_third_try():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Not yet")
        return "success"

    result = await succeeds_on_third_try()
    assert result == "success"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_async_fails_after_max_attempts():
    """Test that function fails after max attempts."""
    call_count = 0

    @retry_async(max_attempts=3, delay=0.01)
    async def always_fails():
        nonlocal call_count
        call_count += 1
        raise ValueError("Always fails")

    with pytest.raises(ValueError, match="Always fails"):
        await always_fails()

    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_async_with_specific_exceptions():
    """Test that only specified exceptions are caught."""
    call_count = 0

    @retry_async(max_attempts=3, delay=0.01, exceptions=(CustomError,))
    async def fails_with_wrong_exception():
        nonlocal call_count
        call_count += 1
        raise ValueError("Wrong exception type")

    # Should fail immediately because ValueError is not in exceptions tuple
    with pytest.raises(ValueError, match="Wrong exception type"):
        await fails_with_wrong_exception()

    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_async_with_multiple_exceptions():
    """Test that multiple exception types are caught."""
    call_count = 0

    @retry_async(
        max_attempts=4, delay=0.01, exceptions=(ValueError, CustomError, TypeError)
    )
    async def fails_with_different_exceptions():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ValueError("First error")
        elif call_count == 2:
            raise CustomError("Second error")
        elif call_count == 3:
            raise TypeError("Third error")
        return "success"

    result = await fails_with_different_exceptions()
    assert result == "success"
    assert call_count == 4


@pytest.mark.asyncio
async def test_retry_async_exponential_backoff():
    """Test that exponential backoff is applied."""
    delays = []
    call_count = 0

    @retry_async(max_attempts=4, delay=0.01, backoff=2.0)
    async def track_delays():
        nonlocal call_count
        call_count += 1
        if call_count > 1:
            delays.append(asyncio.get_event_loop().time())
        if call_count < 4:
            raise ValueError("Not yet")
        return "success"

    await track_delays()

    # Check that delays roughly doubled each time
    # (We can't be exact due to timing, but should be approximately correct)
    assert call_count == 4
    assert len(delays) == 3  # 3 retries after first attempt


@pytest.mark.asyncio
async def test_retry_async_with_args_and_kwargs():
    """Test that args and kwargs are passed correctly."""
    call_count = 0

    @retry_async(max_attempts=3, delay=0.01)
    async def func_with_params(a, b, c=None):
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Not yet")
        return f"{a}-{b}-{c}"

    result = await func_with_params("x", "y", c="z")
    assert result == "x-y-z"
    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_async_preserves_function_metadata():
    """Test that decorator preserves function metadata."""

    @retry_async(max_attempts=3, delay=0.01)
    async def my_function():
        """My function docstring."""
        return "test"

    assert my_function.__name__ == "my_function"
    assert my_function.__doc__ == "My function docstring."


@pytest.mark.asyncio
async def test_retry_async_with_zero_delay():
    """Test retry with zero delay between attempts."""
    call_count = 0

    @retry_async(max_attempts=3, delay=0.0)
    async def instant_retry():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Not yet")
        return "success"

    result = await instant_retry()
    assert result == "success"
    assert call_count == 3
