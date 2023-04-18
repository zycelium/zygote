# pylint: disable=missing-function-docstring, missing-module-docstring
# pylint: disable=redefined-outer-name, unused-argument
import pytest
from zycelium.zygote.models import Peer, start_database, stop_database


@pytest.fixture(scope="function", autouse=True)
async def database():
    await start_database("sqlite://:memory:")
    yield
    await stop_database()


async def test_peer_create():
    peer = await Peer.create(
        uuid="a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6",
        name="Test Peer",
        description="Test Peer Description",
        base_url="https://example.com",
        verify_tls_cert=True,
    )
    assert str(peer.uuid) == "a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6"
    assert peer.name == "Test Peer"
    assert peer.description == "Test Peer Description"
    assert peer.base_url == "https://example.com"
    assert peer.verify_tls_cert is True


async def test_peer_get():
    peer = await Peer.create(
        uuid="a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6",
        name="Test Peer",
        description="Test Peer Description",
        base_url="https://example.com",
        verify_tls_cert=True,
    )
    peer2 = await Peer.get(uuid="a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6")
    assert peer2.uuid == peer.uuid
    assert peer2.name == peer.name
    assert peer2.description == peer.description
    assert peer2.base_url == peer.base_url
    assert peer2.verify_tls_cert == peer.verify_tls_cert