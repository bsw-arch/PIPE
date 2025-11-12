"""Base class for all PIPE domain bots."""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class BotStatus(Enum):
    """Bot operational status."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class BotBase(ABC):
    """
    Abstract base class for all PIPE domain bots.

    Provides common functionality for bot lifecycle management,
    logging, error handling, and state management.
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize the bot.

        Args:
            name: Unique name for this bot instance
            config: Configuration dictionary for the bot
        """
        self.name = name
        self.config = config
        self.status = BotStatus.INITIALIZING
        self.start_time: Optional[datetime] = None
        self.error_count = 0
        self.task_count = 0

        # Set up logging
        self.logger = logging.getLogger(f"pipe.bot.{name}")
        self.logger.setLevel(config.get('log_level', 'INFO'))

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the bot and its resources.

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    async def execute(self) -> None:
        """
        Main execution loop for the bot.

        This method should contain the core logic of the bot.
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up resources before shutdown.
        """
        pass

    async def start(self) -> None:
        """Start the bot."""
        try:
            self.logger.info(f"Starting bot: {self.name}")

            if not await self.initialize():
                raise RuntimeError("Bot initialization failed")

            self.status = BotStatus.RUNNING
            self.start_time = datetime.now()
            self.logger.info(f"Bot {self.name} is now running")

            await self.execute()

        except Exception as e:
            self.logger.error(f"Error in bot {self.name}: {str(e)}", exc_info=True)
            self.status = BotStatus.ERROR
            self.error_count += 1
            raise
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop the bot gracefully."""
        if self.status == BotStatus.STOPPED:
            return

        self.logger.info(f"Stopping bot: {self.name}")
        self.status = BotStatus.STOPPED

        try:
            await self.cleanup()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}", exc_info=True)

        self.logger.info(f"Bot {self.name} stopped")

    async def pause(self) -> None:
        """Pause bot execution."""
        if self.status == BotStatus.RUNNING:
            self.status = BotStatus.PAUSED
            self.logger.info(f"Bot {self.name} paused")

    async def resume(self) -> None:
        """Resume bot execution."""
        if self.status == BotStatus.PAUSED:
            self.status = BotStatus.RUNNING
            self.logger.info(f"Bot {self.name} resumed")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current bot status and metrics.

        Returns:
            Dictionary containing status information
        """
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()

        return {
            'name': self.name,
            'status': self.status.value,
            'uptime_seconds': uptime,
            'error_count': self.error_count,
            'task_count': self.task_count,
            'start_time': self.start_time.isoformat() if self.start_time else None
        }

    async def health_check(self) -> bool:
        """
        Perform health check on the bot.

        Returns:
            True if bot is healthy, False otherwise
        """
        return self.status in [BotStatus.RUNNING, BotStatus.PAUSED]
