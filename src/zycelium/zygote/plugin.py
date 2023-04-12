"""
Plug-in agents discovery.
"""
import asyncio
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


def start_agent(agent_name: str, url: str, auth: dict) -> None:
    """Start an agent."""
    log.info("Starting agent %s", agent_name)
    agent_module = importlib.import_module(agent_name)
    try:
        log.info("Starting agent %s", agent_name)
        asyncio.run(agent_module.agent.run(url=url, auth=auth))
    except Exception as exc:  # pylint: disable=broad-except
        log.exception(exc)
    log.info("Started agent %s", agent_name)