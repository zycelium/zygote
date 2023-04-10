"""Test API."""
import pytest
from tortoise import Tortoise

from zycelium.zygote.models import init_db
from zycelium.zygote.server import app as zygote_app


@pytest.fixture(scope="function", autouse=True)
async def app():
    """Quart app"""
    await init_db("sqlite://:memory:")
    yield zygote_app
    await Tortoise.close_connections()


async def test_frame_post(app):  # pylint: disable=redefined-outer-name
    """Test frame post."""
    client = app.test_client()
    data = {"kind": "event", "name": "test", "data": {"foo": "bar"}}
    response = await client.post("/api/v1/frames", json=data)
    assert response.status_code == 200
    json = await response.json
    assert json["kind"] == "event"
    assert json["name"] == "test"
    assert json["data"] == {"foo": "bar"}
    assert json["meta"] == {}
    assert json["time"] is not None
