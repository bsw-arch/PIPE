"""Main application entry point for PIPE domain bots."""

import asyncio
import signal
import sys
from pathlib import Path
from typing import List

from core.bot_base import BotBase
from core.event_bus import EventBus
from core.state_manager import StateManager
from utils.logger import setup_logging
from utils.metrics import MetricsCollector
from config.config_loader import load_config
from bots.pipeline_bot import PipelineBot
from bots.data_processor_bot import DataProcessorBot
from bots.monitor_bot import MonitorBot


class BotOrchestrator:
    """
    Orchestrates multiple bots in the PIPE domain.

    Manages bot lifecycle, communication, and coordination.
    """

    def __init__(self, config: dict):
        """
        Initialize the bot orchestrator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.bots: List[BotBase] = []
        self.event_bus = EventBus()
        self.state_manager = StateManager(config.get('state_dir', './state'))
        self.metrics = MetricsCollector()
        self.shutdown_event = asyncio.Event()

        # Set up logging
        log_config = config.get('logging', {})
        setup_logging(
            log_level=log_config.get('level', 'INFO'),
            log_file=log_config.get('file')
        )

    async def initialize_bots(self) -> None:
        """Initialize all configured bots."""
        bot_configs = self.config.get('bots', {})

        # Create PipelineBot
        if bot_configs.get('pipeline', {}).get('enabled', True):
            pipeline_bot = PipelineBot(
                name='pipeline_bot',
                config=bot_configs.get('pipeline', {}),
                event_bus=self.event_bus,
                state_manager=self.state_manager
            )
            self.bots.append(pipeline_bot)

        # Create DataProcessorBot
        if bot_configs.get('data_processor', {}).get('enabled', True):
            data_processor = DataProcessorBot(
                name='data_processor_bot',
                config=bot_configs.get('data_processor', {}),
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                metrics=self.metrics
            )
            self.bots.append(data_processor)

        # Create MonitorBot
        if bot_configs.get('monitor', {}).get('enabled', True):
            monitor_bot = MonitorBot(
                name='monitor_bot',
                config=bot_configs.get('monitor', {}),
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                metrics=self.metrics
            )
            self.bots.append(monitor_bot)

        print(f"Initialized {len(self.bots)} bots")

    async def start_bots(self) -> None:
        """Start all bots."""
        print("Starting PIPE domain bots...")

        tasks = []
        for bot in self.bots:
            task = asyncio.create_task(bot.start())
            tasks.append(task)

        # Wait for shutdown signal
        await self.shutdown_event.wait()

        # Stop all bots
        print("\nShutting down bots...")
        for bot in self.bots:
            await bot.stop()

        # Wait for all bot tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)

    async def run(self) -> None:
        """Run the orchestrator."""
        try:
            await self.initialize_bots()
            await self.start_bots()
        except KeyboardInterrupt:
            print("\nReceived interrupt signal")
        except Exception as e:
            print(f"Error running orchestrator: {str(e)}")
            raise
        finally:
            print("Orchestrator shutdown complete")

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\nReceived signal {signum}")
        self.shutdown_event.set()


async def main():
    """Main entry point."""
    print("=" * 60)
    print("PIPE Domain Bot System")
    print("BSW Architecture Project")
    print("=" * 60)
    print()

    # Load configuration
    try:
        config = load_config(config_dir='./config')
    except Exception as e:
        print(f"Failed to load configuration: {str(e)}")
        print("Using default configuration")
        config = {
            'state_dir': './state',
            'logging': {
                'level': 'INFO'
            },
            'bots': {
                'pipeline': {
                    'enabled': True,
                    'check_interval': 30,
                    'default_pipelines': []
                },
                'data_processor': {
                    'enabled': True,
                    'num_workers': 3,
                    'status_interval': 30
                },
                'monitor': {
                    'enabled': True,
                    'monitor_interval': 60,
                    'health_check_interval': 30,
                    'silence_threshold_seconds': 300,
                    'error_threshold': 10
                }
            }
        }

    # Create orchestrator
    orchestrator = BotOrchestrator(config)

    # Set up signal handlers
    signal.signal(signal.SIGINT, orchestrator.handle_shutdown)
    signal.signal(signal.SIGTERM, orchestrator.handle_shutdown)

    # Run
    await orchestrator.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
        sys.exit(0)
