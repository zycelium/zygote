"""Test API."""


async def test_create_space(api):
    """Test create space."""
    space = await api.create_space("test")
    assert space["name"] == "test"


async def test_create_space_not_unique_fail(api):
    """Test create space fail."""
    space = await api.create_space("test")
    assert space["name"] == "test"
    space = await api.create_space("test")
    assert space["success"] is False


async def test_get_space(api):
    """Test get space."""
    space = await api.create_space("test")
    space = await api.get_space(space["uuid"])
    assert space["name"] == "test"


async def test_update_space(api):
    """Test update space."""
    space = await api.create_space("test")
    space = await api.update_space(space["uuid"], name="test2")
    assert space["name"] == "test2"


async def test_get_spaces(api):
    """Test get spaces."""
    await api.create_space("test")
    await api.create_space("test2")
    spaces = await api.get_spaces()
    assert len(spaces["spaces"]) == 2


async def test_create_agent(api):
    """Test create agent."""
    agent = await api.create_agent("test")
    assert agent["name"] == "test"


async def test_create_agent_not_unique_fail(api):
    """Test create agent fail."""
    agent = await api.create_agent("test")
    assert agent["name"] == "test"
    agent = await api.create_agent("test")
    assert agent["success"] is False


async def test_get_agent(api):
    """Test get agent."""
    agent = await api.create_agent("test")
    agent = await api.get_agent(agent["uuid"])
    assert agent["name"] == "test"


async def test_update_agent(api):
    """Test update agent."""
    agent = await api.create_agent("test")
    agent = await api.update_agent(agent["uuid"], name="test2")
    assert agent["name"] == "test2"


async def test_get_agents(api):
    """Test get agents."""
    await api.create_agent("test")
    await api.create_agent("test2")
    agents = await api.get_agents()
    assert len(agents["agents"]) == 2


async def test_delete_agent(api):
    """Test delete agent."""
    agent = await api.create_agent("test")
    agent = await api.delete_agent(agent["uuid"])
    assert agent["success"] is True


async def test_join_space(api):
    """Test join space."""
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    await api.join_space(space["uuid"], agent["uuid"])
    agent_joined = await api.get_agent(agent["uuid"])
    assert agent_joined["spaces"][0]["uuid"] == space["uuid"]


async def test_leave_space(api):
    """Test leave space."""
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    await api.join_space(space["uuid"], agent["uuid"])
    await api.leave_space(space["uuid"], agent["uuid"])
    agent_joined = await api.get_agent(agent["uuid"])
    assert space["uuid"] not in agent_joined["spaces"]


async def test_get_joined_spaces(api):
    """Test get joined spaces."""
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    await api.join_space(space["uuid"], agent["uuid"])
    spaces = await api.get_joined_spaces(agent["uuid"])
    assert len(spaces["spaces"]) == 1
    assert spaces["spaces"][0]["uuid"] == space["uuid"]


async def test_get_unjoined_spaces(api):
    """Test get unjoined spaces."""
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    await api.join_space(space["uuid"], agent["uuid"])
    spaces = await api.get_unjoined_spaces(agent["uuid"])
    assert len(spaces["spaces"]) == 0


async def test_get_joined_agents(api):
    """Test get joined agents."""
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    await api.join_space(space["uuid"], agent["uuid"])
    agents = await api.get_joined_agents(space["uuid"])
    assert len(agents["agents"]) == 1
    assert agents["agents"][0]["uuid"] == agent["uuid"]


async def test_get_unjoined_agents(api):
    """Test get unjoined agents."""
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    await api.join_space(space["uuid"], agent["uuid"])
    agents = await api.get_unjoined_agents(space["uuid"])
    assert len(agents["agents"]) == 0


async def test_create_frame(api):
    """Test create frame."""
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    frame = await api.create_frame(
        kind="event", name="test", agent_uuid=agent["uuid"], space_uuids=[space["uuid"]]
    )
    assert frame["name"] == "test"


async def test_get_frame(api):
    """Test get frame."""
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    frame = await api.create_frame(
        kind="event", name="test", agent_uuid=agent["uuid"], space_uuids=[space["uuid"]]
    )
    frame = await api.get_frame(frame["uuid"])
    assert frame["name"] == "test"
    assert frame["spaces"][0]["uuid"] == space["uuid"]
    assert frame["agent"]["uuid"] == agent["uuid"]


async def test_get_frames_for_agent(api):
    """Test get frames for agent."""
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    frame = await api.create_frame(
        kind="event", name="test", agent_uuid=agent["uuid"], space_uuids=[space["uuid"]]
    )
    frames = await api.get_frames_for_agent(agent["uuid"])
    assert len(frames["frames"]) == 1
    assert frames["frames"][0]["uuid"] == frame["uuid"]


async def test_get_frames_for_space(api):
    """Test get frames for space."""
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    frame = await api.create_frame(
        kind="event", name="test", agent_uuid=agent["uuid"], space_uuids=[space["uuid"]]
    )
    frames = await api.get_frames_for_space(space["uuid"])
    assert len(frames["frames"]) == 1
    assert frames["frames"][0]["uuid"] == frame["uuid"]


async def test_delete_frame(api):
    """Test delete frame."""
    space = await api.create_space("test")
    agent = await api.create_agent("test")
    frame = await api.create_frame(
        kind="event", name="test", agent_uuid=agent["uuid"], space_uuids=[space["uuid"]]
    )
    await api.delete_frame(frame["uuid"])
    frames = await api.get_frames_for_agent(agent["uuid"])
    assert len(frames["frames"]) == 0
