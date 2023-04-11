"""Test API."""
import pytest

from zycelium.zygote.api import ZygoteAPI


async def test_create_space():
    """Test create space."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    assert space["name"] == "test"
    await api.stop()


async def test_create_space_not_unique_fail():
    """Test create space fail."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    assert space["name"] == "test"
    space = await api.create_space("test")
    assert space["success"] is False
    await api.stop()


async def test_get_space():
    """Test get space."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    space = await api.get_space(space["uuid"])
    assert space["name"] == "test"
    await api.stop()


async def test_update_space():
    """Test update space."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    space = await api.update_space(space["uuid"], name="test2")
    assert space["name"] == "test2"
    await api.stop()


async def test_get_spaces():
    """Test get spaces."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    await api.create_space("test")
    await api.create_space("test2")
    spaces = await api.get_spaces()
    assert len(spaces["spaces"]) == 2
    await api.stop()


async def test_create_agent():
    """Test create agent."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    agent = await api.create_agent("test")
    assert agent["name"] == "test"
    await api.stop()


async def test_create_agent_not_unique_fail():
    """Test create agent fail."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    agent = await api.create_agent("test")
    assert agent["name"] == "test"
    agent = await api.create_agent("test")
    assert agent["success"] is False
    await api.stop()


async def test_get_agent():
    """Test get agent."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    agent = await api.create_agent("test")
    agent = await api.get_agent(agent["uuid"])
    assert agent["name"] == "test"
    await api.stop()


async def test_update_agent():
    """Test update agent."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    agent = await api.create_agent("test")
    agent = await api.update_agent(agent["uuid"], name="test2")
    assert agent["name"] == "test2"
    await api.stop()


async def test_get_agents():
    """Test get agents."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    await api.create_agent("test")
    await api.create_agent("test2")
    agents = await api.get_agents()
    assert len(agents["agents"]) == 2
    await api.stop()


async def test_delete_agent():
    """Test delete agent."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    agent = await api.create_agent("test")
    agent = await api.delete_agent(agent["uuid"])
    assert agent["success"] is True
    await api.stop()
