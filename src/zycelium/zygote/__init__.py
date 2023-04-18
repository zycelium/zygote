"""
Zygote.
"""
from zycelium.zygote.config import (
    config,
    Config as DefaultConfig,
    ConfigParseError,
)
from zycelium.zygote import logging
from zycelium.zygote import models

__version__ = "0.1.0"

version = __version__  # pylint: disable=invalid-name


__all__ = [
    "ConfigParseError",
    "DefaultConfig",
    "config",
    "logging",
    "models",
    "version",
]
