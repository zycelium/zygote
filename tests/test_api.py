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


async def test_join_space():
    """Test join space."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    await api.join_space(space["uuid"], agent["uuid"])
    agent_joined = await api.get_agent(agent["uuid"])
    assert space["uuid"] in agent_joined["spaces"]
    await api.stop()


async def test_leave_space():
    """Test leave space."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    await api.join_space(space["uuid"], agent["uuid"])
    await api.leave_space(space["uuid"], agent["uuid"])
    agent_joined = await api.get_agent(agent["uuid"])
    assert space["uuid"] not in agent_joined["spaces"]
    await api.stop()


async def test_get_joined_spaces():
    """Test get joined spaces."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    await api.join_space(space["uuid"], agent["uuid"])
    spaces = await api.get_joined_spaces(agent["uuid"])
    assert len(spaces["spaces"]) == 1
    assert spaces["spaces"][0]["uuid"] == space["uuid"]
    await api.stop()


async def test_get_unjoined_spaces():
    """Test get unjoined spaces."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    await api.join_space(space["uuid"], agent["uuid"])
    spaces = await api.get_unjoined_spaces(agent["uuid"])
    assert len(spaces["spaces"]) == 0
    await api.stop()


async def test_get_joined_agents():
    """Test get joined agents."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    await api.join_space(space["uuid"], agent["uuid"])
    agents = await api.get_joined_agents(space["uuid"])
    assert len(agents["agents"]) == 1
    assert agents["agents"][0]["uuid"] == agent["uuid"]
    await api.stop()


async def test_get_unjoined_agents():
    """Test get unjoined agents."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    await api.join_space(space["uuid"], agent["uuid"])
    agents = await api.get_unjoined_agents(space["uuid"])
    assert len(agents["agents"]) == 0
    await api.stop()


async def test_create_frame():
    """Test create frame."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    frame = await api.create_frame(
        kind="event", name="test", agent_uuid=agent["uuid"], space_uuids=[space["uuid"]]
    )
    assert frame["name"] == "test"
    await api.stop()


async def test_get_frame():
    """Test get frame."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    frame = await api.create_frame(
        kind="event", name="test", agent_uuid=agent["uuid"], space_uuids=[space["uuid"]]
    )
    frame = await api.get_frame(frame["uuid"])
    assert frame["name"] == "test"
    assert frame["spaces"][0]["uuid"] == space["uuid"]
    assert frame["agent"]["uuid"] == agent["uuid"]
    await api.stop()


async def test_get_frames_for_agent():
    """Test get frames for agent."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    frame = await api.create_frame(
        kind="event", name="test", agent_uuid=agent["uuid"], space_uuids=[space["uuid"]]
    )
    frames = await api.get_frames_for_agent(agent["uuid"])
    assert len(frames["frames"]) == 1
    assert frames["frames"][0]["uuid"] == frame["uuid"]
    await api.stop()


async def test_get_frames_for_space():
    """Test get frames for space."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    frame = await api.create_frame(
        kind="event", name="test", agent_uuid=agent["uuid"], space_uuids=[space["uuid"]]
    )
    frames = await api.get_frames_for_space(space["uuid"])
    assert len(frames["frames"]) == 1
    assert frames["frames"][0]["uuid"] == frame["uuid"]
    await api.stop()


async def test_delete_frame():
    """Test delete frame."""
    api = ZygoteAPI()
    await api.start("sqlite://:memory:")
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    frame = await api.create_frame(
        kind="event", name="test", agent_uuid=agent["uuid"], space_uuids=[space["uuid"]]
    )
    await api.delete_frame(frame["uuid"])
    frames = await api.get_frames_for_agent(agent["uuid"])
    assert len(frames["frames"]) == 0
    await api.stop()
