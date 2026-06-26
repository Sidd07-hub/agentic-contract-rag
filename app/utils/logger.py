"""
Centralized logging configuration for the Agentic Contract RAG project.

This module provides a reusable logger instance that can be imported
throughout the application.
"""

import logging
from rich.logging import RichHandler

from app.config import LOG_LEVEL


def setup_logger(name: str) -> logging.Logger:
    """
    Create and configure a logger.

    Args:
        name: Name of the logger.

    Returns:
        Configured logger instance.
    """

    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(LOG_LEVEL)

    handler = RichHandler(
        rich_tracebacks=True,
        show_path=False,
        markup=True
    )

    formatter = logging.Formatter(
        "%(message)s"
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    logger.propagate = False

    return logger