"""Unit tests for logging utilities."""

import pytest
import logging
import sys
from src.utils.logger import setup_logging


@pytest.fixture(autouse=True)
def cleanup_logging():
    """Clean up logging handlers after each test."""
    yield
    # Remove all handlers from root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)


def test_setup_logging_default():
    """Test setup_logging with default parameters."""
    logger = setup_logging()

    assert logger == logging.getLogger()
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_setup_logging_debug_level():
    """Test setup_logging with DEBUG level."""
    logger = setup_logging(log_level="DEBUG")

    assert logger.level == logging.DEBUG


def test_setup_logging_warning_level():
    """Test setup_logging with WARNING level."""
    logger = setup_logging(log_level="WARNING")

    assert logger.level == logging.WARNING


def test_setup_logging_error_level():
    """Test setup_logging with ERROR level."""
    logger = setup_logging(log_level="ERROR")

    assert logger.level == logging.ERROR


def test_setup_logging_critical_level():
    """Test setup_logging with CRITICAL level."""
    logger = setup_logging(log_level="CRITICAL")

    assert logger.level == logging.CRITICAL


def test_setup_logging_lowercase_level():
    """Test setup_logging with lowercase level string."""
    logger = setup_logging(log_level="info")

    assert logger.level == logging.INFO


def test_setup_logging_custom_format():
    """Test setup_logging with custom format."""
    custom_format = "%(levelname)s - %(message)s"
    logger = setup_logging(log_format=custom_format)

    handler = logger.handlers[0]
    assert handler.formatter._fmt == custom_format


def test_setup_logging_with_file(tmp_path):
    """Test setup_logging with file output."""
    log_file = tmp_path / "test.log"
    logger = setup_logging(log_file=str(log_file))

    # Should have console + file handler
    assert len(logger.handlers) == 2
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)

    # Test that log file was created
    assert log_file.exists()


def test_setup_logging_creates_log_directory(tmp_path):
    """Test that setup_logging creates log directory if needed."""
    log_file = tmp_path / "logs" / "nested" / "test.log"
    setup_logging(log_file=str(log_file))  # noqa: F841

    assert log_file.parent.exists()
    assert log_file.exists()


def test_setup_logging_file_handler_formatter(tmp_path):
    """Test that file handler has correct formatter."""
    log_file = tmp_path / "test.log"
    custom_format = "CUSTOM: %(message)s"
    logger = setup_logging(log_file=str(log_file), log_format=custom_format)

    file_handler = next(
        h for h in logger.handlers if isinstance(h, logging.FileHandler)
    )
    assert file_handler.formatter._fmt == custom_format


def test_setup_logging_removes_existing_handlers():
    """Test that setup_logging removes existing handlers."""
    root_logger = logging.getLogger()

    # Record initial handler count (pytest may have added handlers)
    initial_count = len(root_logger.handlers)

    # Add a dummy handler
    dummy_handler = logging.StreamHandler()
    root_logger.addHandler(dummy_handler)

    assert len(root_logger.handlers) == initial_count + 1

    # Setup logging should remove all handlers and add only one
    setup_logging()

    # Should only have the new console handler
    assert len(root_logger.handlers) == 1
    assert root_logger.handlers[0] is not dummy_handler


def test_setup_logging_console_handler_stream():
    """Test that console handler writes to stdout."""
    logger = setup_logging()

    console_handler = logger.handlers[0]
    assert console_handler.stream == sys.stdout


def test_setup_logging_writes_to_file(tmp_path):
    """Test that logging actually writes to file."""
    log_file = tmp_path / "test.log"
    setup_logging(log_level="INFO", log_file=str(log_file))  # noqa: F841

    # Log a test message
    test_logger = logging.getLogger("test")
    test_logger.info("Test message")

    # Read file content
    with open(log_file, "r") as f:
        content = f.read()

    assert "Test message" in content
    assert "INFO" in content


def test_setup_logging_respects_log_level(tmp_path):
    """Test that log level is respected."""
    log_file = tmp_path / "test.log"
    setup_logging(log_level="WARNING", log_file=str(log_file))  # noqa: F841

    test_logger = logging.getLogger("test")
    test_logger.debug("Debug message")
    test_logger.info("Info message")
    test_logger.warning("Warning message")
    test_logger.error("Error message")

    # Read file content
    with open(log_file, "r") as f:
        content = f.read()

    # Debug and Info should be filtered out
    assert "Debug message" not in content
    assert "Info message" not in content

    # Warning and Error should be included
    assert "Warning message" in content
    assert "Error message" in content
