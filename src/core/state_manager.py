"""State management for PIPE domain bots."""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class StateManager:
    """
    Manages persistent state for bots.

    Provides key-value storage with automatic persistence
    and state recovery.
    """

    def __init__(self, state_dir: str = "./state"):
        """
        Initialize the state manager.

        Args:
            state_dir: Directory to store state files
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state: Dict[str, Dict[str, Any]] = {}
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger("pipe.statemanager")
        self.auto_save = True

    async def load_state(self, bot_name: str) -> Dict[str, Any]:
        """
        Load state for a specific bot.

        Args:
            bot_name: Name of the bot

        Returns:
            State dictionary for the bot
        """
        async with self.lock:
            if bot_name in self.state:
                return self.state[bot_name]

            state_file = self.state_dir / f"{bot_name}.json"
            if state_file.exists():
                try:
                    with open(state_file, 'r') as f:
                        loaded_state = json.load(f)
                        self.state[bot_name] = loaded_state
                        self.logger.info(f"Loaded state for bot: {bot_name}")
                        return loaded_state
                except Exception as e:
                    self.logger.error(f"Failed to load state for {bot_name}: {str(e)}")

            # Return empty state if file doesn't exist
            self.state[bot_name] = {}
            return self.state[bot_name]

    async def save_state(self, bot_name: str, state_data: Dict[str, Any] = None) -> bool:
        """
        Save state for a specific bot.

        Args:
            bot_name: Name of the bot
            state_data: State data to save (if None, saves current state)

        Returns:
            True if save successful, False otherwise
        """
        async with self.lock:
            if state_data is not None:
                self.state[bot_name] = state_data

            if bot_name not in self.state:
                self.logger.warning(f"No state to save for bot: {bot_name}")
                return False

            state_file = self.state_dir / f"{bot_name}.json"
            try:
                # Add metadata
                save_data = {
                    'bot_name': bot_name,
                    'last_updated': datetime.now().isoformat(),
                    'data': self.state[bot_name]
                }

                with open(state_file, 'w') as f:
                    json.dump(save_data, f, indent=2)

                self.logger.debug(f"Saved state for bot: {bot_name}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to save state for {bot_name}: {str(e)}")
                return False

    async def get_value(self, bot_name: str, key: str, default: Any = None) -> Any:
        """
        Get a value from bot state.

        Args:
            bot_name: Name of the bot
            key: Key to retrieve
            default: Default value if key doesn't exist

        Returns:
            The value or default
        """
        state = await self.load_state(bot_name)
        return state.get(key, default)

    async def set_value(self, bot_name: str, key: str, value: Any) -> None:
        """
        Set a value in bot state.

        Args:
            bot_name: Name of the bot
            key: Key to set
            value: Value to store
        """
        state = await self.load_state(bot_name)
        state[key] = value

        if self.auto_save:
            await self.save_state(bot_name)

    async def delete_value(self, bot_name: str, key: str) -> bool:
        """
        Delete a value from bot state.

        Args:
            bot_name: Name of the bot
            key: Key to delete

        Returns:
            True if key was deleted, False if it didn't exist
        """
        state = await self.load_state(bot_name)
        if key in state:
            del state[key]
            if self.auto_save:
                await self.save_state(bot_name)
            return True
        return False

    async def clear_state(self, bot_name: str) -> None:
        """
        Clear all state for a bot.

        Args:
            bot_name: Name of the bot
        """
        async with self.lock:
            self.state[bot_name] = {}
            await self.save_state(bot_name)
            self.logger.info(f"Cleared state for bot: {bot_name}")
