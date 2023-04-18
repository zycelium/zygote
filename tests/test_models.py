# pylint: disable=missing-function-docstring, missing-module-docstring
# pylint: disable=redefined-outer-name, unused-argument
import pytest
from zycelium.zygote.models import Instance, start_database, stop_database


@pytest.fixture(scope="function", autouse=True)
async def database():
    await start_database("sqlite://:memory:")
    yield
    await stop_database()


async def test_instance_create_me(database):
    own_instance = await Instance.create_me("test-name", "test-description")
    assert own_instance.name == "test-name"
    assert own_instance.description == "test-description"
    assert own_instance.me is True
    assert own_instance.verify_tls_cert is True


async def test_instance_get_me(database):
    await Instance.create_me("test-name", "test-description", verify_tls_cert=False)
    own_instance = await Instance.get_me()
    assert own_instance.name == "test-name"
    assert own_instance.description == "test-description"
    assert own_instance.me is True
    assert own_instance.verify_tls_cert is False


async def test_instance_create_peer(database):
    await Instance.create_me("test-name", "test-description")
    peer_instance = await Instance.create_peer(
        "00000000-0000-0000-0000-000000000000",
        "peer-name",
        "peer-description",
        base_url="https://example.com",
        verify_tls_cert=False,
    )
    assert str(peer_instance.uuid) == "00000000-0000-0000-0000-000000000000"
    assert peer_instance.name == "peer-name"
    assert peer_instance.description == "peer-description"
    assert peer_instance.me is False
    assert peer_instance.base_url == "https://example.com"
    assert peer_instance.verify_tls_cert is False


async def test_instance_get_peer(database):
    await Instance.create_me("test-name", "test-description")
    await Instance.create_peer(
        "00000000-0000-0000-0000-000000000000", "peer-name", "peer-description"
    )
    peer_instance = await Instance.get_peer_by_uuid(
        uuid="00000000-0000-0000-0000-000000000000"
    )
    assert str(peer_instance.uuid) == "00000000-0000-0000-0000-000000000000"
    assert peer_instance.name == "peer-name"
    assert peer_instance.description == "peer-description"
    assert peer_instance.me is False

    peer_instance = await Instance.get_peer_by_name(name="peer-name")
    assert str(peer_instance.uuid) == "00000000-0000-0000-0000-000000000000"
    assert peer_instance.name == "peer-name"
    assert peer_instance.description == "peer-description"
    assert peer_instance.me is False


async def test_instance_get_peers(database):
    await Instance.create_me("test-name", "test-description")
    await Instance.create_peer(
        "00000000-0000-0000-0000-000000000000", "peer-name", "peer-description"
    )
    await Instance.create_peer(
        "00000000-0000-0000-0000-000000000001", "peer-name-2", "peer-description-2"
    )
    peer_instances = await Instance.get_peers()
    assert len(peer_instances) == 2
    assert str(peer_instances[0].uuid) == "00000000-0000-0000-0000-000000000000"
    assert peer_instances[0].name == "peer-name"
    assert peer_instances[0].description == "peer-description"
    assert peer_instances[0].me is False
    assert str(peer_instances[1].uuid) == "00000000-0000-0000-0000-000000000001"
    assert peer_instances[1].name == "peer-name-2"
    assert peer_instances[1].description == "peer-description-2"
    assert peer_instances[1].me is False
