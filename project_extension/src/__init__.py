"""Self-contained gaze fixation generator for project_extension."""

from .config import EXTENSION_CONFIG
from .generator import run_cli

__all__ = ["EXTENSION_CONFIG", "run_cli"]

