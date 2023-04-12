"""
Plug-in agents discovery.
"""
import importlib
import pkgutil
from typing import Iterable

from zycelium.zygote.logging import get_logger

log = get_logger("zygote.plugin")


def discover_agents() -> Iterable[str]:
    """Discover agents."""

    def _iter_namespace(ns_pkg):
        return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

    # Built-in agents
    log.info("Discovering built-in agents...")
    namespace = importlib.import_module("zycelium.zygote.agents")
    for _, name, _ in _iter_namespace(namespace):
        log.info("Found built-in agent: %s", name)
        yield name

    # Installable agents
    log.info("Discovering installed agents")
    namespace = importlib.import_module("zycelium.agents")
    for _, name, _ in _iter_namespace(namespace):
        log.info("Found installed agent: %s", name)
        yield name
