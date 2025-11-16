"""
Structured Logging for PIPE.

Provides JSON-formatted structured logging for better
log aggregation and analysis in production systems.
"""

import json
import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class StructuredLogger:
    """
    JSON structured logging handler.

    Formats log messages as JSON for easy parsing by
    log aggregation systems like ELK, Splunk, or CloudWatch.
    """

    def __init__(
        self,
        name: str = "pipe",
        level: int = logging.INFO,
        output_file: Optional[Path] = None,
    ):
        """
        Initialize structured logger.

        Args:
            name: Logger name
            level: Logging level
            output_file: Optional file path for JSON logs
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers = []  # Clear existing handlers

        # Add JSON formatter
        if output_file:
            handler = logging.FileHandler(output_file)
        else:
            handler = logging.StreamHandler(sys.stdout)

        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)

    def get_logger(self) -> logging.Logger:
        """Get the configured logger."""
        return self.logger


class JSONFormatter(logging.Formatter):
    """
    Custom log formatter that outputs JSON.

    Formats log records as JSON objects with standard fields:
    - timestamp: ISO 8601 timestamp
    - level: Log level (INFO, ERROR, etc.)
    - logger: Logger name
    - message: Log message
    - Additional context fields
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add process and thread info
        log_data["process"] = {
            "id": record.process,
            "name": record.processName,
        }
        log_data["thread"] = {
            "id": record.thread,
            "name": record.threadName,
        }

        return json.dumps(log_data)


class ContextLogger:
    """
    Logger with automatic context injection.

    Allows adding context fields that are included in all
    subsequent log messages.
    """

    def __init__(
        self, logger: logging.Logger, context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize context logger.

        Args:
            logger: Base logger to use
            context: Default context to include in all logs
        """
        self.logger = logger
        self.context = context or {}

    def add_context(self, **kwargs) -> None:
        """Add fields to logging context."""
        self.context.update(kwargs)

    def remove_context(self, *keys) -> None:
        """Remove fields from logging context."""
        for key in keys:
            self.context.pop(key, None)

    def clear_context(self) -> None:
        """Clear all context fields."""
        self.context = {}

    def _log_with_context(
        self, level: int, message: str, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log message with context."""
        extra_fields = {**self.context}
        if extra:
            extra_fields.update(extra)

        # Create a LogRecord with extra fields
        self.logger.log(level, message, extra={"extra_fields": extra_fields})

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, message, kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message with context."""
        self._log_with_context(logging.INFO, message, kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, message, kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message with context."""
        self._log_with_context(logging.ERROR, message, kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, message, kwargs)


def configure_structured_logging(
    level: str = "INFO",
    json_file: Optional[str] = None,
    enable_console: bool = True,
) -> None:
    """
    Configure structured logging for the entire application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_file: Optional JSON log file path
        enable_console: Enable console output
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = []

    # Add JSON file handler
    if json_file:
        file_handler = logging.FileHandler(json_file)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)

    # Add console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(console_handler)


def create_audit_logger(audit_file: str) -> StructuredLogger:
    """
    Create a dedicated audit logger.

    Audit logs are important for compliance and security,
    so they get their own logger with guaranteed persistence.

    Args:
        audit_file: Path to audit log file

    Returns:
        Configured audit logger
    """
    audit_logger = StructuredLogger(
        name="pipe.audit",
        level=logging.INFO,
        output_file=Path(audit_file),
    )

    return audit_logger


def log_audit_event(
    logger: logging.Logger,
    event_type: str,
    actor: str,
    action: str,
    resource: str,
    result: str,
    **extra_fields,
) -> None:
    """
    Log an audit event in standardized format.

    Args:
        logger: Logger to use
        event_type: Type of event (e.g., "authentication", "authorization")
        actor: Who performed the action
        action: What action was performed
        resource: What resource was affected
        result: Result of the action (success/failure)
        **extra_fields: Additional fields to include
    """
    audit_data = {
        "event_type": event_type,
        "actor": actor,
        "action": action,
        "resource": resource,
        "result": result,
        **extra_fields,
    }

    logger.info(
        f"Audit: {event_type} - {actor} {action} {resource} ({result})",
        extra={"extra_fields": audit_data},
    )
