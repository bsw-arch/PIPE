"""Pipeline automation bot for PIPE domain."""

import asyncio
from typing import Dict, Any, List
from datetime import datetime

from ..core.bot_base import BotBase
from ..core.event_bus import Event, EventBus
from ..core.state_manager import StateManager
from ..utils.retry import retry_async


class PipelineBot(BotBase):
    """
    Bot for managing and executing automated pipelines.

    Handles CI/CD pipeline orchestration, task scheduling,
    and workflow automation.
    """

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        event_bus: EventBus,
        state_manager: StateManager
    ):
        """
        Initialize the pipeline bot.

        Args:
            name: Bot name
            config: Configuration dictionary
            event_bus: Event bus for communication
            state_manager: State manager for persistence
        """
        super().__init__(name, config)
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.pipelines: Dict[str, Dict] = {}
        self.running_pipelines: List[str] = []

    async def initialize(self) -> bool:
        """Initialize the pipeline bot."""
        try:
            self.logger.info("Initializing PipelineBot")

            # Load saved state
            state = await self.state_manager.load_state(self.name)
            self.pipelines = state.get('pipelines', {})

            # Subscribe to pipeline events
            self.event_bus.subscribe('pipeline.trigger', self._on_pipeline_trigger)
            self.event_bus.subscribe('pipeline.cancel', self._on_pipeline_cancel)

            # Load default pipelines from config
            default_pipelines = self.config.get('default_pipelines', [])
            for pipeline_config in default_pipelines:
                await self.register_pipeline(pipeline_config)

            self.logger.info(f"PipelineBot initialized with {len(self.pipelines)} pipelines")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize PipelineBot: {str(e)}")
            return False

    async def execute(self) -> None:
        """Main execution loop."""
        self.logger.info("PipelineBot execution started")

        while self.status.value == "running":
            try:
                # Check for scheduled pipelines
                await self._check_scheduled_pipelines()

                # Monitor running pipelines
                await self._monitor_running_pipelines()

                # Publish status
                await self._publish_status()

                # Sleep interval
                await asyncio.sleep(self.config.get('check_interval', 30))

            except Exception as e:
                self.logger.error(f"Error in execution loop: {str(e)}", exc_info=True)
                self.error_count += 1
                await asyncio.sleep(5)

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up PipelineBot")

        # Cancel all running pipelines
        for pipeline_id in self.running_pipelines[:]:
            await self._cancel_pipeline(pipeline_id)

        # Save state
        await self.state_manager.save_state(self.name, {
            'pipelines': self.pipelines
        })

        self.logger.info("PipelineBot cleanup complete")

    async def register_pipeline(self, pipeline_config: Dict[str, Any]) -> str:
        """
        Register a new pipeline.

        Args:
            pipeline_config: Pipeline configuration

        Returns:
            Pipeline ID
        """
        pipeline_id = pipeline_config.get('id', f"pipeline_{len(self.pipelines)}")

        self.pipelines[pipeline_id] = {
            'id': pipeline_id,
            'name': pipeline_config.get('name', pipeline_id),
            'stages': pipeline_config.get('stages', []),
            'schedule': pipeline_config.get('schedule'),
            'enabled': pipeline_config.get('enabled', True),
            'created_at': datetime.now().isoformat(),
            'last_run': None,
            'run_count': 0
        }

        self.logger.info(f"Registered pipeline: {pipeline_id}")
        await self.state_manager.save_state(self.name, {'pipelines': self.pipelines})

        return pipeline_id

    @retry_async(max_attempts=3, delay=2.0)
    async def run_pipeline(self, pipeline_id: str, context: Dict[str, Any] = None) -> bool:
        """
        Execute a pipeline.

        Args:
            pipeline_id: ID of the pipeline to run
            context: Optional context data for the pipeline

        Returns:
            True if successful, False otherwise
        """
        if pipeline_id not in self.pipelines:
            self.logger.error(f"Pipeline not found: {pipeline_id}")
            return False

        pipeline = self.pipelines[pipeline_id]
        if not pipeline['enabled']:
            self.logger.warning(f"Pipeline {pipeline_id} is disabled")
            return False

        self.logger.info(f"Starting pipeline: {pipeline_id}")
        self.running_pipelines.append(pipeline_id)

        try:
            # Publish pipeline start event
            await self.event_bus.publish(Event(
                event_type='pipeline.started',
                source=self.name,
                data={'pipeline_id': pipeline_id, 'context': context}
            ))

            # Execute each stage
            for stage in pipeline['stages']:
                stage_name = stage.get('name', 'unnamed')
                self.logger.info(f"Executing stage: {stage_name} in pipeline {pipeline_id}")

                # Simulate stage execution
                await self._execute_stage(stage, context)

            # Update pipeline stats
            pipeline['last_run'] = datetime.now().isoformat()
            pipeline['run_count'] += 1
            self.task_count += 1

            # Publish pipeline complete event
            await self.event_bus.publish(Event(
                event_type='pipeline.completed',
                source=self.name,
                data={'pipeline_id': pipeline_id, 'success': True}
            ))

            self.logger.info(f"Pipeline {pipeline_id} completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Pipeline {pipeline_id} failed: {str(e)}", exc_info=True)
            self.error_count += 1

            await self.event_bus.publish(Event(
                event_type='pipeline.failed',
                source=self.name,
                data={'pipeline_id': pipeline_id, 'error': str(e)}
            ))

            return False

        finally:
            if pipeline_id in self.running_pipelines:
                self.running_pipelines.remove(pipeline_id)
            await self.state_manager.save_state(self.name, {'pipelines': self.pipelines})

    async def _execute_stage(self, stage: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Execute a single pipeline stage."""
        stage_type = stage.get('type', 'task')
        duration = stage.get('duration', 2)

        # Simulate stage work
        await asyncio.sleep(duration)

        self.logger.debug(f"Stage {stage.get('name')} completed")

    async def _check_scheduled_pipelines(self) -> None:
        """Check for pipelines that should run based on schedule."""
        # Placeholder for schedule checking logic
        pass

    async def _monitor_running_pipelines(self) -> None:
        """Monitor health of running pipelines."""
        if self.running_pipelines:
            self.logger.debug(f"Currently running {len(self.running_pipelines)} pipelines")

    async def _cancel_pipeline(self, pipeline_id: str) -> None:
        """Cancel a running pipeline."""
        if pipeline_id in self.running_pipelines:
            self.running_pipelines.remove(pipeline_id)
            self.logger.info(f"Cancelled pipeline: {pipeline_id}")

    async def _publish_status(self) -> None:
        """Publish bot status to event bus."""
        status = self.get_status()
        status['running_pipelines'] = len(self.running_pipelines)
        status['total_pipelines'] = len(self.pipelines)

        await self.event_bus.publish(Event(
            event_type='bot.status',
            source=self.name,
            data=status
        ))

    async def _on_pipeline_trigger(self, event: Event) -> None:
        """Handle pipeline trigger events."""
        pipeline_id = event.data.get('pipeline_id')
        context = event.data.get('context', {})

        if pipeline_id:
            await self.run_pipeline(pipeline_id, context)

    async def _on_pipeline_cancel(self, event: Event) -> None:
        """Handle pipeline cancel events."""
        pipeline_id = event.data.get('pipeline_id')

        if pipeline_id:
            await self._cancel_pipeline(pipeline_id)
