"""Data processing bot for PIPE domain."""

import asyncio
import json
from typing import Dict, Any, List, Callable
from datetime import datetime
from pathlib import Path

from ..core.bot_base import BotBase
from ..core.event_bus import Event, EventBus
from ..core.state_manager import StateManager
from ..utils.retry import retry_async
from ..utils.metrics import MetricsCollector


class DataProcessorBot(BotBase):
    """
    Bot for processing and transforming data streams.

    Handles data ingestion, transformation, validation,
    and output to various destinations.
    """

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        event_bus: EventBus,
        state_manager: StateManager,
        metrics: MetricsCollector
    ):
        """
        Initialize the data processor bot.

        Args:
            name: Bot name
            config: Configuration dictionary
            event_bus: Event bus for communication
            state_manager: State manager for persistence
            metrics: Metrics collector
        """
        super().__init__(name, config)
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.metrics = metrics
        self.processors: Dict[str, Callable] = {}
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.workers: List[asyncio.Task] = []

    async def initialize(self) -> bool:
        """Initialize the data processor bot."""
        try:
            self.logger.info("Initializing DataProcessorBot")

            # Load saved state
            state = await self.state_manager.load_state(self.name)
            processed_count = state.get('processed_count', 0)
            self.task_count = processed_count

            # Register default processors
            self._register_default_processors()

            # Subscribe to data events
            self.event_bus.subscribe('data.process', self._on_data_process)
            self.event_bus.subscribe('data.batch', self._on_data_batch)

            # Start worker tasks
            num_workers = self.config.get('num_workers', 3)
            for i in range(num_workers):
                worker = asyncio.create_task(self._worker(f"worker-{i}"))
                self.workers.append(worker)

            self.logger.info(f"DataProcessorBot initialized with {num_workers} workers")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize DataProcessorBot: {str(e)}")
            return False

    async def execute(self) -> None:
        """Main execution loop."""
        self.logger.info("DataProcessorBot execution started")

        while self.status.value == "running":
            try:
                # Monitor queue size
                queue_size = self.processing_queue.qsize()
                self.metrics.gauge('data_processor.queue_size', queue_size)

                # Publish status
                await self._publish_status()

                # Sleep interval
                await asyncio.sleep(self.config.get('status_interval', 30))

            except Exception as e:
                self.logger.error(f"Error in execution loop: {str(e)}", exc_info=True)
                self.error_count += 1
                await asyncio.sleep(5)

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up DataProcessorBot")

        # Cancel worker tasks
        for worker in self.workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)

        # Save state
        await self.state_manager.save_state(self.name, {
            'processed_count': self.task_count
        })

        self.logger.info("DataProcessorBot cleanup complete")

    def _register_default_processors(self) -> None:
        """Register default data processors."""
        self.processors['json'] = self._process_json
        self.processors['csv'] = self._process_csv
        self.processors['text'] = self._process_text
        self.processors['transform'] = self._process_transform
        self.processors['validate'] = self._process_validate

    async def _worker(self, worker_id: str) -> None:
        """
        Worker task for processing data from queue.

        Args:
            worker_id: Unique identifier for this worker
        """
        self.logger.info(f"Worker {worker_id} started")

        while self.status.value == "running":
            try:
                # Get data from queue with timeout
                try:
                    data_item = await asyncio.wait_for(
                        self.processing_queue.get(),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Process the data
                with self.metrics.timer('data_processor.processing_time'):
                    await self._process_data_item(data_item, worker_id)

                self.processing_queue.task_done()
                self.task_count += 1
                self.metrics.increment('data_processor.items_processed')

            except asyncio.CancelledError:
                self.logger.info(f"Worker {worker_id} cancelled")
                break
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {str(e)}", exc_info=True)
                self.error_count += 1
                self.metrics.increment('data_processor.errors')

        self.logger.info(f"Worker {worker_id} stopped")

    @retry_async(max_attempts=3, delay=1.0)
    async def _process_data_item(self, data_item: Dict[str, Any], worker_id: str) -> None:
        """
        Process a single data item.

        Args:
            data_item: Data to process
            worker_id: ID of the worker processing this item
        """
        processor_type = data_item.get('type', 'text')
        data = data_item.get('data')
        metadata = data_item.get('metadata', {})

        self.logger.debug(f"Worker {worker_id} processing {processor_type} data")

        # Get appropriate processor
        processor = self.processors.get(processor_type, self._process_default)

        # Process the data
        result = await processor(data, metadata)

        # Publish result
        await self.event_bus.publish(Event(
            event_type='data.processed',
            source=self.name,
            data={
                'type': processor_type,
                'result': result,
                'metadata': metadata,
                'worker_id': worker_id
            }
        ))

    async def _process_json(self, data: Any, metadata: Dict) -> Dict[str, Any]:
        """Process JSON data."""
        if isinstance(data, str):
            data = json.loads(data)

        # Example transformation
        processed = {
            'original': data,
            'processed_at': datetime.now().isoformat(),
            'metadata': metadata
        }

        return processed

    async def _process_csv(self, data: Any, metadata: Dict) -> Dict[str, Any]:
        """Process CSV data."""
        # Simulate CSV processing
        await asyncio.sleep(0.1)

        return {
            'rows_processed': len(data.split('\n')) if isinstance(data, str) else 0,
            'processed_at': datetime.now().isoformat()
        }

    async def _process_text(self, data: Any, metadata: Dict) -> Dict[str, Any]:
        """Process text data."""
        text = str(data)

        return {
            'length': len(text),
            'word_count': len(text.split()),
            'processed_at': datetime.now().isoformat()
        }

    async def _process_transform(self, data: Any, metadata: Dict) -> Dict[str, Any]:
        """Apply transformations to data."""
        transformations = metadata.get('transformations', [])

        result = data
        for transform in transformations:
            # Apply transformation (placeholder)
            result = f"transformed_{result}"

        return {'transformed_data': result}

    async def _process_validate(self, data: Any, metadata: Dict) -> Dict[str, Any]:
        """Validate data against schema."""
        schema = metadata.get('schema', {})

        # Placeholder validation
        is_valid = True
        errors = []

        return {
            'valid': is_valid,
            'errors': errors,
            'validated_at': datetime.now().isoformat()
        }

    async def _process_default(self, data: Any, metadata: Dict) -> Dict[str, Any]:
        """Default processor."""
        return {
            'data': data,
            'processed_at': datetime.now().isoformat()
        }

    async def submit_data(self, data_type: str, data: Any, metadata: Dict = None) -> None:
        """
        Submit data for processing.

        Args:
            data_type: Type of data (json, csv, text, etc.)
            data: The data to process
            metadata: Optional metadata
        """
        data_item = {
            'type': data_type,
            'data': data,
            'metadata': metadata or {},
            'submitted_at': datetime.now().isoformat()
        }

        await self.processing_queue.put(data_item)
        self.metrics.increment('data_processor.items_queued')

    async def _publish_status(self) -> None:
        """Publish bot status to event bus."""
        status = self.get_status()
        status['queue_size'] = self.processing_queue.qsize()
        status['active_workers'] = len(self.workers)
        status['processors'] = list(self.processors.keys())

        await self.event_bus.publish(Event(
            event_type='bot.status',
            source=self.name,
            data=status
        ))

    async def _on_data_process(self, event: Event) -> None:
        """Handle data processing events."""
        data_type = event.data.get('type', 'text')
        data = event.data.get('data')
        metadata = event.data.get('metadata', {})

        await self.submit_data(data_type, data, metadata)

    async def _on_data_batch(self, event: Event) -> None:
        """Handle batch data processing events."""
        batch = event.data.get('batch', [])

        for item in batch:
            await self.submit_data(
                item.get('type', 'text'),
                item.get('data'),
                item.get('metadata', {})
            )
