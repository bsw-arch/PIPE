"""
AXIS Task Bot - Shared Agent Framework
=======================================
Base classes and utilities for Augmentic AI agents

Part of the AXIS Bot Ecosystem - 46 Collaborative AI Agents
"""

__version__ = "0.1.0"
__author__ = "AXIS Team"

from .base_agent import BaseAgent, AgentConfig
from .augmentic_agent import AugmenticAgent
from .logger import get_logger, setup_logging

__all__ = [
    "BaseAgent",
    "AgentConfig",
    "AugmenticAgent",
    "get_logger",
    "setup_logging",
]
