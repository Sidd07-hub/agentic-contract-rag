"""
Utility helper functions used across the project.
"""

from pathlib import Path


def ensure_directory(path: Path) -> None:
    """
    Create directory if it does not exist.

    Args:
        path: Directory path.
    """
    path.mkdir(parents=True, exist_ok=True)


def file_exists(path: Path) -> bool:
    """
    Check whether a file exists.

    Args:
        path: File path.

    Returns:
        True if the file exists.
    """
    return path.exists()