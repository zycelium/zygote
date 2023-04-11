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
    assert len(spaces) == 2
    await api.stop()
